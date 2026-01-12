import pygame
import sys
import os
import random

WIDTH, HEIGHT = 768, 704
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
pygame.init()

GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_AREA_X = 224
PLAY_AREA_Y = 32

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

COLORS = {
    'I': (0, 255, 255), # Cyan
    'O': (255, 255, 0), # Yellow
    'T': (128, 0, 128), # Purple
    'S': (0, 255, 0), # Green
    'Z': (255, 0, 0), # Red
    'J': (0, 0, 255), # Blue
    'L': (255, 165, 0) # Orange
}

# Load and scale block images
BLOCK = 32

block_colors = ['Blue', 'LightBlue', 'Green', 'Orange', 'Purple', 'Red', 'Yellow']
blocks = {}

for color in block_colors:
    img = pygame.image.load(os.path.join("Assets", "Single Blocks", f"{color}.png"))
    blocks[color.lower()] = pygame.transform.scale(img, (BLOCK, BLOCK))

BLOCK_IMAGES = {
    'I': blocks['lightblue'],
    'O': blocks['yellow'],
    'T': blocks['purple'],
    'S': blocks['green'],
    'Z': blocks['red'],
    'J': blocks['blue'],
    'L': blocks['orange']
}

# Piece class to represent Tetris pieces
class Piece:
                def __init__(self, shape_type):
                    self.shape_type = shape_type
                    self.shape = SHAPES[shape_type]
                    self.color = COLORS[shape_type]
                    self.block_image = BLOCK_IMAGES[shape_type]
                    self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
                    self.y = 0

FPS = 60

# Load board image
board_image = pygame.image.load(os.path.join("Assets", "Board", "board.png"))
game_board = pygame.transform.scale(board_image, (384, 704))

# Initialize the grid, a 2D array filled with zeros
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def get_random_piece():
    shape_type = random.choice(list(SHAPES.keys()))
    return Piece(shape_type)

def draw_grid():
     for row in range(GRID_HEIGHT):
          for col in range(GRID_WIDTH):
               if grid[row][col] != 0:
                    piece_type = grid[row][col]
                    x = PLAY_AREA_X + col * BLOCK
                    y = PLAY_AREA_Y + row * BLOCK
                    WIN.blit(BLOCK_IMAGES[piece_type], (x, y))

def draw_window(current_piece, grid):
            WIN.fill((0, 0, 0))  # Fill the window with black
            WIN.blit(game_board, (192, 0))  # Draw the game board

            draw_grid()  # Draw the locked pieces on the grid

            # Draw the current piece
            for row in range(len(current_piece.shape)):
                for col in range(len(current_piece.shape[row])):
                    if current_piece.shape[row][col] == 1:
                        x = PLAY_AREA_X + (current_piece.x + col) * BLOCK
                        y = PLAY_AREA_Y + (current_piece.y + row) * BLOCK
                        WIN.blit(current_piece.block_image, (x, y))

            
            pygame.display.update()  # Update the display  

# Check if the move is valid
def valid_move(piece, grid, dx=0, dy=0):
     # dx, dy are the changes we want to make (move left = dx=-1, etc) 
     for row in range(len(piece.shape)):
          for col in range(len(piece.shape[row])):
               if piece.shape[row][col] == 1:
                    new_x = piece.x + col + dx
                    new_y = piece.y + row + dy
                    if new_x < 0 or new_x >= GRID_WIDTH:
                         return False
                    if new_y >= GRID_HEIGHT:
                         return False
                    
                    if new_y >= 0 and grid[new_y][new_x] != 0:
                         return False
                    
     return True

def lock_piece(piece, grid):
     for row in range(len(piece.shape)):
        for col in range(len(piece.shape[row])):
             if piece.shape[row][col] == 1:
                  grid_x = piece.x + col
                  grid_y = piece.y + row
                  grid[grid_y][grid_x] = piece.shape_type

def main():

    fall_time = 0
    fall_speed = 500 # milliseconds

    dt = 0 # Delta time for DAS
    das_delay = 100
    das_repeat = 50
    das_timer = 0
    das_active = False
    last_key = None

    piece_queue = [get_random_piece() for _ in range(5)] # Pre-generate 5 pieces
    current_piece = piece_queue.pop(0) # Get the next piece
    piece_queue.append(get_random_piece()) # Add a new random piece to the queue
    print(f"Piece type: {current_piece.shape_type}")
    print(f"Position: ({current_piece.x}, {current_piece.y})")
    print(f"Shape: {current_piece.shape}")

    def rotate_piece(piece, clockwise=True):
         old_shape = piece.shape

         if clockwise:
              # rotate 90 degrees clockwise: transpose then reverse each row
              new_shape = [list(row) for row in zip(*old_shape[::-1])]
         else:
              # rotate 90 degrees counter-clockwise: reverse each row then transpose
              new_shape = [list(row) for row in zip(*old_shape)][::-1]
         return new_shape

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        fall_time += clock.get_rawtime()

        dt = clock.get_rawtime() # Delta time in milliseconds

        # Loop through the event queue
        for event in pygame.event.get():
            # Check for quit event
            if event.type == pygame.QUIT:
                run = False

            # Handle initial key press
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if valid_move(current_piece, grid, dx=-1):
                        current_piece.x -= 1
                        last_key = pygame.K_LEFT
                        das_timer = 0
                        das_active = False
                elif event.key == pygame.K_RIGHT:
                    if valid_move(current_piece, grid, dx=1):
                        current_piece.x += 1
                        last_key = pygame.K_RIGHT
                        das_timer = 0
                        das_active = False

                elif event.key == pygame.K_SPACE:
                     # Hard drop
                     while valid_move(current_piece, grid, dy=1):
                          current_piece.y += 1
                     lock_piece(current_piece, grid)
                     current_piece = piece_queue.pop(0)
                     piece_queue.append(get_random_piece())

                elif event.key == pygame.K_UP:
                     # Rotate piece clockwise
                     rotated_shape = rotate_piece(current_piece, clockwise=True)
                     old_shape = current_piece.shape
                     current_piece.shape = rotated_shape
                
                elif event.key == pygame.K_z:
                    # Rotate piece counter-clockwise
                    rotated_shape = rotate_piece(current_piece, clockwise=False)
                    old_shape = current_piece.shape
                    current_piece.shape = rotated_shape

                if not valid_move(current_piece, grid):
                    current_piece.shape = old_shape  # Revert if invalid
                    

        current_fall_speed = fall_speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            current_fall_speed = 50  # Faster fall speed when down key is held  

        if fall_time >= current_fall_speed:
            if valid_move(current_piece, grid, dy=1):
                current_piece.y += 1
            else:
                lock_piece(current_piece, grid)

                current_piece = piece_queue.pop(0)
                piece_queue.append(get_random_piece())
            fall_time = 0

        # Handle held keys DAS
        keys = pygame.key.get_pressed()
        if last_key in (pygame.K_LEFT, pygame.K_RIGHT):
            if keys[last_key]:
                das_timer += dt
                if not das_active and das_timer >= das_delay:
                    das_active = True
                    das_timer = 0
                if das_active and das_timer >= das_repeat:
                    if last_key == pygame.K_LEFT:
                        if valid_move(current_piece, grid, dx=-1):
                            current_piece.x -= 1
                    elif last_key == pygame.K_RIGHT:
                        if valid_move(current_piece, grid, dx=1):
                            current_piece.x += 1
                    das_timer = 0
            else:
                last_key = None
                das_active = False
                das_timer = 0
         
  

        draw_window(current_piece, grid)



    pygame.quit()

# Entry point of the program
if __name__ == "__main__":
    main()