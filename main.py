import pygame
import sys
import os
import random
import time
from grid import Grid
from pieces import Piece, get_random_piece, rotate_piece
from const import FPS, GRID_WIDTH, GRID_HEIGHT, BLOCK, PLAY_AREA_X, PLAY_AREA_Y

start = time.time()


pygame.display.init()
print("Pygame.display initialized")
print(f"Runtime: {time.time() - start} seconds")

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, allowedchanges=pygame.AUDIO_ALLOW_ANY_CHANGE)
pygame.mixer.init()
print("Pygame.mixer initialized")
print(f"Runtime: {time.time() - start} seconds")

# Encountered issue with joystick module not initializing with certain devices. Unplugging and replugging usb devices fixed it. (Pygame module issue, beyond me)
pygame.joystick.init()
print("Pygame.joystick initialized")
print(f"Runtime: {time.time() - start} seconds")

WIDTH, HEIGHT = 768, 704
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Tetris")


# scale block images

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


# Load board image
board_image = pygame.image.load(os.path.join("Assets", "Board", "board.png"))
game_board = pygame.transform.scale(board_image, (384, 704))




def draw_grid(grid):
     for row in range(GRID_HEIGHT):
          for col in range(GRID_WIDTH):
               if grid.get_cell(col, row) != 0:
                    piece_type = grid.get_cell(col, row)
                    x = PLAY_AREA_X + col * BLOCK
                    y = PLAY_AREA_Y + row * BLOCK
                    WIN.blit(BLOCK_IMAGES[piece_type], (x, y))

def draw_window(current_piece, grid):
            WIN.fill((0, 0, 0))  # Fill the window with black
            WIN.blit(game_board, (192, 0))  # Draw the game board

            draw_grid(grid)  # Draw the locked pieces on the grid

            # Draw the current piece
            for row in range(len(current_piece.shape)):
                for col in range(len(current_piece.shape[row])):
                    if current_piece.shape[row][col] == 1:
                        x = PLAY_AREA_X + (current_piece.x + col) * BLOCK
                        y = PLAY_AREA_Y + (current_piece.y + row) * BLOCK
                        WIN.blit(current_piece.block_image, (x, y))

            
            pygame.display.update()  # Update the display  


def try_rotation(piece, grid, rotated_shape):
        old_shape = piece.shape
        piece.shape = rotated_shape
        
        if grid.is_valid_move(piece):
             return True
        
        kick_offsets = [(-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]

        for dx, dy in kick_offsets:
             piece.x += dx
             piece.y += dy
             if grid.is_valid_move(piece):
                  return True
             
             piece.x -= dx
             piece.y -= dy

        piece.shape = old_shape
        return False




def main():

    # Initialize the grid, a 2D array filled with zeros
    grid = Grid(GRID_WIDTH, GRID_HEIGHT)

    fall_time = 0
    fall_speed = 500 # milliseconds

    dt = 0 # Delta time for DAS
    das_delay = 100
    das_repeat = 50
    das_timer = 0
    das_active = False
    last_key = None

    piece_queue = [get_random_piece(BLOCK_IMAGES) for _ in range(5)] # Pre-generate 5 pieces
    current_piece = piece_queue.pop(0) # Get the next piece
    piece_queue.append(get_random_piece(BLOCK_IMAGES)) # Add a new random piece to the queue



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
                    if grid.is_valid_move(current_piece, dx=-1):
                        current_piece.x -= 1
                        last_key = pygame.K_LEFT
                        das_timer = 0
                        das_active = False
                elif event.key == pygame.K_RIGHT:
                    if grid.is_valid_move(current_piece, dx=1):
                        current_piece.x += 1
                        last_key = pygame.K_RIGHT
                        das_timer = 0
                        das_active = False

                elif event.key == pygame.K_SPACE:
                     # Hard drop
                     while grid.is_valid_move(current_piece, dy=1):
                          current_piece.y += 1
                     grid.lock_piece(current_piece)
                     lines = grid.clear_lines()
                     current_piece = piece_queue.pop(0)
                     piece_queue.append(get_random_piece(BLOCK_IMAGES))

                elif event.key == pygame.K_UP:
                     # Rotate piece clockwise
                     rotated_shape = rotate_piece(current_piece, clockwise=True)
                     try_rotation(current_piece, grid, rotated_shape)
                
                elif event.key == pygame.K_z:
                    # Rotate piece counter-clockwise
                    rotated_shape = rotate_piece(current_piece, clockwise=False)
                    try_rotation(current_piece, grid, rotated_shape)

                    

        current_fall_speed = fall_speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            current_fall_speed = 50  # Faster fall speed when down key is held  

        if fall_time >= current_fall_speed:
            if grid.is_valid_move(current_piece, dy=1):
                current_piece.y += 1
            else:
                grid.lock_piece(current_piece)
                lines = grid.clear_lines()
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
                        if grid.is_valid_move(current_piece, dx=-1):
                            current_piece.x -= 1
                    elif last_key == pygame.K_RIGHT:
                        if grid.is_valid_move(current_piece, dx=1):
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