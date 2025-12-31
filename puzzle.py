
import copy
import random
from typing_extensions import Literal

import numpy as np

PIECE_TYPE = Literal['edge', 'middle', 'corner']
SUB_AREA = Literal['top_left', 'top_right', 'bottom_left', 'bottom_right']

class Piece:
    """
    class for pieces
    """
    def __init__(
        self,
        piece_type: PIECE_TYPE,
        connection_pts: int,
        unconnected_edges: int,
        connection_map: dict(str, int) | None = None,
        corner_connections: int | None = None,
        middle_connections: int | None = None,
        edge_connections: int | None = None,
        connected_edges: int = 0,
        area: SUB_AREA | None = None
    ):
        self.piece_type = piece_type
        if connection_map is None:
            self.connection_map = {}
        else: self.connection_map = connection_map
        self.connection_map['connection_pts'] = connection_pts
        self.connection_map['unconnected_edges'] = unconnected_edges
        self.connection_map['connected_edges'] = connected_edges
        self.connection_map['corner_connections'] = corner_connections
        self.connection_map['middle_connections'] = middle_connections
        self.connection_map['edge_connections'] = edge_connections
        self.area = area
    
    def test_connection(
        self,
        test_piece: Piece,
        puzzle: Puzzle
    ) -> bool:
        """
        test if puzzle pieces fit together
        returns true if pieces fit and decrements available slots for pieces.
        """
        # check if pieces can fit
        connection_types_remaining = test_piece.connection_map[test_piece.piece_type +'_connections']
            
        if connection_types_remaining == 0:
            # no available connection slots for piece remaining
            return False
        piece_a_unconnected_edges = self.connection_map['unconnected_edges']
        piece_b_unconnected_edges = test_piece.connection_map['unconnected_edges']
        connection_prob = min(piece_a_unconnected_edges, piece_b_unconnected_edges)/(puzzle.piece_test_pool.size)
        if piece_a_unconnected_edges < piece_b_unconnected_edges: 
            puzzle.solution_time += random.randint(piece_a_unconnected_edges, piece_b_unconnected_edges)
        else:
            puzzle.solution_time += random.randint(piece_b_unconnected_edges, piece_a_unconnected_edges)
        if random.random() <= connection_prob:
            self.connection_map['connected_edges'] +=1
            self.connection_map['unconnected_edges'] -= 1
            test_piece.connection_map['connected_edges'] += 1
            test_piece.connection_map['unconnected_edges'] -= 1
            self.connection_map[test_piece.piece_type+'_connections'] -= 1
            test_piece.connection_map[self.piece_type+'_connections'] -= 1
            return True
        else:
            return False
    
        

class EdgePiece(Piece):
    """
    class for edge pieces
    """
    def __init__(
        self,
        edge_connections: int,
        middle_connections: int,
        corner_connections: int
    ):
        self.connection_map:{str,int}
        super().__init__(
            piece_type='edge',
            connection_pts=3,
            unconnected_edges=3,
            edge_connections=edge_connections,
            middle_connections=middle_connections,
            corner_connections=corner_connections,
            connection_map={}
            )



class MiddlePiece(Piece):
    """
    class for middle pieces
    """
    def __init__(
        self,
        edge_connections: int,
        middle_connections: int,
        corner_connections: int = 0
    ):
        self.connection_map:{str,int}
        super().__init__(
            piece_type='middle', 
            connection_pts=4, 
            unconnected_edges=4,
            edge_connections=edge_connections,
            middle_connections=middle_connections,
            corner_connections=corner_connections,
            connection_map={}
            )

class CornerPiece(Piece):
    def __init__(
        self,
        edge_connections: int,
        middle_connections: int,
        corner_connections: int
    ):
        self.connection_map:{str,int}
        super().__init__(
            piece_type='corner', 
            connection_pts=2, 
            unconnected_edges=2,
            edge_connections=edge_connections,
            middle_connections=middle_connections,
            corner_connections=corner_connections
            )

class Puzzle:
    def __init__(
        self,
        length: int = 40,
        height: int = 25,
        corner_piece_count:int = 4,
    ):
        self.length = length
        self.height = height
        self.total_piece_count = length * height
        self.edge_pieces_count = (length-2)*2 + (height-2)*2
        self.corner_piece_count = corner_piece_count
        self.middle_pieces_count = self.total_piece_count - self.edge_pieces_count - self.corner_piece_count
        self.solution_time = 0
        self.all_puzzle_pieces = np.array([])
        self.unconnected_pieces = np.array([])
        self.fully_connected_pieces = np.array([])
        self.partially_connected_pieces = np.array([])
        self.piece_test_pool = np.array([])
        
    def create_puzzle(self):
        full_puzzle = np.array([])
        # create corner piece. Can only connect to edge pieces
        for i in range(self.corner_piece_count):
            full_puzzle = np.append(
                full_puzzle, 
                CornerPiece(edge_connections=2, middle_connections=0, corner_connections=0)
            )
        # create edge pieces
        # edge pieces not connected to corner pieces
        for i in range(self.edge_pieces_count-self.corner_piece_count*2):
            full_puzzle = np.append(
                full_puzzle, 
                EdgePiece(
                    edge_connections=2,
                    middle_connections=1,
                    corner_connections=0
                    )
                )
        # edge pieces connected to corner pieces
        for i in range(self.corner_piece_count*2):
            full_puzzle = np.append(
                full_puzzle, 
                EdgePiece(
                    edge_connections=1,
                    middle_connections=1,
                    corner_connections=1
                    )
                )
        # create middle pieces
        # middle pieces that connect to edge pieces
        for i in range(self.edge_pieces_count):
            full_puzzle = np.append(
                full_puzzle, 
                MiddlePiece(
                    corner_connections=0,
                    edge_connections=1,
                    middle_connections=3
                )
            )
        # middle pieces that only connect to middle pieces
        for i in range (self.middle_pieces_count-self.edge_pieces_count):
            full_puzzle = np.append(
                full_puzzle,
                MiddlePiece(
                    edge_connections=0,
                    corner_connections=0,
                    middle_connections=4
                )
            )

        self.all_puzzle_pieces = full_puzzle
        self.unconnected_pieces = copy.deepcopy(full_puzzle)
        self.fully_connected_pieces = np.array([])
        self.partially_connected_pieces = np.array([])
    
    def pickup_random_piece(
        self,
        piece_pool: np.array | None = None
    ) -> Piece:
        if piece_pool is None:
            if self.partially_connected_pieces is not None:
                piece_pool = np.concat([self.unconnected_pieces, self.partially_connected_pieces])
            else:
                piece_pool = self.unconnected_pieces
        piece_a = np.random.choice(piece_pool)
        self.solution_time += 2
        return piece_a

    def random_solve(
        self,
    ) -> float:
        self.create_puzzle()
        while self.unconnected_pieces.size > 2:
            piece_a = self.pickup_random_piece()
            self.unconnected_pieces = np.delete(self.unconnected_pieces, np.where(self.unconnected_pieces == piece_a)[0]) #remove grabbed piece from pool
            self.piece_test_pool = copy.deepcopy(self.unconnected_pieces) # create pool of pieces to test piece_a against
            while piece_a.connection_map['unconnected_edges'] > 0: #while that piece is not fully connected 
                try:
                    piece_b:Piece = self.pickup_random_piece(piece_pool=self.piece_test_pool) #grab new random piece from pool
                    connection_result = piece_a.test_connection(piece_b, self) #test if pieces connect
                    self.piece_test_pool = np.delete(self.piece_test_pool, np.where(self.piece_test_pool == piece_b)[0]) 
                    if connection_result:
                        if piece_b.connection_map['unconnected_edges']==0:
                            self.fully_connected_pieces = np.append(self.fully_connected_pieces, piece_b)
                            self.unconnected_pieces = np.delete(
                                self.unconnected_pieces, 
                                np.where(self.unconnected_pieces == piece_b)[0]
                            )
                except ZeroDivisionError, ValueError:
                    self.solution_time += 1
                    break
            self.fully_connected_pieces = np.append(self.fully_connected_pieces, piece_a)
            self.unconnected_pieces = np.delete(self.unconnected_pieces, np.where(self.unconnected_pieces == piece_a)[0])
        #all but one piece is left. Connect and finish puzzle
        return self.solution_time
        

    def edge_in_solve(
        self,
    ):
        # sort puzzle into edge, middle, and corner pieces

        # starting with a corner, complete the edges

        # get random middle piece, and see if connects to any of the edge pieces or partially connected pieces
        

        return 0


        