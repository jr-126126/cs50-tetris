# cs50-tetris
CS50 Final Project - Tetris

## Demo Video
https://www.youtube.com/watch?v=rgUQbwz1_z8

## Description
A recreation of Tetris, in the style of NES tetris with a few extra modern features.
The game is written in Python (3.12.10) with Pygame.

**Features:**
- Classic Tetris with NES-style controls
- Piece-holding system
- 5 Piece-preview queue
- Progressive difficulty with increasing fall speed
- Dynamic music syncs with level progression
- Basic line clear animation and sound effects


## How to run
It's important to install Python 3.12.10 - lastest version of Python is not compatabile with the lastest stable release of Python (as of writing)
the latest verison of pygame is required.
```bash
# Install Python 3.12.10 from python.org

# Install Pygame
pip install pygame
# Or Pygame-CE may fix compability issues
pip install py-game

# Clone the repository
git clone https://github.com/jrjr-126126/cs50-tetris
cd cs50-tetris

# Run the game
python main.py
```
## Controls
- **Arrow Keys (←/→)** - Move piece left/right
- **Arrow Key (↓)** - Soft drop (faster fall)
- **Space** - Hard drop (instant drop)
- **Up Arrow** - Rotate clockwise
- **Z** - Rotate counter-clockwise
- **C** - Hold piece

## Design Decisions

### Grid System
Game board is as a 10x20 2D array where '0' represents empty cells. '1's Represent occupied cells. This modular design helps simplify collision, line clearing, rotation and other important game elements.

### Piece Representation
Pieces are defined as 2D matrices in the 'SHAPES' dictionary. Pieces also have a class that stores it's shape, position and associated asset(piece colour). A single block asset is loaded based on piece shape, each '1' of the shape is filled with the appropriate coloured block.

### Movement System (DAS)
Implements Delayed Auto Shift (DAS) to replicate NES Tetris control style:
- Initial key press moves the piece immediately 
- Hold delay: Delay before auto-repeat begins
- Auto-repeat rate: sets the time between movements

Creates movement system that rewards tapping quickly for speed - whilst this can feel somewhat jank, it encapsulates the old-school NES feel.

### Piece Queue & Hold System
**Queue:** Pre-generates 5 pieces using random.choice(), when a piece is moved to the current piece add a new random piece to the queue.

**Hold:** Stores a single piece that can be swapped with the current piece. Limited to one swap per piece. Temp variable is used when held piece variable and current piece are stored.

```python
temp = current_piece
current_piece = held_piece
held_piece = temp
```


### Line Clearing
When a row is complete:
1. Full rows are detected via 'get_full_rows()'
2. Line clear animation begins(ghost blocks flash based on FLASH_SPEED and FLASH_LENGTH 10ms, 100ms respectively)
3. After animation completes, rows are removed and grids shift down
4. Score is calculated
5. Level increases every 10 lines, gradually increasing falling speed

### Music System
Music transitions 'seamlessly' between three tempo levels:
- Normal (Levels 0-4)
- Fast (Levels 5-9)
- Fastest (Levels 10+)

Uses 'pygame.mixer.music.set_endevent()' to detect track completion and switch to the next tempo only when last track has completed.

## Challenges
**Event Loop Management:** Implementing game states required refactoring the main game loop. Dealing with indentation and scope was difficult

**Asset Dependencies:** Many functions require loaded assets (images, fonts, sounds). Balancing organisation wiith asset scope/accessiblity proved challenging.

**Pygame Init Issues:** Encountered conflicts with joystick module, individual module init to debug took a while. Managed to find a work around eventually.



## Future Improvements
- **Local high-score system**
- **Smoother music loops**
- **Rework scoring**
- **Visual/audio polish**
- **Refactor** to seperate rendering from game logic
- **Pause functionality**
- **Settings menu**

## Project Structure
Structure:
- main.py - main game loop + rendering
- grid.py - grid class and functions
- const.py - Constant values
- pieces.py - piece class and functions
- scoring.py - calculates score

## Resources
Resources:
https://www.youtube.com/watch?v=blLLtdv4tvo

https://www.youtube.com/watch?v=nF_crEtmpBo

copilot/claude - help with DAS, rotation, file structure, event loop management

**Assets:**
- Block sprites: Tetriminos Pack By L-Gad: https://l-gad.itch.io/tetriminos-asset-pack
- Font: Press Start 2P (Google Fonts)
- Music: No copyright piano cover: https://www.youtube.com/watch?v=Q7mcjjl_P3k

