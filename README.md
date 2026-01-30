# 24 Card Game

An aesthetic poker card game built with Python and Pygame. Draw 4 cards and use algebraic operations (+, -, ×, ÷) to make 24!

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)

## Game Rules

1. Click "Draw Cards" to get 4 random poker cards
2. Try to combine all 4 numbers using +, -, ×, ÷ to equal exactly 24
3. Each card can only be used once
4. Card values: A=1, J=11, Q=12, K=13, number cards = face value
5. Cards are not returned to the deck, so you have 13 draws per game (52 cards ÷ 4)

## Features

- Beautiful animated card dealing with flip effects
- Hover effects and particle animations
- Twinkling star background
- Solution checker - verify if a solution exists
- Show answer - reveals a valid solution
- High DPI support for crisp graphics

## Installation

1. Make sure you have Python 3.7+ installed
2. Install Pygame:
   ```bash
   pip install pygame
   ```
3. Run the game:
   ```bash
   python game24.py
   ```

## Controls

### Mouse
- Click buttons to interact

### Keyboard Shortcuts
- `Space` - Draw cards
- `S` - Show answer
- `C` - Check if solution exists
- `N` - New game

## Screenshots

The game features:
- Elegant card design with suit symbols (♥ ♦ ♣ ♠)
- Smooth animations and transitions
- Dark purple aesthetic theme with gold accents

## Requirements

- Python 3.7+
- Pygame 2.0+

## License

MIT License - feel free to use and modify!
