
import copy
import random
from typing_extensions import Literal

import numpy as np

PIECE_TYPE = Literal['edge', 'middle', 'corner']
SUB_AREA = Literal['top_left', 'top_right', 'bottom_left', 'bottom_right']

class PieceType:
    """
    class for pieces
    """
    def __init__(
        self,
        piece_type: PIECE_TYPE,
        connection_pnts: int,
        unconnected_edges: int,
        corner_connections: int | None = None,
        middle_connections: int | None = None,
        edge_connections: int | None = None,
        connected_edges: int = 0,
        area: SUB_AREA | None = None
    ):
        self.piece_type = piece_type
        self.connection_pnts = connection_pnts
        self.unconnected_edges = unconnected_edges
        self.connected_edges = connected_edges
        self.corner_connections = corner_connections
        self.middle_connections = middle_connections
        self.edge_connections = edge_connections
        self.area = area
    
    def test_connection(
        self,
        test_piece,
        remaining_unconnected_pieces:int
    ):
        """
        test if puzzle pieces fit together
        returns true if pieces fit and decrements available slots for pieces.
        """
        # check if pieces can fit
        connection_types_remaining: int
        match test_piece.piece_type:
            case "edge":
                connection_types_remaining = self.edge_connections
            case "middle":
                connection_types_remaining = self.middle_connections
            case "corner":
                connection_types_remaining = self.corner_connections
            
        if connection_types_remaining == 0:
            # no available connection slots for piece remaining
            return False, test_piece

        connection_prob = min(self.unconnected_edges, test_piece.unconnected_edges)/remaining_unconnected_pieces
        if random.random() <= connection_prob:
            self.connected_edges +=1
            self.unconnected_edges -= 1
            test_piece.connected_edges += 1
            test_piece.unconnected_edges -= 1
            return True, test_piece
        else:
            return False, test_piece

class EdgePiece(PieceType):
    """
    class for edge pieces
    """
    def __init__(
        self,
        edge_connections: int,
        middle_connections: int,
        corner_connections: int
    ):
        self.edge_connections = edge_connections
        self.middle_connections = middle_connections
        self.corner_connections = corner_connections
        super().__init__(piece_type='edge', connection_pnts=3, unconnected_edges=3)



class MiddlePiece(PieceType):
    """
    class for middle pieces
    """
    def __init__(
        self,
        edge_connections: int,
        middle_connections: int,
        corner_connections: int = 0
    ):
        self.edge_connections = edge_connections
        self.middle_connections = middle_connections
        self.corner_connections = corner_connections
        super().__init__(piece_type='middle', connection_pnts=4, unconnected_edges=4)

class CornerPiece(PieceType):
    def __init__(
        self,
        edge_connections: int,
        middle_connections: int,
        corner_connections: int
    ):
        self.edge_connections = edge_connections
        self.middle_connections = middle_connections
        self.corner_connections = corner_connections
        super().__init__(piece_type='corner', connection_pnts=2, unconnected_edges=2)

class Puzzle:
    def __init__(
        self,
        length: int = 40,
        height: int = 25,
        corner_piece_count:int = 4,
        test_time: float = 2.0
    ):
        self.length = length
        self.height = height
        self.total_piece_count = length * height
        self.edge_pieces_count = (length-2)*2 + (height-2)*2
        self.corner_piece_count = corner_piece_count
        self.middle_pieces_count = self.total_piece_count - self.edge_pieces_count - self.corner_piece_count
        self.remaining_unconnectecd_pieces = self.total_piece_count
        self.test_time = test_time
    
    def create_puzzle(self):
        full_puzzle = np.array([])
        # create corner piece. Can only connect to edge pieces
        for i in range(self.corner_piece_count):
            full_puzzle = np.append(full_puzzle, CornerPiece(edge_connections=2, middle_connections=0, corner_connections=0))
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

        return full_puzzle
     
    def random_solve(
        self,
        full_puzzle
    ) -> float:
        time_to_solve = 0
        fully_connected_pieces = np.array([])
        unconnected_puzzle_pieces = copy.deepcopy(full_puzzle)
        while unconnected_puzzle_pieces.size > 2:
            piece_a = np.random.choice(unconnected_puzzle_pieces) #grab a random piece
            piece_pool = np.delete(unconnected_puzzle_pieces, np.where(unconnected_puzzle_pieces == piece_a)[0]) #remove grabbed piece from pool
            attempts = 0
            while piece_a.unconnected_edges > 0: #while that piece is not fully connected
                try:
                    piece_b = np.random.choice(piece_pool) #grab new random piece from pool
                    attempts+=1
                    connection, piece_b = piece_a.test_connection(piece_b, piece_pool.size) #test if pieces connect
                    piece_pool = np.delete(piece_pool, np.where(piece_pool == piece_b)[0]) 
                    if connection:
                        # print("piece connected")
#                       # print(f"piece_a has {piece_a.unconnected_edges} unconnceted edges")
#                       # print(f"piece_b has {piece_b.unconnected_edges} unconnected edges")
                        if piece_b.unconnected_edges==0:
                            fully_connected_pieces = np.append(fully_connected_pieces, piece_b)
                            unconnected_puzzle_pieces = np.delete(
                                unconnected_puzzle_pieces, 
                                np.where(unconnected_puzzle_pieces == piece_b)[0]
                            )
                        # print(f"took {i} random piece to fully connect piece a")
                    fully_connected_pieces = np.append(fully_connected_pieces, piece_a)
                    unconnected_puzzle_pieces = np.delete(unconnected_puzzle_pieces, np.where(unconnected_puzzle_pieces == piece_a)[0])
                    time_to_solve += attempts * self.test_time
                except:
                    # print("non logical solution")
                    time_to_solve += piece_pool.size*self.test_time
                    break
        #all but one piece is left. Connect and finish puzzle
        return time_to_solve+self.test_time
        

    def edge_in_solve(
        self,
        full_puzzle
    ):
        # sort puzzle into edge, middle, and corner pieces

        # starting with a corner, complete the edges

        # get random middle piece, and see if connects to any of the edge pieces or partially connected pieces
        

        return 0


        