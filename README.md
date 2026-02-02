# cs50-tetris
CS50 Final Project - Tetris

## Description
A recreation of Tetris, in the style of NES tetris with a few extra modern features.
The game is written in Python (3.12.10) with Pygame.

- Classic Tetris
- Piece-holding
- 5 Piece-preview
- Music + basic sound effect

## How to run
How to run:
It's important to install Python 3.12.10 - lastest version of Python is not compatabile with the lastest stable release of Python (as of writing)
the latest verison of pygame is required.

## Design
Design:
- Game uses a 2d grid array - the grid allows for easier collison detection, line clearing etc.
- Game also uses Delayed auto shift(DAS) for movement - to keep the feel of NES tetris
- Piece hold and piece queue - brought some 'newer' tetris features, NES tetris is quite difficult without these

## Future Improvements
Future improvement/bug fixes:
- Local high-score system
- Better music some loops feel jarring
- Rework scoring
- Visual polish
- Clean file structure/readability

## Project Structure
Structure:
- main.py - main game loop + asset loading
- grid.py - grid class and functions
- const.py - Constant values
- pieces - piece class and functions
- scoring - calculates score

## Resources
Resources:
https://www.youtube.com/watch?v=blLLtdv4tvo

https://www.youtube.com/watch?v=nF_crEtmpBo

copilot/claude - help with DAS, rotation, file structure

