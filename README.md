# Infinite Minesweeper (Python)

An endless Minesweeper game built in Python with Tkinter. Instead of a fixed board size, you can scroll infinitely in any direction while new sections of the grid generate automatically.

## Features
- **Endless Map:** Generates the board in 16x16 blocks only when you scroll into new areas.
- **Smooth Performance:** Only draws the tiles currently visible inside your game window so the game stays fast.
- **Safe First Click:** Clears mines around your very first click so you never lose on turn one.

## Controls
- **Left-Click:** Reveal a tile
- **Right-Click:** Place or remove a flag
- **Middle-Click + Drag (or Arrow Keys):** Move around the board
- **R:** Restart with a new board

## How to Run
Make sure you have Python 3 installed, then run the file in your terminal or IDE:
```bash
python infinite_minesweeper.py
```

## Acknowledgments
Built using Python and Tkinter, with AI assistance used for debugging and structuring the infinite grid logic.
