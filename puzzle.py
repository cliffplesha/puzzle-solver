
import copy
import random
import itertools
from typing_extensions import Literal

import numpy as np
import networkx as nx

PIECE_TYPE = Literal['edge', 'middle', 'corner']
SUB_AREA = Literal['top_left', 'top_right', 'bottom_left', 'bottom_right']

class Piece:
    """
    class for pieces
    """
    def __init__(
        self,
        piece_type: PIECE_TYPE,
        node_location: tuple,
        unconnected_edges: int,
        area: SUB_AREA | None = None
    ):
        self.piece_type = piece_type
        self.area = area
        self.node_location = node_location
        self.connected_edges = 0
        self.unconnected_edges = unconnected_edges
    


class Puzzle:
    def __init__(
        self,
        m: int = 25,
        n: int = 40,
    ):
        self.rows = m
        self.columns = n
        self.solution_time = 0
        self.all_puzzle_pieces:np.ndarray[Piece] = np.array([])
        self.unconnected_pieces = np.array([])
        self.fully_connected_pieces = np.array([])
        self.partially_connected_pieces = np.array([])
        self.piece_test_pool = np.array([])
        
    def create_puzzle(self):
        full_puzzle = np.array([])
        self.solution_time = 0
        G:nx.graph.Graph = nx.grid_2d_graph(self.rows,self.columns)
        self.puzzle_structure = G
        for node in G.nodes:
            if node[1]<20 and node[0]<13:
                area='top_left'
            elif node[1]>= 20 and node[0]<13:
                area = 'top_right'
            elif node[1]< 20 and node[0]>=13:
                area = 'bottom_left'
            elif node[1]>= 20 and node[0]>=13:
                area = 'bottom_right'

            match G.degree(node):
                case 2:
                    piece = Piece(
                        piece_type='corner',
                        node_location=node,
                        unconnected_edges=2,
                        area=area
                    )
                case 3:
                    piece = Piece(
                        piece_type='edge',
                        node_location=node,
                        unconnected_edges=3,
                        area=area
                    )
                case 4:
                   piece = Piece(
                        piece_type='middle',
                        node_location=node,
                        unconnected_edges=4,
                        area=area
                    )
            full_puzzle = np.append(full_puzzle, piece)
        self.all_puzzle_pieces = full_puzzle
        self.unconnected_pieces = np.array([])
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

    def test_for_connection(
        self,
        piece_a:Piece,
        piece_b:Piece
    ) -> bool:
        
        if piece_b.node_location in list(self.puzzle_structure.adj[piece_a.node_location]):
            try:
                self.solution_time += random.randint(1,int(piece_a.unconnected_edges*piece_b.unconnected_edges/2))
            except ValueError:
                # an unconnected edge is 0
                self.solution_time += 1
            piece_a.unconnected_edges -= 1
            piece_b.unconnected_edges -= 1
            piece_a.connected_edges += 1
            piece_b.connected_edges += 1
            return True
        else:
            self.solution_time += piece_a.unconnected_edges*piece_b.unconnected_edges/2
            return False


    def sort_back_of_puzzle(
        self
    )->list[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Method to simulated sorting all pieces
        Returns arrays of sorted pieces
        """
        top_left_pieces = np.array([])
        top_right_pieces = np.array([])
        bottom_left_pieces = np.array([])
        bottom_right_pieces = np.array([])

        for piece in self.all_puzzle_pieces:
            piece: Piece
            self.solution_time += 4 #estimated time to sort an individual piece
            match piece.area:
                case 'top_left':
                    top_left_pieces = np.append(top_left_pieces,piece)
                case 'top_right':
                    top_right_pieces = np.append(top_right_pieces,piece)
                case 'bottom_left':
                    bottom_left_pieces = np.append(bottom_left_pieces,piece)
                case 'bottom_right':
                    bottom_right_pieces = np.append(bottom_right_pieces,piece)
        return top_left_pieces, top_right_pieces, bottom_left_pieces, bottom_right_pieces
                    
    def sort_shape_of_puzzle(
        self
    )->list[np.ndarray, np.ndarray, np.ndarray]:
        """
        Sorts the puzzle into edge, middle, and corner pieces

        Returns:
            list[middle_pieces, edge_pieces, corner_pieces]
        """
        edge_pieces = np.array([])
        middle_pieces = np.array([])
        corner_pieces = np.array([])
        for piece in self.all_puzzle_pieces:
            piece: Piece
            self.solution_time += 4
            match piece.piece_type:
                case "middle":
                    middle_pieces = np.append(middle_pieces, piece)
                case "edge":
                    edge_pieces = np.append(edge_pieces, piece)
                case "corner":
                    corner_pieces = np.append(corner_pieces, piece)
        
        return middle_pieces, edge_pieces, corner_pieces
        

    def random_solve(
        self,
        piece_pool:np.ndarray[Piece] | None = None
    ) -> float:
        if piece_pool is None:
            self.create_puzzle()
            self.unconnected_pieces = self.all_puzzle_pieces
        else:
            self.unconnected_pieces = copy.deepcopy(piece_pool)
        
        while self.unconnected_pieces.size > 2:
            piece_a = self.pickup_random_piece()
            self.unconnected_pieces = np.delete(self.unconnected_pieces, np.where(self.unconnected_pieces == piece_a)[0]) #remove grabbed piece from pool
            self.piece_test_pool = copy.deepcopy(self.unconnected_pieces) # create pool of pieces to test piece_a against
            while piece_a.unconnected_edges > 0: #while that piece is not fully connected
                try:
                    piece_b:Piece = self.pickup_random_piece(piece_pool=self.piece_test_pool) #grab new random piece from pool
                except ValueError:
                    # no further pieces to test. Must be edge for not full puzzle
                    if piece_a not in self.partially_connected_pieces:
                        self.partially_connected_pieces = np.append(self.partially_connected_pieces, piece_a)
                    break
                connection_result = self.test_for_connection(piece_a=piece_a, piece_b=piece_b)
                self.piece_test_pool = np.delete(self.piece_test_pool, np.where(self.piece_test_pool == piece_b)[0]) 
                if connection_result:
                    self.unconnected_pieces = np.delete(
                            self.unconnected_pieces, 
                            np.where(self.unconnected_pieces == piece_b)[0]
                         )
                    if piece_b.unconnected_edges==0:
                        self.fully_connected_pieces = np.append(self.fully_connected_pieces, piece_b)
                    else:
                        if piece_b not in self.partially_connected_pieces:
                            self.partially_connected_pieces = np.append(self.partially_connected_pieces, piece_b)                 
            self.unconnected_pieces = np.delete(self.unconnected_pieces, np.where(self.unconnected_pieces == piece_a)[0])
            if piece_a.unconnected_edges == 0:
                if piece_a in self.partially_connected_pieces:
                    self.partially_connected_pieces = np.delete(self.partially_connected_pieces, np.where(self.partially_connected_pieces == piece_a)[0])
                self.fully_connected_pieces = np.append(self.fully_connected_pieces, piece_a)

        #all but one piece is left. Connect and finish puzzle
        return self.solution_time
        
    def solve_edges(
        self,
        edge_pieces: np.ndarray[Piece],
        corner_pieces: np.ndarray[Piece]
    ):
        piece_pool = np.concat([edge_pieces, corner_pieces])
        self.random_solve(piece_pool=piece_pool)
            
        
    #     return 0

    # def edge_in_solve(
    #     self,
    # ):
    #     [edge_pieces, middle_pieces, corner_pieces] = self.sort_puzzle()

    #     # sort puzzle into edge, middle, and corner pieces

    #     # starting with a corner, complete the edges

    #     # get random middle piece, and see if connects to any of the edge pieces or partially connected pieces
        

    #     return 0


        