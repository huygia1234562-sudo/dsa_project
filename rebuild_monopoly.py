
import os

logic_content = """import random

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.money = 1500
        self.position = 0
        # 5 landmarks, levels 0 to 5
        self.landmarks = [0, 0, 0, 0, 0]

    def upgrade_landmark(self, index):
        if self.landmarks[index] < 5:
            cost = self.get_upgrade_cost(index)
            if self.money >= cost:
                self.money -= cost
                self.landmarks[index] += 1
                return True
        return False

    def get_upgrade_cost(self, index):
        return (self.landmarks[index] + 1) * 150

class Space:
    def __init__(self, name, space_type, value=0, color="white"):
        self.name = name
        self.space_type = space_type  # money, railroad, chance, tax, go, jail
        self.value = value
        self.color = color

class MonopolyLogic:
    def __init__(self):
        self.players = [
            Player("Player 1", "red"),
            Player("Player 2", "blue")
        ]
        self.current_player_idx = 0
        self.board = self._init_board()

    def _init_board(self):
        board = []
        for i in range(40):
            if i == 0:
                board.append(Space("GO", "go", 200, "#d9ead3"))
            elif i == 10:
                board.append(Space("JAIL", "jail", 0, "#f4cccc"))
            elif i == 20:
                board.append(Space("FREE PARK", "money", 100, "#d9ead3"))
            elif i == 30:
                board.append(Space("GO TO JAIL", "jail", 0, "#f4cccc"))
            elif i in [5, 15, 25, 35]:
                board.append(Space("RAILROAD\\n(Minigame)", "railroad", 0, "#fce5cd"))
            elif i in [4, 38]:
                board.append(Space("TAX", "tax", 150, "#eeeeee"))
            elif i in [7, 22, 36]:
                board.append(Space("CHANCE", "chance", 0, "#fff2cc"))
            else:
                board.append(Space(f"PROPERTY\\nTILE", "money", 50 + (i*5), "#9fc5e8"))
        return board

    def roll_dice(self):
        return random.randint(1, 6), random.randint(1, 6)

    def next_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
"""

ui_content = """import tkinter as tk
from tkinter import messagebox
import random
import math
from monopoly_logic import MonopolyLogic
from minigame_ui import (
    TypingRaceDialog, PingPongDialog, QuickMathDialog, CoinCatcherDialog,
    MemoryCardDialog, PacmanDialog, ChickenCrossDialog, MazeEscapeDialog
)

class FloatingText:
    def __init__(self, canvas, x, y, text, color):
        self.canvas = canvas
        self.id = canvas.create_text(x, y, text=text, fill=color, font=("Arial", 16, "bold"), tags="dynamic")
        self.y = y
        self.life = 30
    def update(self):
        self.y -= 2
        self.canvas.coords(self.id, self.canvas.coords(self.id)[0], self.y)
        self.life -= 1
        if self.life <= 0:
            self.canvas.delete(self.id)
        return self.life > 0

class MonopolyUI:
    def __init__(self, parent, on_back):
        self.parent = parent
        self.on_back = on_back
        self.logic = MonopolyLogic()
        self.floating_texts = []
        self.animating = False
        
        self.setup_ui()
        self.draw_static_board()
        self.draw_dynamic()
        self.update_info()
        self.animate_tick()

    def setup_ui(self):
        self.toolbar = tk.Frame(self.parent, bg="#d9e3f0", height=50)
        self.toolbar.pack(fill=tk.X)
        self.toolbar.pack_propagate(False)
        
        tk.Button(self.toolbar, text="< Back to Menu", command=self.on_back).pack(side=tk.LEFT, padx=10, pady=10)
        self.info_label = tk.Label(self.toolbar, text="", font=("Arial", 14, "bold"), bg="#d9e3f0")
        self.info_label.pack(side=tk.LEFT, padx=20, pady=10)

        self.body_frame = tk.Frame(self.parent, bg="#eef2f3")
        self.body_frame.pack(expand=True, fill=tk.BOTH)

        self.board_size = 650
        self.space_size = self.board_size / 11
        
        self.canvas = tk.Canvas(self.body_frame, bg="#cbf0cd", width=self.board_size, height=self.board_size, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Move the ROLL button to bottom right
        btn_size = 100
        self.btn_roll = tk.Button(self.canvas, text="ROLL", font=("Arial", 16, "bold"), 
                                  bg="#e63946", fg="white", activebackground="#d62828",
                                  relief=tk.RAISED, bd=5, command=self.handle_roll)
        self.btn_roll.place(x=self.board_size - 130, y=self.board_size - 130, width=btn_size, height=btn_size)

        # Right frame for City Builds
        self.city_frame = tk.Frame(self.body_frame, bg="white", width=250)
        self.city_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.city_frame.pack_propagate(False)
        
        self.city_labels = []
        self.city_btns = []
        tk.Label(self.city_frame, text="City Landmarks", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        for i in range(5):
            lbl = tk.Label(self.city_frame, text=f"Landmark {i+1}: Lv 0", font=("Arial", 12), bg="white")
            lbl.pack(pady=(10, 0))
            btn = tk.Button(self.city_frame, text="Upgrade ($150)", bg="#a8dadc", command=lambda idx=i: self.upgrade_landmark(idx))
            btn.pack(pady=(0, 10))
            self.city_labels.append(lbl)
            self.city_btns.append(btn)

    def spawn_floating_text(self, x, y, text, color):
        self.floating_texts.append(FloatingText(self.canvas, x, y, text, color))

    def animate_tick(self):
        new_texts = []
        for ft in self.floating_texts:
            if ft.update():
                new_texts.append(ft)
        self.floating_texts = new_texts
        self.parent.after(40, self.animate_tick)

    def get_logical_coords(self, index):
        if 0 <= index <= 10: return 10 - index, 10
        elif 11 <= index <= 20: return 0, 20 - index
        elif 21 <= index <= 30: return index - 20, 0
        else: return 10, index - 30

    def to_iso(self, x, y, z=0):
        scale = 30
        x *= scale
        y *= scale
        iso_x = 320 + (x - y) * 0.866
        iso_y = 100 + (x + y) * 0.5 - z
        return iso_x, iso_y

    def draw_static_board(self):
        self.canvas.delete("board_item")
        
        # Center green board
        cb1 = self.to_iso(1, 1, 0)
        cb2 = self.to_iso(10, 1, 0)
        cb3 = self.to_iso(10, 10, 0)
        cb4 = self.to_iso(1, 10, 0)
        self.canvas.create_polygon(cb1[0], cb1[1], cb2[0], cb2[1], cb3[0], cb3[1], cb4[0], cb4[1], fill="#9ec52d", outline="#9ec52d", tags="board_item")

        # MONOPOLY banner
        mb1 = self.to_iso(2, 4.5, 1)
        mb2 = self.to_iso(9, 4.5, 1)
        mb3 = self.to_iso(9, 6.5, 1)
        mb4 = self.to_iso(2, 6.5, 1)
        self.canvas.create_polygon(mb1[0], mb1[1], mb2[0], mb2[1], mb3[0], mb3[1], mb4[0], mb4[1], fill="#e9322e", outline="white", width=4, tags="board_item")
        tx, ty = self.to_iso(5.5, 5.5, 5)
        self.canvas.create_text(tx, ty, text="MONOPOLY", font=("Arial", 26, "bold"), fill="white", angle=28, tags="board_item")

        space_draw_order = []
        for i, space in enumerate(self.logic.board):
            tx, ty = self.get_logical_coords(i)
            space_draw_order.append((tx + ty, i, space, tx, ty))
        
        space_draw_order.sort(key=lambda item: item[0])
        self.space_centers = {}
        
        for depth, i, space, tx, ty in space_draw_order:
            z_top = 10
            color = space.color
            
            c1, c2, c3, c4 = self.to_iso(tx, ty, z_top), self.to_iso(tx+1, ty, z_top), self.to_iso(tx+1, ty+1, z_top), self.to_iso(tx, ty+1, z_top)
            b1, b2, b3, b4 = self.to_iso(tx, ty, 0), self.to_iso(tx+1, ty, 0), self.to_iso(tx+1, ty+1, 0), self.to_iso(tx, ty+1, 0)
            
            self.canvas.create_polygon(c4[0], c4[1], b4[0], b4[1], b1[0], b1[1], c1[0], c1[1], fill="#999999", outline="black", tags="board_item")
            self.canvas.create_polygon(c3[0], c3[1], b3[0], b3[1], b4[0], b4[1], c4[0], c4[1], fill="#666666", outline="black", tags="board_item")
            self.canvas.create_polygon(c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], c4[0], c4[1], fill=color, outline="black", tags="board_item")
            
            display_text = space.name
            if space.value > 0 and space.space_type == "money":
               display_text += f"\\n${space.value}"
            elif space.value > 0 and space.space_type == "tax":
               display_text += f"\\n-${space.value}"
                
            ct_x, ct_y = self.to_iso(tx+0.5, ty+0.5, z_top+4)
            self.canvas.create_text(ct_x, ct_y, text=display_text, font=("Arial", 6, "bold"), justify=tk.CENTER, tags="board_item")
            
            self.space_centers[i] = (ct_x, ct_y)

    def draw_dynamic(self):
        self.canvas.delete("player_token")
        for idx, player in enumerate(self.logic.players):
            if hasattr(self, "animating_player") and self.animating_player == idx:
                px, py = self.anim_x, self.anim_y
            else:
                tx, ty = self.get_logical_coords(player.position)
                ox = 0.3 + (idx * 0.4)
                px, py = self.to_iso(tx+ox, ty+0.5, 20)
            
            self.canvas.create_oval(px-10, py-20, px+10, py, fill=player.color, outline="white", width=2, tags="player_token")

    def upgrade_landmark(self, index):
        player = self.logic.players[self.logic.current_player_idx]
        if player.upgrade_landmark(index):
            tx, ty = self.space_centers[player.position]
            self.spawn_floating_text(tx, ty-50, "-$$$", "red")
            self.update_info()
            
            # Level Up City check
            if all(v == 5 for v in player.landmarks):
                tk.messagebox.showinfo("City Complete!", f"{player.name} finished all Landmarks!\\nWelcome to the next board map!")
                player.landmarks = [0, 0, 0, 0, 0]
                self.update_info()
        else:
            tk.messagebox.showwarning("Upgrade Failed", "Not enough money or reached max level!")

    def update_info(self):
        player = self.logic.players[self.logic.current_player_idx]
        self.info_label.config(text=f"{player.name}'s Turn   |   Money: ${player.money}", fg=player.color)
        
        # update side panel buttons
        for i in range(5):
            lvl = player.landmarks[i]
            cost = player.get_upgrade_cost(i)
            self.city_labels[i].config(text=f"Landmark {i+1}: Level {lvl}/5")
            if lvl == 5:
                self.city_btns[i].config(text="MAX", state=tk.DISABLED)
            else:
                self.city_btns[i].config(text=f"Upgrade (${cost})", state=tk.NORMAL)

    def handle_roll(self):
        self.btn_roll.config(state=tk.DISABLED)
        for b in self.city_btns: b.config(state=tk.DISABLED)
        
        d1, d2 = self.logic.roll_dice()
        self.animate_dice_throw(35, d1, d2)

    def draw_die_face(self, x, y, value):
        s = 20
        top_color = "white"
        left_color = "#e0e0e0"
        right_color = "#cccccc"
        
        t1, t2, t3, t4 = (x, y-s), (x+s*1.2, y-s*0.4), (x, y+s*0.2), (x-s*1.2, y-s*0.4)
        self.canvas.create_polygon(*t1, *t2, *t3, *t4, fill=top_color, outline="black", width=2, tags="dice_anim")
        
        l1, l2, l3, l4 = t4, t3, (x, y+s*1.4), (x-s*1.2, y+s*0.8)
        self.canvas.create_polygon(*l1, *l2, *l3, *l4, fill=left_color, outline="black", width=2, tags="dice_anim")
        
        r1, r2, r3, r4 = t3, t2, (x+s*1.2, y+s*0.8), (x, y+s*1.4)
        self.canvas.create_polygon(*r1, *r2, *r3, *r4, fill=right_color, outline="black", width=2, tags="dice_anim")
        
        r = 3
        def draw_pip(px, py):
            ix, iy = x + px * 1.2, y - s*0.4 + py * 0.6
            self.canvas.create_oval(ix-r, iy-r, ix+r, iy+r, fill="black", tags="dice_anim")
        
        dots = {1: [(0,0)], 2: [(-6,-6), (6,6)], 3: [(-6,-6), (0,0), (6,6)], 
                4: [(-6,-6), (-6,6), (6,-6), (6,6)], 5: [(-6,-6), (-6,6), (6,-6), (6,6), (0,0)],
                6: [(-6,-8), (-6,0), (-6,8), (6,-8), (6,0), (6,8)]}
        for dx, dy in dots.get(value, []): draw_pip(dx, dy)

    def animate_dice_throw(self, ticks, d1, d2):
        self.canvas.delete("dice_anim")
        if not hasattr(self, "dice_state") or ticks == 35:
            self.dice_state = {
                "d1x": self.board_size/2, "d1y": self.board_size - 100,
                "d2x": self.board_size/2+40, "d2y": self.board_size - 80,
                "d1vx": -8.0, "d1vy": -24.0, "d2vx": -11.0, "d2vy": -22.0, "g": 2.5
            }
        
        if ticks > 0:
            st = self.dice_state
            st["d1x"] += st["d1vx"]; st["d1y"] += st["d1vy"]; st["d1vy"] += st["g"]
            st["d2x"] += st["d2vx"]; st["d2y"] += st["d2vy"]; st["d2vy"] += st["g"]
            
            floor = self.board_size / 2 + 30
            if st["d1y"] > floor and st["d1vy"] > 0:
                st["d1y"] = floor; st["d1vy"] = -st["d1vy"] * 0.55; st["d1vx"] *= 0.65
            if st["d2y"] > floor and st["d2vy"] > 0:
                st["d2y"] = floor; st["d2vy"] = -st["d2vy"] * 0.55; st["d2vx"] *= 0.65
            
            self.draw_die_face(st["d1x"], st["d1y"], random.randint(1, 6))
            self.draw_die_face(st["d2x"], st["d2y"], random.randint(1, 6))
            self.parent.after(40, self.animate_dice_throw, ticks - 1, d1, d2)
        else:
            self.draw_die_face(self.dice_state["d1x"], self.dice_state["d1y"], d1)
            self.draw_die_face(self.dice_state["d2x"], self.dice_state["d2y"], d2)
            
            steps = d1 + d2
            self.spawn_floating_text(self.board_size/2, self.board_size/2 - 50, f"MOVE {steps}!", "blue")
            self.parent.after(800, lambda: self.start_token_anim(steps))

    def start_token_anim(self, steps):
        self.canvas.delete("dice_anim")
        self.animating_player = self.logic.current_player_idx
        self.anim_steps_left = steps
        self.anim_step_progress = 0.0
        self.anim_current_space = self.logic.players[self.animating_player].position
        self.animate_token()

    def animate_token(self):
        player = self.logic.players[self.animating_player]
        if self.anim_steps_left <= 0:
            del self.animating_player
            self.draw_dynamic()
            self.handle_space_action(player, self.logic.board[player.position])
            return

        next_space = (self.anim_current_space + 1) % 40
        self.anim_step_progress += 0.25 # 4 frames per tile
        
        if self.anim_step_progress >= 1.0:
            self.anim_current_space = next_space
            player.position = next_space
            self.anim_step_progress = 0.0
            self.anim_steps_left -= 1
            
            if next_space == 0:
                player.money += 200
                self.update_info()
                tx, ty = self.space_centers[0]
                self.spawn_floating_text(tx, ty - 30, "+$200 PASS GO", "green")
                
        p1 = self.space_centers[self.anim_current_space]
        p2 = self.space_centers[next_space]
        
        t = self.anim_step_progress
        bx = p1[0] + (p2[0] - p1[0]) * t
        by = p1[1] + (p2[1] - p1[1]) * t
        arc = math.sin(t * math.pi) * 20
        
        self.anim_x = bx
        self.anim_y = by - 15 - arc
        
        self.draw_dynamic()
        self.parent.after(40, self.animate_token)

    def handle_space_action(self, player, space):
        tx, ty = self.space_centers[player.position]
        
        if space.space_type == "money":
            player.money += space.value
            self.spawn_floating_text(tx, ty - 30, f"+${space.value}", "green")
            self.end_player_turn()
            
        elif space.space_type == "tax":
            player.money -= space.value
            self.spawn_floating_text(tx, ty - 30, f"-${space.value}", "red")
            self.end_player_turn()
            
        elif space.space_type == "railroad":
            self.spawn_floating_text(tx, ty - 30, "MINIGAME!", "orange")
            popup = tk.Toplevel(self.parent)
            popup.title("Minigame Time!")
            popup.geometry("300x150")
            tk.Label(popup, text=f"Railroad!\\nWin the minigame to steal from the opponent!").pack(pady=20)
            tk.Button(popup, text="Play Minigame", command=lambda: self.launch_random_minigame(popup, player)).pack()
            
        else:
            self.end_player_turn()

    def launch_random_minigame(self, popup, player):
        popup.destroy()
        minigames = [TypingRaceDialog, PingPongDialog, QuickMathDialog, CoinCatcherDialog, MemoryCardDialog, PacmanDialog, ChickenCrossDialog, MazeEscapeDialog]
        selected_minigame = random.choice(minigames)
        
        def on_minigame_end(winner):
            winning_player = self.logic.players[winner - 1]
            other_player = self.logic.players[1 if winner == 1 else 0]
            
            steal_amnt = min(500, other_player.money)
            winning_player.money += steal_amnt
            other_player.money -= steal_amnt
            
            tx, ty = self.space_centers[winning_player.position]
            self.spawn_floating_text(tx, ty-40, f"+${steal_amnt} HEIST!", "green")
            
            tk.messagebox.showinfo("Heist Success!", f"{winning_player.name} won and stole ${steal_amnt} from {other_player.name}!")
            self.end_player_turn()

        selected_minigame(self.parent, on_minigame_end)

    def end_player_turn(self):
        self.logic.next_turn()
        self.update_info()
        self.btn_roll.config(state=tk.NORMAL)
        for b in self.city_btns: b.config(state=tk.NORMAL)
"""

with open("monopoly_logic.py", "w", encoding="utf-8") as f:
    f.write(logic_content)
    
with open("monopoly_ui.py", "w", encoding="utf-8") as f:
    f.write(ui_content)

print("Rewrote successfully!")

