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

pygame.mixer.music.load(os.path.join("Assets", "Music", "Tetris_normal.mp3"))

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

line_clear_sound = pygame.mixer.Sound(os.path.join("Assets", "Sounds", "tetris_line_clear.wav"))
line_clear_sound.set_volume(0.1)


def draw_menu(font_large, font_small):
    WIN.fill((0, 0, 0))

    # Title
    title = font_large.render("TETRIS", True, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    WIN.blit(title, title_rect)

    # Instructions
    start_text = font_small.render("PRESS SPACE TO START", True, (255, 200, 0))
    start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    WIN.blit(start_text, start_rect)

    # Controls
    controls_y = HEIGHT // 2 + 80
    controls = [
        "ARROWS - Move",
        "UP - Rotate",
        "Z - Rotate CCW",
        "C - Hold Piece",
        "SPACE - Hard Drop"
    ]

    for i, text in enumerate(controls):
        control_text = font_small.render(text, True, (180, 180, 180))
        control_rect = control_text.get_rect(center=(WIDTH // 2, controls_y + i * 30))
        WIN.blit(control_text, control_rect)
    pygame.display.update()

def draw_game_over(score, level, total_lines, font_large, font_small):
    # semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    WIN.blit(overlay, (0, 0))

    # Game over text
    game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    WIN.blit(game_over_text, game_over_rect)

    # Final stats
    stats_y = HEIGHT // 2
    score_text = font_small.render(f"SCORE: {score}", True, (255, 255, 255))
    level_text = font_small.render(f"LEVEL: {level}", True, (255, 255, 255))
    lines_text = font_small.render(f"LINES: {total_lines}", True, (255, 255, 255))
    
    WIN.blit(score_text, score_text.get_rect(center=(WIDTH // 2, stats_y)))
    WIN.blit(level_text, level_text.get_rect(center=(WIDTH // 2, stats_y + 40)))
    WIN.blit(lines_text, lines_text.get_rect(center=(WIDTH // 2, stats_y + 80)))

    # Restart prompt
    restart_text = font_small.render("PRESS R TO RESTART", True, (255, 200, 0))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
    WIN.blit(restart_text, restart_rect)

    pygame.display.update()

def reset_game():
    grid = Grid(GRID_WIDTH, GRID_HEIGHT)
    
    fall_time = 0
    dt = 0
    das_delay = 100
    das_repeat = 50
    das_timer = 0
    das_active = False
    last_key = None
    
    line_clear_delay = 0
    full_rows = []
    flash_visible = True
    flash_timer = 0
    
    score = 0
    level = 0
    total_lines_cleared = 0
    
    base_fall_speed = 500
    fall_speed = base_fall_speed
    
    held_piece = None
    can_swap = True

    
    piece_queue = [get_random_piece(BLOCK_IMAGES) for _ in range(5)]
    current_piece = piece_queue.pop(0)
    piece_queue.append(get_random_piece(BLOCK_IMAGES))
    
    return (grid, fall_time, dt, das_delay, das_repeat, das_timer, das_active, last_key,
            line_clear_delay, full_rows, flash_visible, flash_timer, score, level, 
            total_lines_cleared, base_fall_speed, fall_speed, held_piece, can_swap, 
            piece_queue, current_piece)

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

def draw_ghost_piece(current_piece, grid):
    # Find where piece will land
    ghost_y = current_piece.y
    while True:
        # Keep moving down until it would collide
        test_y = ghost_y + 1
        valid = True
        for row in range(len(current_piece.shape)):
            for col in range(len(current_piece.shape[row])):
                if current_piece.shape[row][col] == 1:
                    new_y = test_y + row
                    new_x = current_piece.x + col
                    if new_y >= GRID_HEIGHT or (new_y >= 0 and grid.get_cell(new_x, new_y) != 0):
                        valid = False
                        break
            if not valid:
                break
        
        if valid:
            ghost_y = test_y
        else:
            break
    
    # Draw ghost piece at landing position
    for row in range(len(current_piece.shape)):
        for col in range(len(current_piece.shape[row])):
            if current_piece.shape[row][col] == 1:
                x = PLAY_AREA_X + (current_piece.x + col) * BLOCK
                y = PLAY_AREA_Y + (ghost_y + row) * BLOCK
                pygame.draw.rect(WIN, (255, 255, 255), (x, y, BLOCK, BLOCK), 1)

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

            
            draw_ghost_piece(current_piece, grid)

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

    # Game states
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2

    game_state = MENU

# Initialize to None - will be set when game starts
    grid = None
    current_piece = None
    score = 0
    level = 0
    total_lines_cleared = 0
    held_piece = None
    piece_queue = []
    fall_time = 0
    dt = 0
    das_timer = 0
    das_active = False
    last_key = None
    line_clear_delay = 0
    full_rows = []
    flash_visible = True
    flash_timer = 0
    can_swap = True
    base_fall_speed = 500
    fall_speed = 500
    current_fall_speed = 500
    current_track = None

    pending_music_change = None

    pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

   


    # Clock and main game loop
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)

        if game_state == MENU:
            draw_menu(font_large, font_small)

             # Loop through the event queue
            for event in pygame.event.get():
                # Check for quit event
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE :
                     # Start new game
                    (grid, fall_time, dt, das_delay, das_repeat, das_timer, das_active, last_key,
                     line_clear_delay, full_rows, flash_visible, flash_timer, score, level,
                     total_lines_cleared, base_fall_speed, fall_speed, held_piece, can_swap,
                     piece_queue, current_piece) = reset_game()
                    

                    # Start music (normal)
                    pygame.mixer.music.load(os.path.join("Assets", "Music", "Tetris_normal.mp3"))
                    pygame.mixer.music.play(0)
                    current_track = "normal"


                    game_state = PLAYING

        elif game_state == GAME_OVER:
            draw_game_over(score, level, total_lines_cleared, font_large, font_small)

            # Loop through the event queue
            for event in pygame.event.get():
                # Check for quit event
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                     # Start new game
                    (grid, fall_time, dt, das_delay, das_repeat, das_timer, das_active, last_key,
                     line_clear_delay, full_rows, flash_visible, flash_timer, score, level,
                     total_lines_cleared, base_fall_speed, fall_speed, held_piece, can_swap,
                     piece_queue, current_piece) = reset_game()
                    
                    # Start music (normal)
                    pygame.mixer.music.load(os.path.join("Assets", "Music", "Tetris_normal.mp3"))
                    pygame.mixer.music.play(0)  # Play once
                    current_track = "normal"
                    
                    game_state = PLAYING
        
        elif game_state == PLAYING:

            fall_time += clock.get_rawtime()
            dt = clock.get_rawtime() # Delta time in milliseconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                # Check if music track finished
                if event.type == pygame.USEREVENT + 1:
                    print("Music end event fired!")
                    if pending_music_change:
                        print(f"Switching to {pending_music_change}")
                        pygame.mixer.music.load(os.path.join("Assets", "Music", f"Tetris_{pending_music_change}.mp3"))
                        pygame.mixer.music.play(0)  # Play once
                        current_track = pending_music_change
                        pending_music_change = None
                    else:
                        # No change pending - just loop the current track
                        print(f"Looping {current_track}")
                        pygame.mixer.music.play(0)  # Restart the same track

                
                # Handle initial key press
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: # Move left
                        if grid.is_valid_move(current_piece, dx=-1):
                            current_piece.x -= 1
                            last_key = pygame.K_LEFT
                            das_timer = 0
                            das_active = False
                    elif event.key == pygame.K_RIGHT: # Move right
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
                            line_clear_sound.play()
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

                    
                    # REMOVE OR HIDE FROM USER - CHEATS (cheat code in future maybe?)    
                    elif event.key == pygame.K_q:
                        # DEBUG: Fill bottom 4 rows for testing
                        for row in range(GRID_HEIGHT - 4, GRID_HEIGHT):
                            for col in range(GRID_WIDTH):
                                if grid.get_cell(col, row) == 0:  # Only fill empty cells
                                        grid.grid[row][col] = 'T'  # Fill with T piece type


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

                            


            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                current_fall_speed = S_D_SPEED  # Faster fall speed when down key is held  
            else:
                current_fall_speed = fall_speed
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
                            line_clear_sound.play()
                            line_clear_delay = FLASH_LENGTH
                        else:
                            current_piece = piece_queue.pop(0) # Spawn new piece
                            piece_queue.append(get_random_piece(BLOCK_IMAGES))
                        
                        # If new piece spawns in occupied grid spaces - game over
                        if not grid.is_valid_move(current_piece):
                            print("GAME OVER!")
                            game_state = GAME_OVER
                            pygame.mixer.music.stop
                        

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

                            old_level = level
                            level = total_lines_cleared // LINES_PER_LEVEL
                            fall_speed = base_fall_speed - (level * 50) # Increase fall speed based on level
                            fall_speed = max(50, fall_speed) # Limit max fallspeed
                            full_rows = []

                            # Check if level changed and update music
                            if level != old_level:
                                print(f"Level changed from {old_level} to {level}")  # Debug
                                if level == 5:
                                    pending_music_change = "fast"
                                    print("Flagged music change to FAST")  # Debug
                                elif level == 10:
                                    pending_music_change = "fastest"
                                    print("Flagged music change to FASTEST")  # Debug
                        

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