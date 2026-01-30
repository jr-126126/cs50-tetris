import pygame
import sys
import os
import random
import time
from grid import Grid
from pieces import Piece, get_random_piece, rotate_piece
from const import FPS, GRID_WIDTH, GRID_HEIGHT, BLOCK, PLAY_AREA_X, PLAY_AREA_Y, FLASH_SPEED, FLASH_LENGTH, LINES_PER_LEVEL, S_D_SPEED
from scoring import calculate_score

start = time.time()

# Pygame init + debugging
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

pygame.font.init()
print("Pygame.font initialized")
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

# Ghost block
ghost_block = pygame.image.load(os.path.join("Assets", "Ghost", "Single.png"))
ghost_block = pygame.transform.scale(ghost_block, (BLOCK, BLOCK))

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

# Load fonts for UI elements
font_large = pygame.font.Font(os.path.join("Assets", "Fonts", "Press_Start_2P", "PressStart2P-Regular.ttf"), 20) # Labels
font_small = pygame.font.Font(os.path.join("Assets", "Fonts", "Press_Start_2P", "PressStart2P-Regular.ttf"), 16) # Values


def draw_ui(score, level, total_lines, font_large, font_small):
    # UI positioning
    ui_x = 20
    ui_y = 450
    spacing = 80

    # Draw labels and values

    # Score
    score_label = font_large.render("SCORE", True, (255, 255, 255))
    score_value = font_small.render(str(score), True, (255, 200, 0))
    WIN.blit(score_label, (ui_x, ui_y))
    WIN.blit(score_value, (ui_x, ui_y + 40))

    # Level
    level_label = font_large.render("LEVEL", True, (255, 255, 255))
    level_value = font_small.render(str(level), True, (255, 200, 0))
    WIN.blit(level_label, (ui_x, ui_y + spacing))
    WIN.blit(level_value, (ui_x, ui_y + spacing + 40))

    # Lines
    lines_label = font_large.render("LINES", True, (255, 255, 255))
    lines_value = font_small.render(str(total_lines), True, (255, 200, 0))
    WIN.blit(lines_label, (ui_x, ui_y + spacing * 2))
    WIN.blit(lines_value, (ui_x, ui_y + spacing * 2 + 40))
    
def draw_held_piece(held_piece, font_large):
        # Draw hold label
        held_label = font_large.render("HELD", True, (255, 255, 255))
        WIN.blit(held_label, (20, 50))

        # draw held piece
        if held_piece:
            for row in range(len(held_piece.shape)):
                for col in range(len(held_piece.shape[row])):
                    if held_piece.shape[row][col] == 1:
                        x = 20 + col * BLOCK
                        y = 100 + row * BLOCK
                        WIN.blit(held_piece.block_image, (x, y))

def draw_piece_queue(piece_queue, font_large):
    # Draw "NEXT" label
    next_label = font_large.render("NEXT", True, (255, 255, 255))
    WIN.blit(next_label, (590, 50))
    
    # Draw next 5 pieces
    start_y = 100
    spacing = 80  # Space between each preview piece
    
    for i, piece in enumerate(piece_queue[:5]):  # Show first 5 pieces
        # Calculate position for this piece
        preview_x = 590
        preview_y = start_y + (i * spacing)
        
        # Draw the piece
        for row in range(len(piece.shape)):
            for col in range(len(piece.shape[row])):
                if piece.shape[row][col] == 1:
                    x = preview_x + col * BLOCK
                    y = preview_y + row * BLOCK
                    WIN.blit(piece.block_image, (x, y))

def draw_grid(grid, full_rows=None, flash_visible=True):  
     for row in range(GRID_HEIGHT):
          for col in range(GRID_WIDTH):
               if grid.get_cell(col, row) != 0:
                    piece_type = grid.get_cell(col, row)
                    x = PLAY_AREA_X + col * BLOCK
                    y = PLAY_AREA_Y + row * BLOCK



                    # If row full and animating draw ghost
                    if full_rows and row in full_rows and flash_visible:
                         WIN.blit(ghost_block, (x, y))
                    else:
                        piece_type = grid.get_cell(col, row)
                        WIN.blit(BLOCK_IMAGES[piece_type], (x, y))

def draw_window(current_piece, grid, full_rows, line_clear_delay,
                 flash_visible, score, level, total_lines, held_piece, piece_queue):
            WIN.fill((0, 0, 0))  # Fill the window with black
            WIN.blit(game_board, (192, 0))  # Draw the game board

            draw_grid(grid, full_rows if line_clear_delay > 0 else None, flash_visible)  # Draw the locked pieces on the grid

            # Draw the current piece
            for row in range(len(current_piece.shape)):
                for col in range(len(current_piece.shape[row])):
                    if current_piece.shape[row][col] == 1:
                        x = PLAY_AREA_X + (current_piece.x + col) * BLOCK
                        y = PLAY_AREA_Y + (current_piece.y + row) * BLOCK


                        piece_grid_y = current_piece.y + row
                        if full_rows and line_clear_delay > 0 and piece_grid_y in full_rows:
                             WIN.blit(ghost_block, (x, y))
                        else:
                            WIN.blit(current_piece.block_image,(x, y))

            draw_ui(score, level, total_lines, font_large, font_small)
            draw_held_piece(held_piece, font_large)
            draw_piece_queue(piece_queue, font_large)

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

    # DAS variables
    dt = 0 # Delta time for DAS
    das_delay = 100
    das_repeat = 50
    das_timer = 0
    das_active = False
    last_key = None

    # Line clear animation variables
    line_clear_delay = 0 # line clear animation timer
    full_rows = [] # store the rows that are full
    flash_visible = True
    flash_timer = 0

    # Score and level variables
    score = 0
    level = 0
    total_lines_cleared = 0

    # fall speed variables
    fall_time = 0
    base_fall_speed = 500 # milliseconds
    fall_speed = base_fall_speed

    held_piece = None
    can_swap = True

    piece_queue = [get_random_piece(BLOCK_IMAGES) for _ in range(5)] # Pre-generate 5 pieces
    current_piece = piece_queue.pop(0) # Get the next piece
    piece_queue.append(get_random_piece(BLOCK_IMAGES)) # Add a new random piece to the queue


    # Clock and main game loop
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

                     # Lock piece on hard drop     
                     grid.lock_piece(current_piece)
                     full_rows = grid.get_full_rows()
                     can_swap = True # Reset ability to hold when locking a piece
                     if full_rows:
                          line_clear_delay = FLASH_LENGTH # 
                     else:
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


                elif event.key == pygame.K_c: # Hotkey for 'hold'
                    if can_swap:
                        # If no held piece
                        if held_piece is None:
                            # Move current piece to held, get a new piece.
                            held_piece = current_piece
                            current_piece = piece_queue.pop(0)
                            piece_queue.append(get_random_piece(BLOCK_IMAGES))
                        # If held piece
                        else:
                            # Swap current with held
                            temp = current_piece
                            current_piece = held_piece
                            held_piece = temp

                            # reset pos
                            current_piece.x = GRID_WIDTH // 2 - len(current_piece.shape[0]) // 2
                            current_piece.y = 0

                        can_swap = False

                        
                            

                # REMOVE OR HIDE FROM USER - CHEATS (cheat code in future maybe?)    
               # elif event.key == pygame.K_q:
                #    # DEBUG: Fill bottom 4 rows for testing
                #    for row in range(GRID_HEIGHT - 4, GRID_HEIGHT):
                #        for col in range(GRID_WIDTH):
                #            if grid.get_cell(col, row) == 0:  # Only fill empty cells
                #                grid.grid[row][col] = 'T'  # Fill with T piece type

                    

        current_fall_speed = fall_speed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            current_fall_speed = S_D_SPEED  # Faster fall speed when down key is held  
        if line_clear_delay <= 0:
            if fall_time >= current_fall_speed:
                if grid.is_valid_move(current_piece, dy=1):
                    current_piece.y += 1
                else:
                    # Lock piece on soft drop
                    grid.lock_piece(current_piece)
                    full_rows = grid.get_full_rows()
                    can_swap = True # Reset ability to hold when locking a piece
                    if full_rows:
                        line_clear_delay = 300
                    else:
                        current_piece = piece_queue.pop(0) # Spawn new piece
                        piece_queue.append(get_random_piece(BLOCK_IMAGES))
                    
                    # If new piece spawns in occupied grid spaces - game over
                    if not grid.is_valid_move(current_piece):
                        print("GAME OVER!")
                        run = False
                    

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
         
         # Start animation timer
        if line_clear_delay > 0:
             line_clear_delay -= dt # count down
             flash_timer += dt

            
             if flash_timer >= FLASH_SPEED:
                  flash_visible = not flash_visible
                  flash_timer = 0
                  

             if line_clear_delay <= 0:
                  if full_rows:
                        lines = grid.clear_rows(full_rows)

                        score += calculate_score(lines, level)
                        total_lines_cleared += lines

                        level = total_lines_cleared // LINES_PER_LEVEL
                        fall_speed = base_fall_speed - (level * 50) # Increase fall speed based on level
                        fall_speed = max(50, fall_speed) # Limit max fallspeed
                        full_rows = []

                  flash_visible = True
                  current_piece = piece_queue.pop(0)
                  piece_queue.append(get_random_piece(BLOCK_IMAGES))
                  if not grid.is_valid_move(current_piece):
                      print("GAME OVER")
                      run = False
                  print(f"Score: {score} | Level: {level} | Lines: {total_lines_cleared}")
        

        draw_window(current_piece, grid, full_rows, line_clear_delay,
                     flash_visible, score, level, total_lines_cleared, held_piece, piece_queue)
        



    pygame.quit()

# Entry point of the program
if __name__ == "__main__":
    main()