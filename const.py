# game fps and blocksize
FPS = 60
BLOCK = 32

# Grid and play area
GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_AREA_X = 224
PLAY_AREA_Y = 32

# line clear animation speed/length
FLASH_SPEED = 10
FLASH_LENGTH = 100

# scores
SCORE_SINGLE = 40
SCORE_DOUBLE = 100
SCORE_TRIPLE = 300
SCORE_TETRIS = 1200
LINES_PER_LEVEL = 10

# 2D arrays representing Tetris piece shapes
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}