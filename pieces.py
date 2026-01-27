import random
from const import SHAPES, GRID_WIDTH

# Piece class to represent Tetris pieces
class Piece:
                def __init__(self, shape_type, block_images):
                    self.shape_type = shape_type
                    self.shape = SHAPES[shape_type]
                    self.block_image = block_images[shape_type]
                    self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
                    self.y = 0



def get_random_piece(block_images):
    shape_type = random.choice(list(SHAPES.keys()))
    return Piece(shape_type, block_images)


def rotate_piece(piece, clockwise=True):
    old_shape = piece.shape

    if clockwise:
         # rotate 90 degrees clockwise: transpose then reverse each row
        new_shape = [list(row) for row in zip(*old_shape[::-1])]
    else:
        # rotate 90 degrees counter-clockwise: reverse each row then transpose
        new_shape = [list(row) for row in zip(*old_shape)][::-1]
    return new_shape