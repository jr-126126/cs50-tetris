
FPS = 60
BLOCK = 32

GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_AREA_X = 224
PLAY_AREA_Y = 32

FLASH_SPEED = 10
FLASH_LENGTH = 100
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