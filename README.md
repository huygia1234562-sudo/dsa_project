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

## 🧠 DSA Mini-Games

The game integrates 10 distinct minigames, each demonstrating a different DSA technique:

1.  **Word Builder**: Uses a **Trie (Prefix Tree)** for O(L) word validation.
2.  **Snake Race**: Uses a **Singly Linked List** for body segment management.
3.  **Typing Race**: Uses the **KMP (Knuth-Morris-Pratt)** algorithm for pattern matching.
4.  **Pacman Survival**: Uses **BFS (Breadth-First Search)** for ghost pathfinding.
5.  **Maze Escape**: Uses **DFS (Depth-First Search)** for randomized maze generation.
6.  **Quick Math**: Uses **RPN (Reverse Polish Notation)** and **Stacks** for expression evaluation.
7.  **Ping Pong**: Uses **AABB Collision Detection**.
8.  **Coin Catcher**: Uses **AABB Collision Detection** and object pooling.
9.  **Memory Card**: Uses **Fisher-Yates Shuffle** and **Hash Maps**.
10. **Chicken Cross**: Uses **Circular Queues (Deque)** for object pooling of obstacles.

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
- `report.md`: Detailed academic report of the project.

## 📜 License
This project was developed for the IT003.Q21.TTNT course.
