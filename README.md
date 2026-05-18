# Monopoly Party Mode - DSA Project

Python/Tkinter Monopoly-style game with a party-mode minigame system, Monopoly GO-inspired board visuals, Vietnamese-themed tile names, and DSA-based minigames.

## Features

### Monopoly Gameplay

- Classic Monopoly movement, dice rolls, doubles, jail, Chance cards, Community Chest cards, rent, bankruptcy, houses, and hotels.
- 40-tile board with custom Vietnamese place names.
- Three-choice landing menu on purchasable tiles:
  - `1. Continue`: continue normal tile effect, such as rent, minigame, or end turn.
  - `2. Buy / Upgrade`: buy unowned property or upgrade current player's property.
  - `3. Sell`: sell current player's house/hotel or sell owned property back to bank.
- House/hotel upgrades appear as 2.5D buildings on the tile color lane.
- Owners are shown with player-colored houses.
- Monopoly GO-style isometric board with generated tile images, color lanes, place names, and prices baked into each tile image.

### Party Mode

- Minigame tiles trigger a minigame challenge; winner receives the card effect.
- Active random minigames:
  1. Typing Race
  2. Ping Pong
  3. Quick Math
  4. Coin Catcher
  5. Pacman
  6. Snake Race

## DSA Concepts

- Typing Race: KMP string matching.
- Ping Pong: AABB collision detection.
- Quick Math: Reverse Polish Notation and stack evaluation.
- Coin Catcher: AABB collision detection and list-based object tracking.
- Pacman: BFS pathfinding on a grid.
- Snake Race: linked-list style snake body management.
- Monopoly engine: arrays/lists for board data, circular movement with modulo, dictionaries for groups/cards, and queue-like card deck traversal.

## Run

```powershell
python main.py
```

## Debug Minigames

Use the standalone launcher to test minigames without starting Monopoly:

```powershell
python debug_minigames.py
```

Launch one directly:

```powershell
python debug_minigames.py "Quick Math"
python debug_minigames.py 3
```

## Project Structure

- `main.py`: main menu and app entry point.
- `monopoly_logic.py`: Monopoly rules, board data, rent, cards, jail, housing, and bankruptcy.
- `monopoly_ui.py`: Tkinter UI, isometric board rendering, dice animation, landing menu, token flow, and minigame integration.
- `monopoly_dialogs.py`: jail and card dialogs.
- `minigame_ui.py`: minigame implementations.
- `debug_minigames.py`: standalone minigame debug launcher.

## Requirements

- Python 3.10+
- Pillow (`PIL`) for generated tile images.
- Tkinter, included with standard Python on most installs.

## Course

Developed for IT003.Q21.TTNT.
