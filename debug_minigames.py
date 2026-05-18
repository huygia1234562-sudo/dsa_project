import sys
import traceback
import tkinter as tk
from tkinter import messagebox

from minigame_ui import (
    TypingRaceDialog,
    PingPongDialog,
    QuickMathDialog,
    CoinCatcherDialog,
    PacmanDialog,
    SnakeRaceDialog,
)


GAMES = [
    ("Typing Race", TypingRaceDialog),
    ("Ping Pong", PingPongDialog),
    ("Quick Math", QuickMathDialog),
    ("Coin Catcher", CoinCatcherDialog),
    ("Pacman", PacmanDialog),
    ("Snake Race", SnakeRaceDialog),
]


class MinigameDebugApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minigame Debug Launcher")
        self.root.geometry("520x430")
        self.root.minsize(460, 360)

        tk.Label(
            root,
            text="Minigame Debug Launcher",
            font=("Arial", 16, "bold"),
        ).pack(pady=(12, 6))

        body = tk.Frame(root)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        left = tk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        tk.Label(left, text="Choose minigame", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.listbox = tk.Listbox(left, font=("Arial", 11), height=12)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=(4, 8))
        for name, _ in GAMES:
            self.listbox.insert(tk.END, name)
        self.listbox.selection_set(0)
        self.listbox.bind("<Double-Button-1>", lambda _event: self.launch_selected())

        buttons = tk.Frame(left)
        buttons.pack(fill=tk.X)
        tk.Button(
            buttons,
            text="Run Selected",
            command=self.launch_selected,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Button(
            buttons,
            text="Clear Log",
            command=self.clear_log,
            bg="#40546a",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        right = tk.Frame(body)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Debug log", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.log = tk.Text(right, height=12, width=30, font=("Consolas", 9), wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self.write_log("Ready. Double-click a game or press Run Selected.")

    def selected_game(self):
        selection = self.listbox.curselection()
        if not selection:
            return None
        return GAMES[selection[0]]

    def launch_selected(self):
        game = self.selected_game()
        if game is None:
            messagebox.showwarning("No Game", "Select a minigame first.", parent=self.root)
            return
        self.launch_game(*game)

    def launch_game(self, name, dialog_cls):
        self.write_log(f"Launching: {name}")

        def on_finish(winner):
            self.write_log(f"{name} finished. Winner: Player {winner}")

        try:
            dialog = dialog_cls(self.root, on_finish)
            dialog.focus_force()
        except Exception:
            details = traceback.format_exc()
            self.write_log(details)
            messagebox.showerror("Minigame Error", details, parent=self.root)

    def clear_log(self):
        self.log.delete("1.0", tk.END)

    def write_log(self, text):
        self.log.insert(tk.END, text.rstrip() + "\n")
        self.log.see(tk.END)


def find_game(query):
    query = query.lower().strip()
    if query.isdigit():
        idx = int(query) - 1
        if 0 <= idx < len(GAMES):
            return GAMES[idx]
    for name, dialog_cls in GAMES:
        if query in name.lower() or query in dialog_cls.__name__.lower():
            return name, dialog_cls
    return None


def main():
    root = tk.Tk()
    app = MinigameDebugApp(root)
    if len(sys.argv) > 1:
        game = find_game(" ".join(sys.argv[1:]))
        if game is None:
            names = ", ".join(name for name, _ in GAMES)
            app.write_log(f"No match. Available: {names}")
        else:
            root.after(200, lambda: app.launch_game(*game))
    root.mainloop()


if __name__ == "__main__":
    main()
