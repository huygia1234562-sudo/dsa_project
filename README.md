# Monopoly Party Mode - DSA Project

A feature-rich Monopoly implementation built with Python and Tkinter, featuring 10 unique mini-games based on core Data Structures and Algorithms (DSA) concepts.

## 🎲 Features

### Core Monopoly Gameplay
- **Classic Rule Parity**: Includes movement, property purchasing, rent calculation (doubled for monopolies), housing development (even building rule), and jail mechanics.
- **Dynamic Turn Management**: Full state machine handling dice rolls, doubles, card draws, and bankruptcy.
- **Visual Interface**: Interactive board with token animations, dice physics, and floating status text.

### Party Mode: Railroad & Community Chest Challenges
- **Railroad Heists**: Landing on an opponent's railroad triggers a minigame battle. The winner steals money from the loser.
- **Community Chest Challenge**: Landing on Community Chest starts a global battle. The winner of the minigame claims the card's effect.

## 🧠 Mini-Games

The game integrates 10 distinct minigames:

1.  **Word Builder**
2.  **Snake Race**
3.  **Typing Race**
4.  **Pacman Survival**
5.  **Maze Escape**
6.  **Quick Math**
7.  **Ping Pong**
8.  **Coin Catcher**
9.  **Memory Card**
10. **Chicken Cross**

## 🛠️ Technology Stack
- **Language**: Python 3.x
- **GUI Framework**: Tkinter (Standard Library)
- **Graphics**: Tkinter Canvas API

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher installed on your system.

### Running the Game
Simply run the `main.py` file to launch the main menu:

```bash
python main.py
```

## 📁 Project Structure

- `main.py`: Entry point and main menu.
- `monopoly_logic.py`: The "Brain" - handles rules, player states, and board data.
- `monopoly_ui.py`: The "Face" - handles the board rendering and animations.
- `monopoly_dialogs.py`: Specialized UI components for Jail and Cards.
- `minigame_ui.py`: Implementation of all 10 DSA mini-games.

## 📜 License
This project was developed for the IT003.Q21.TTNT course.
