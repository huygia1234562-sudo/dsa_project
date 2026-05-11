import tkinter as tk
from tkinter import messagebox
import time
import random

class TypingRaceDialog(tk.Toplevel):
    """
    Minigame: Turn-Based Typing Race (Time Attack).
    DSA Technique: Knuth-Morris-Pratt (KMP) Pattern Matching.
    Calculates who has the fastest time to grant them the first-move advantage!
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Typing Time Attack (KMP)")
        self.geometry("650x300")
        self.resizable(False, False)
        self.callback = callback
        
        # Modal dialog locks the main window
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        
        self.sentences = [
            "Tạ Cao Nguyên Bảo đẹp trai nhất thế giới",
            "idk what to type here just placeholder sentences hihi",
            "Tôi yêu Huế, Huế là nơi tuyệt vời nhất"
            "PDLAB is all you need I love PDLAB"
        ]
        self.target_sentence = random.choice(self.sentences)
        self.current_player = 1
        self.p1_time = 0
        self.p2_time = 0
        self.start_time = 0
        
        self.info_label = tk.Label(self, text="Player 1: Get Ready!", font=("Arial", 16, "bold"), fg="blue")
        self.info_label.pack(pady=15)
        
        self.sentence_label = tk.Label(self, text=self.target_sentence, font=("Arial", 16, "italic"))
        self.sentence_label.pack(pady=10)
        
        self.entry = tk.Entry(self, font=("Arial", 16), width=45)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.check_typing)
        self.entry.config(state="disabled")
        
        self.start_btn = tk.Button(self, text="Start Typing (Player 1)", font=("Arial", 14), bg="#e0f0d9", command=self.start_turn)
        self.start_btn.pack(pady=10)

    def start_turn(self):
        self.start_btn.config(state="disabled")
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.focus()
        self.start_time = time.time()
        self.info_label.config(text=f"Player {self.current_player}: Type the sentence and hit Enter!", fg="black")
        
    def check_typing(self, event):
        typed_text = self.entry.get()
        
        # DSA Technique: KMP Algorithm for Exact Pattern Matching
        if self.kmp_exact_match(typed_text, self.target_sentence):
            elapsed = time.time() - self.start_time
            if self.current_player == 1:
                self.p1_time = elapsed
                self.current_player = 2
                self.target_sentence = random.choice(self.sentences)
                self.sentence_label.config(text=self.target_sentence)
                self.info_label.config(text=f"P1 finished in {self.p1_time:.2f}s! Player 2: Get Ready!", fg="red")
                self.start_btn.config(text="Start Typing (Player 2)", state="normal", bg="#f5c6cb")
                self.entry.delete(0, tk.END)
                self.entry.config(state="disabled")
            else:
                self.p2_time = elapsed
                winner = 1 if self.p1_time < self.p2_time else 2
                messagebox.showinfo("Race Over", f"Player 1: {self.p1_time:.2f}s\nPlayer 2: {self.p2_time:.2f}s\n\nPlayer {winner} wins the advantage and goes first!", parent=self)
                self.callback(winner)
                self.destroy()
        else:
            self.info_label.config(text="Typo detected! Match it perfectly!", fg="red")

    def kmp_exact_match(self, txt, pat):
        """
        Implementation of the Knuth-Morris-Pratt Algorithm to check if the typed text 
        exactly matches the target pattern.
        """
        if len(txt) != len(pat):
            return False
            
        M = len(pat)
        N = len(txt)
        lps = [0] * M
        
        # Calculate LPS (Longest Proper Prefix which is also Suffix) Array
        length = 0
        lps[0] = 0
        i = 1
        while i < M:
            if pat[i] == pat[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
                    
        # KMP Search
        i = 0 # index for txt
        j = 0 # index for pat
        while i < N:
            if pat[j] == txt[i]:
                i += 1
                j += 1
            if j == M:
                return True
            elif i < N and pat[j] != txt[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
                    
        return False


class PingPongDialog(tk.Toplevel):
    """
    Minigame: Classic Ping Pong
    DSA Technique: AABB (Axis-Aligned Bounding Box) Collision Detection.
    Player 1 (W/S) vs Player 2 (Up/Down). First to 3 points goes first!
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Ping Pong Sprint")
        self.geometry("600x530")
        self.resizable(False, False)
        self.callback = callback
        
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        
        self.p1_score = 0
        self.p2_score = 0
        self.target_score = 3
        
        self.info_label = tk.Label(self, text="First to 3 wins! P1: W/S  |  P2: Up/Down", font=("Arial", 14, "bold"), fg="purple")
        self.info_label.pack(pady=5)
        
        self.score_label = tk.Label(self, text="0 - 0", font=("Arial", 20, "bold"))
        self.score_label.pack(pady=5)
        
        self.canvas = tk.Canvas(self, width=600, height=350, bg="black")
        self.canvas.pack()
        
        # Game Entities
        self.paddle_w, self.paddle_h = 10, 70
        self.p1_y = 140
        self.p2_y = 140
        
        self.ball_x, self.ball_y = 295, 170
        self.ball_size = 10
        self.ball_dx = random.choice([-5, 5])
        self.ball_dy = random.choice([-3, 3])
        
        # Movement Dictionary for smooth controls
        self.keys = {'w': False, 's': False, 'Up': False, 'Down': False}
        
        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)
        
        self.start_btn = tk.Button(self, text="Start Match", font=("Arial", 14, "bold"), bg="#e0f0d9", command=self.start_game)
        self.start_btn.pack(pady=5)
        
        self.running = False
        self.draw_initial_state()

    def draw_initial_state(self):
        self.canvas.delete("all")
        self.canvas.create_line(300, 0, 300, 350, dash=(10, 10), fill="white")
        self.canvas.create_rectangle(30, self.p1_y, 30 + self.paddle_w, self.p1_y + self.paddle_h, fill="#00a8ff")
        self.canvas.create_rectangle(570 - self.paddle_w, self.p2_y, 570, self.p2_y + self.paddle_h, fill="#ff4757")
        self.canvas.create_oval(self.ball_x, self.ball_y, self.ball_x + self.ball_size, self.ball_y + self.ball_size, fill="#feca57")

    def start_game(self):
        self.start_btn.config(state="disabled")
        self.running = True
        self.update_game()

    def key_press(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = True

    def key_release(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = False

    def update_game(self):
        if not self.running:
            return
            
        paddle_speed = 6
        
        # Player 1 Movement
        if self.keys['w'] and self.p1_y > 0:
            self.p1_y -= paddle_speed
        if self.keys['s'] and self.p1_y < 350 - self.paddle_h:
            self.p1_y += paddle_speed
            
        # Player 2 Movement
        if self.keys['Up'] and self.p2_y > 0:
            self.p2_y -= paddle_speed
        if self.keys['Down'] and self.p2_y < 350 - self.paddle_h:
            self.p2_y += paddle_speed
            
        # Ball Movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ceiling / Floor Collision
        if self.ball_y <= 0 or self.ball_y >= 350 - self.ball_size:
            self.ball_dy *= -1
            
        # AABB Collision: Player 1 Paddle
        if self.ball_x <= 30 + self.paddle_w:
            if self.p1_y < self.ball_y + self.ball_size and self.p1_y + self.paddle_h > self.ball_y:
                self.ball_dx = abs(self.ball_dx) + 0.5  # Speed up slightly
                self.ball_x = 30 + self.paddle_w
                
        # AABB Collision: Player 2 Paddle
        if self.ball_x >= 570 - self.paddle_w - self.ball_size:
            if self.p2_y < self.ball_y + self.ball_size and self.p2_y + self.paddle_h > self.ball_y:
                self.ball_dx = -abs(self.ball_dx) - 0.5
                self.ball_x = 570 - self.paddle_w - self.ball_size
                
        # Scoring
        if self.ball_x < 0:
            self.p2_score += 1
            self.reset_ball(-5)
        elif self.ball_x > 600:
            self.p1_score += 1
            self.reset_ball(5)
            
        self.score_label.config(text=f"{self.p1_score} - {self.p2_score}")
        
        # Redraw 
        self.canvas.delete("all")
        # Dashed middle line
        self.canvas.create_line(300, 0, 300, 350, dash=(10, 10), fill="white")
        # Paddles & Ball
        self.canvas.create_rectangle(30, self.p1_y, 30 + self.paddle_w, self.p1_y + self.paddle_h, fill="#00a8ff")
        self.canvas.create_rectangle(570 - self.paddle_w, self.p2_y, 570, self.p2_y + self.paddle_h, fill="#ff4757")
        self.canvas.create_oval(self.ball_x, self.ball_y, self.ball_x + self.ball_size, self.ball_y + self.ball_size, fill="#feca57")
        
        if self.p1_score >= self.target_score or self.p2_score >= self.target_score:
            self.running = False
            winner = 1 if self.p1_score > self.p2_score else 2
            messagebox.showinfo("Ping Pong Over!", f"Player {winner} dominated the Pong match!\nThey get to place the first piece.", parent=self)
            self.callback(winner)
            self.destroy()
        else:
            self.after(16, self.update_game) # 60 FPS loop
            
    def reset_ball(self, dir_x):
        self.ball_x, self.ball_y = 295, 170
        self.ball_dx = dir_x
        self.ball_dy = random.choice([-3, 3])


class QuickMathDialog(tk.Toplevel):
    """
    Minigame: Quick Math Speedrun
    DSA Technique: Reverse Polish Notation (RPN) Expression Generator & Evaluator 
    to robustly create random math expressions without parenthesis parsing errors.
    Player 1 vs Player 2: Fastest time to evaluate the Math expression wins!
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Quick Math RPN Race")
        self.geometry("600x400")
        self.resizable(False, False)
        self.callback = callback
        
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.p1_time = 0.0
        self.p2_time = 0.0
        self.current_player = 1
        self.start_time = 0.0
        
        # Generation State
        self.current_expr = ""
        self.current_ans = 0
        
        self.info_label = tk.Label(self, text="Quick Math - Player 1's Turn!", font=("Arial", 16, "bold"), fg="#2980b9")
        self.info_label.pack(pady=20)
        
        self.math_label = tk.Label(self, text="[Press Start to Generate Math]", font=("Courier", 24, "bold"), bg="#f1c40f", padx=20, pady=10)
        self.math_label.pack(pady=10)
        
        self.entry = tk.Entry(self, font=("Arial", 20), width=10, justify="center")
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.check_answer)
        self.entry.config(state="disabled")
        
        self.start_btn = tk.Button(self, text="Start Timer (Player 1)", font=("Arial", 14, "bold"), bg="#d4edda", command=self.start_race)
        self.start_btn.pack(pady=20)

    def generate_rpn_expression(self, length=7):
        """Generates a random valid RPN sequence and calculates infix + answer"""
        ops = ['+', '-', '*']
        expression = []
        num_count = 0
        op_count = 0
        target_nums = (length + 1) // 2
        
        while num_count + op_count < length:
            can_add_num = num_count < target_nums
            can_add_op = (num_count - op_count) >= 2 and op_count < target_nums - 1
            
            choices = []
            if can_add_num: choices.append('num')
            if can_add_op: choices.append('op')
            
            choice = random.choice(choices)
            if choice == 'num':
                expression.append(str(random.randint(1, 9)))
                num_count += 1
            else:
                expression.append(random.choice(ops))
                op_count += 1
                
        # Evaluate & Convert to Infix
        eval_stack = []
        str_stack = []
        for token in expression:
            if token in ops:
                b_val = eval_stack.pop()
                a_val = eval_stack.pop()
                b_str = str_stack.pop()
                a_str = str_stack.pop()
                
                if token == '+': eval_stack.append(a_val + b_val)
                elif token == '-': eval_stack.append(a_val - b_val)
                elif token == '*': eval_stack.append(a_val * b_val)
                
                str_stack.append(f"({a_str} {token} {b_str})")
            else:
                eval_stack.append(int(token))
                str_stack.append(token)
                
        return str_stack[0], eval_stack[0]

    def start_race(self):
        self.start_btn.config(state="disabled")
        
        infix_str, answer = self.generate_rpn_expression(length=5)
        self.current_expr = infix_str
        self.current_ans = answer
        
        self.math_label.config(text=f"Solve: {self.current_expr} = ?")
        self.entry.config(state="normal")
        self.entry.focus_set()
        
        self.start_time = time.time()
        self.info_label.config(text=f"Player {self.current_player}, GO!", fg="green")

    def check_answer(self, event):
        user_input = self.entry.get().strip()
        try:
            val = int(user_input)
        except ValueError:
            self.info_label.config(text="Numbers only! Try again!", fg="red")
            return
            
        if val == self.current_ans:
            elapsed = time.time() - self.start_time
            if self.current_player == 1:
                self.p1_time = elapsed
                self.current_player = 2
                self.info_label.config(text=f"P1 Time: {self.p1_time:.2f}s. Player 2's Turn!", fg="#c0392b")
                self.math_label.config(text="[Press Start to Generate Math]")
                self.start_btn.config(text="Start Timer (Player 2)", state="normal", bg="#f5c6cb")
                self.entry.delete(0, tk.END)
                self.entry.config(state="disabled")
            else:
                self.p2_time = elapsed
                winner = 1 if self.p1_time < self.p2_time else 2
                messagebox.showinfo("Race Over", f"Player 1: {self.p1_time:.2f}s\nPlayer 2: {self.p2_time:.2f}s\n\nPlayer {winner} wins the advantage and goes first!", parent=self)
                self.callback(winner)
                self.destroy()
        else:
            self.info_label.config(text=f"Wrong! Answer was {self.current_ans}. Generating new...", fg="red")
            self.entry.delete(0, tk.END)
            # Penalty: Generate new math for them!
            new_str, new_ans = self.generate_rpn_expression(length=5)
            self.current_expr = new_str
            self.current_ans = new_ans
            self.math_label.config(text=f"Solve: {self.current_expr} = ?")


class CoinCatcherDialog(tk.Toplevel):
    """
    Minigame: Coin Catcher Arcade
    DSA Technique: 1D Array Sliding Window / Coordinate Math
    Player 1 (A/D) vs Player 2 (Left/Right). Catch falling objects!
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Coin Catcher")
        self.geometry("600x530")
        self.resizable(False, False)
        self.callback = callback
        
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        
        self.p1_score = 0
        self.p2_score = 0
        self.target_score = 10
        
        self.info_label = tk.Label(self, text="First to catch 10 Coins! P1: [A][D]  |  P2: [<][>]", font=("Arial", 14, "bold"), fg="darkorange")
        self.info_label.pack(pady=5)
        
        self.score_label = tk.Label(self, text="0 - 0", font=("Arial", 20, "bold"), fg="black")
        self.score_label.pack(pady=5)
        
        self.canvas = tk.Canvas(self, width=600, height=350, bg="#2c3e50")
        self.canvas.pack()
        
        # Baskets
        self.basket_w = 60
        self.basket_h = 20
        self.p1_x = 150
        self.p2_x = 400
        self.basket_y = 330
        
        # Falling Objects
        self.coins = []
        self.coin_speed = 5
        
        # Movement Trackers
        self.keys = {'a': False, 'd': False, 'Left': False, 'Right': False}
        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)
        
        self.start_btn = tk.Button(self, text="Start Catching", font=("Arial", 14, "bold"), bg="#e0f0d9", command=self.start_game)
        self.start_btn.pack(pady=5)
        
        self.running = False
        self.draw_frame()

    def start_game(self):
        self.start_btn.config(state="disabled")
        self.running = True
        self.update_game()

    def key_press(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = True

    def key_release(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = False

    def draw_frame(self):
        self.canvas.delete("all")
        # P1 Basket
        self.canvas.create_rectangle(self.p1_x, self.basket_y, self.p1_x + self.basket_w, self.basket_y + self.basket_h, fill="#00a8ff")
        self.canvas.create_text(self.p1_x + self.basket_w//2, self.basket_y + 10, text="P1", fill="white", font=("Arial", 10, "bold"))
        # P2 Basket
        self.canvas.create_rectangle(self.p2_x, self.basket_y, self.p2_x + self.basket_w, self.basket_y + self.basket_h, fill="#ff4757")
        self.canvas.create_text(self.p2_x + self.basket_w//2, self.basket_y + 10, text="P2", fill="white", font=("Arial", 10, "bold"))
        
        # Draw Coins
        for coin in self.coins:
            cx, cy = coin['x'], coin['y']
            self.canvas.create_oval(cx, cy, cx + 15, cy + 15, fill="#f1c40f", outline="#f39c12", width=2)
            self.canvas.create_text(cx + 7, cy + 7, text="$", fill="black", font=("Arial", 8, "bold"))

    def update_game(self):
        if not self.running:
            return
            
        paddle_speed = 8
        
        # Physics movement
        if self.keys['a'] and self.p1_x > 0:
            self.p1_x -= paddle_speed
        if self.keys['d'] and self.p1_x < 600 - self.basket_w:
            self.p1_x += paddle_speed
            
        if self.keys['Left'] and self.p2_x > 0:
            self.p2_x -= paddle_speed
        if self.keys['Right'] and self.p2_x < 600 - self.basket_w:
            self.p2_x += paddle_speed

        # RNG Coin Spawning (10% chance per frame to drop a coin)
        if random.random() < 0.10:
            self.coins.append({'x': random.randint(10, 580), 'y': 0})
            
        # Update coins and check bounding boxes
        active_coins = []
        for coin in self.coins:
            coin['y'] += self.coin_speed
            cx, cy = coin['x'], coin['y']
            
            # P1 Catch Collision
            if (self.p1_x < cx + 15 and self.p1_x + self.basket_w > cx and
                self.basket_y < cy + 15 and self.basket_y + self.basket_h > cy):
                self.p1_score += 1
            # P2 Catch Collision
            elif (self.p2_x < cx + 15 and self.p2_x + self.basket_w > cx and
                  self.basket_y < cy + 15 and self.basket_y + self.basket_h > cy):
                self.p2_score += 1
            # Still falling and not off screen
            elif cy < 360:
                active_coins.append(coin)
                
        self.coins = active_coins
        self.score_label.config(text=f"{self.p1_score} - {self.p2_score}")
        
        self.draw_frame()
        
        # Check Win Conditions
        if self.p1_score >= self.target_score or self.p2_score >= self.target_score:
            self.running = False
            winner = 1 if self.p1_score >= self.target_score else 2
            messagebox.showinfo("Coin Catcher Over!", f"Player {winner} grabbed 10 coins first!\nThey get to place the piece.", parent=self)
            self.callback(winner)
            self.destroy()
        else:
            self.after(16, self.update_game) # 60 FPS Loop


class MemoryCardDialog(tk.Toplevel):
    """
    Minigame: Memory Card Match
    DSA Technique: Hash Maps ($O(1)$ state tracking) & Fisher-Yates Array Shuffling.
    Player 1 against Player 2. Take turns flipping pairs. Most pairs wins!
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Memory Card Match")
        self.geometry("600x550")
        self.resizable(False, False)
        self.callback = callback
        
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        
        self.p1_pairs = 0
        self.p2_pairs = 0
        self.current_player = 1
        
        self.info_label = tk.Label(self, text="Player 1's Turn", font=("Arial", 16, "bold"), fg="blue")
        self.info_label.pack(pady=10)
         
        self.score_label = tk.Label(self, text="P1: 0  |  P2: 0", font=("Arial", 14, "bold"))
        self.score_label.pack(pady=5)
        
        # O(1) State Tracking via Hash Map
        self.cards_state = {} 
        self.flipped_cards = []
        self.lock_board = False
        
        self.canvas = tk.Canvas(self, width=500, height=400, bg="#eaf2f8")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)
        
        self.init_cards()
        self.draw_board()

    def fisher_yates_shuffle(self, arr):
        """Standard Fisher-Yates O(N) array shuffle"""
        for i in range(len(arr) - 1, 0, -1):
            j = random.randint(0, i)
            arr[i], arr[j] = arr[j], arr[i]
        return arr

    def init_cards(self):
        # 16 cards total / 8 pairs (A-H)
        symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] * 2
        self.fisher_yates_shuffle(symbols)
        
        card_w, card_h = 100, 80
        padding = 20
        start_x, start_y = \
            (500 - (4*card_w + 3*padding)) // 2, \
            (400 - (4*card_h + 3*padding)) // 2
        
        card_id = 0
        for row in range(4):
            for col in range(4):
                x = start_x + col * (card_w + padding)
                y = start_y + row * (card_h + padding)
                
                # Hash Map storage for O(1) metadata access
                self.cards_state[card_id] = {
                    'x': x, 'y': y,
                    'w': card_w, 'h': card_h,
                    'symbol': symbols[card_id],
                    'flipped': False,
                    'matched': False
                }
                card_id += 1

    def draw_board(self):
        self.canvas.delete("all")
        for cid, state in self.cards_state.items():
            x, y, w, h = state['x'], state['y'], state['w'], state['h']
            
            if state['matched']:
                self.canvas.create_rectangle(x, y, x+w, y+h, fill="#d4edda", outline="gray")
                self.canvas.create_text(x+w//2, y+h//2, text=state['symbol'], font=("Arial", 20, "bold"), fill="gray")
            elif state['flipped']:
                self.canvas.create_rectangle(x, y, x+w, y+h, fill="white", outline="black")
                self.canvas.create_text(x+w//2, y+h//2, text=state['symbol'], font=("Arial", 20, "bold"))
            else:
                self.canvas.create_rectangle(x, y, x+w, y+h, fill="#3498db", outline="black")
                self.canvas.create_text(x+w//2, y+h//2, text="?", font=("Arial", 20, "bold"), fill="white")

    def handle_click(self, event):
        if self.lock_board:
            return
            
        ex, ey = event.x, event.y
        # Look up bounding box
        clicked_id = None
        for cid, state in self.cards_state.items():
            if state['matched'] or state['flipped']:
                continue
            if state['x'] <= ex <= state['x'] + state['w'] and state['y'] <= ey <= state['y'] + state['h']:
                clicked_id = cid
                break
                
        if clicked_id is not None:
            self.cards_state[clicked_id]['flipped'] = True
            self.flipped_cards.append(clicked_id)
            self.draw_board()
            
            if len(self.flipped_cards) == 2:
                self.lock_board = True
                self.after(800, self.check_match)

    def check_match(self):
        id1, id2 = self.flipped_cards
        c1, c2 = self.cards_state[id1], self.cards_state[id2]
        
        if c1['symbol'] == c2['symbol']:
            c1['matched'] = True
            c2['matched'] = True
            if self.current_player == 1:
                self.p1_pairs += 1
            else:
                self.p2_pairs += 1
                
            # Current player gets to go again!
        else:
            c1['flipped'] = False
            c2['flipped'] = False
            # Switch turns
            self.current_player = 2 if self.current_player == 1 else 1
            self.info_label.config(text=f"Player {self.current_player}'s Turn", fg="blue" if self.current_player == 1 else "red")
            
        self.score_label.config(text=f"P1: {self.p1_pairs}  |  P2: {self.p2_pairs}")
        self.flipped_cards.clear()
        self.draw_board()
        self.lock_board = False
        
        if self.p1_pairs + self.p2_pairs == 8:
            winner = 1 if self.p1_pairs > self.p2_pairs else (2 if self.p2_pairs > self.p1_pairs else random.choice([1,2]))
            messagebox.showinfo("Memory Card Over!", f"Player {winner} got the most pairs!\nThey get to place the piece.", parent=self)
            self.callback(winner)
            self.destroy()


class PacmanDialog(tk.Toplevel):
    """
    Minigame: 2-Player Pacman Dot Rush (Survival)
    DSA Technique: BFS (Breadth-First Search) Graph Traversal for Ghost Pathfinding.
    Player 1 (WASD) vs Player 2 (Arrows). The monsters use BFS to chase the players!
    30 Second Timer. If a player is caught or time ends, the highest score wins.
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Pacman BFS Escape")
        # Bigger map requires bigger window
        self.geometry("600x650")
        self.resizable(False, False)
        self.callback = callback
        
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        
        self.p1_score = 0
        self.p2_score = 0
        self.time_left = 30
        self.running = True
        
        self.info_label = tk.Label(self, text="Eat dots! Evade Ghosts! P1: WASD | P2: Arrows", font=("Arial", 12, "bold"), fg="purple")
        self.info_label.pack(pady=5)
        
        self.score_label = tk.Label(self, text=f"Time: {self.time_left}s | P1: 0   -   P2: 0", font=("Arial", 16, "bold"))
        self.score_label.pack(pady=5)
        
        # 21x21 Grid, 25px per cell
        self.cell_size = 25
        self.canvas = tk.Canvas(self, width=21*self.cell_size, height=21*self.cell_size, bg="black")
        self.canvas.pack()
        
        # 0 = Dot, 1 = Wall, 2 = Empty
        self.map_data = [
            [1]*21,
            [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1],
            [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1],
            [1,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
            [1,1,1,1,1,0,1,1,1,2,1,2,1,1,1,0,1,1,1,1,1],
            [2,2,2,2,1,0,1,2,2,2,2,2,2,2,1,0,1,2,2,2,2],
            [1,1,1,1,1,0,1,2,1,1,2,1,1,2,1,0,1,1,1,1,1],
            [2,2,2,2,2,0,2,2,1,2,2,2,1,2,2,0,2,2,2,2,2],
            [1,1,1,1,1,0,1,2,1,1,1,1,1,2,1,0,1,1,1,1,1],
            [2,2,2,2,1,0,1,2,2,2,2,2,2,2,1,0,1,2,2,2,2],
            [1,1,1,1,1,0,1,2,1,1,1,1,1,2,1,0,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1,1],
            [1,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1]*21
        ]
        
        # Player Positions (Row, Col)
        self.p1_pos = [1, 1]
        self.p2_pos = [19, 19]

        # Monster Positions (Row, Col) - Spaawning in the middle box
        self.ghost1_pos = [10, 9]  # Chases P1
        self.ghost2_pos = [10, 11] # Chases P2
        
        self.keys = {'w':False, 'a':False, 's':False, 'd':False, 'Up':False, 'Left':False, 'Down':False, 'Right':False}
        self.bind("<KeyPress>", self.key_press)
        
        self.draw_map()
        self.draw_entities()
        
        # Start timers and AI loops
        self.update_timer()
        self.move_ghosts()

    def update_timer(self):
        if not self.running: return
        self.time_left -= 1
        self.update_score_display()
        
        if self.time_left <= 0:
            self.end_game("Time's Up!")
        else:
            self.after(1000, self.update_timer)

    def update_score_display(self):
        self.score_label.config(text=f"Time: {self.time_left}s | P1: {self.p1_score}   -   P2: {self.p2_score}")

    def get_bfs_next_step(self, start, target):
        """
        DSA Technique: Breadth-First Search (BFS) to find the shortest path 
        for monsters to chase the players through the 2D grid matrix.
        """
        from collections import deque
        
        queue = deque([(start[0], start[1], [])])
        visited = set()
        visited.add((start[0], start[1]))
        
        while queue:
            r, c, path = queue.popleft()
            
            # If we reached the target, take the first step of the path
            if [r, c] == target:
                if len(path) > 0:
                    return path[0]
                return start
                
            # Expand to 4 directions
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r + dr, c + dc
                
                # Check mapping bounds & walls (with tunnel wrap-around handling)
                if nr < 0: nr = 20
                elif nr > 20: nr = 0
                if nc < 0: nc = 20
                elif nc > 20: nc = 0
                
                if self.map_data[nr][nc] != 1 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc, path + [[nr, nc]]))
                    
        return start # No path available
        
    def move_ghosts(self):
        if not self.running: return
        
        # Ghost 1 tracks Player 1, Ghost 2 tracks Player 2 using BFS
        self.ghost1_pos = self.get_bfs_next_step(self.ghost1_pos, self.p1_pos)
        self.ghost2_pos = self.get_bfs_next_step(self.ghost2_pos, self.p2_pos)
        
        self.draw_entities()
        self.check_collision()
        
        if self.running:
            self.after(400, self.move_ghosts) # Monsters move every 0.4s
        
    def key_press(self, event):
        if not self.running: return
        sym = event.keysym
        
        # P1 Movement (WASD)
        if sym in ['w', 'a', 's', 'd']:
            new_r, new_c = self.p1_pos[0], self.p1_pos[1]
            if sym == 'w': new_r -= 1
            if sym == 's': new_r += 1
            if sym == 'a': new_c -= 1
            if sym == 'd': new_c += 1
            
            self.handle_player_move(1, new_r, new_c)
                
        # P2 Movement (Arrows)
        elif sym in ['Up', 'Down', 'Left', 'Right']:
            new_r, new_c = self.p2_pos[0], self.p2_pos[1]
            if sym == 'Up': new_r -= 1
            if sym == 'Down': new_r += 1
            if sym == 'Left': new_c -= 1
            if sym == 'Right': new_c += 1
            
            self.handle_player_move(2, new_r, new_c)
            
        self.draw_entities()
        self.check_collision()
        
    def handle_player_move(self, player_id, new_r, new_c):
        # Wrap around grid (Tunnels on the edge)
        if new_r < 0: new_r = 20
        elif new_r > 20: new_r = 0
        if new_c < 0: new_c = 20
        elif new_c > 20: new_c = 0
        
        if self.map_data[new_r][new_c] != 1:
            if player_id == 1:
                self.p1_pos = [new_r, new_c]
            else:
                self.p2_pos = [new_r, new_c]
            self.check_eat(player_id, new_r, new_c)
        
    def check_eat(self, player, r, c):
        if self.map_data[r][c] == 0:
            self.map_data[r][c] = 2 # Mark empty
            if player == 1: self.p1_score += 1
            else: self.p2_score += 1
            self.update_score_display()
            self.draw_map() # Force map redraw to clear the dot visually

    def check_collision(self):
        if self.ghost1_pos == self.p1_pos or self.ghost2_pos == self.p1_pos:
            self.end_game("Player 1 was caught by a Ghost!")
        elif self.ghost1_pos == self.p2_pos or self.ghost2_pos == self.p2_pos:
            self.end_game("Player 2 was caught by a Ghost!")

    def end_game(self, reason):
        self.running = False
        # Calculate Winner: Highest score wins, tie goes to random
        winner = 1 if self.p1_score > self.p2_score else (2 if self.p2_score > self.p1_score else random.choice([1, 2]))
        messagebox.showinfo("Game Over", f"{reason}\n\nPlayer 1: {self.p1_score} dots\nPlayer 2: {self.p2_score} dots\n\nPlayer {winner} wins and steals the turn!", parent=self)
        self.callback(winner)
        self.destroy()

    def draw_map(self):
        self.canvas.delete("map")
        for r in range(21):
            for c in range(21):
                val = self.map_data[r][c]
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if val == 1: # Wall
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1e272e", outline="#34495e", tags="map")
                elif val == 0: # Dot
                    cx, cy = x1 + self.cell_size//2, y1 + self.cell_size//2
                    self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill="#f1c40f", tags="map")

    def draw_entities(self):
        self.canvas.delete("entity")
        
        # Ghost 1 (Magenta - targets P1)
        g1_x = self.ghost1_pos[1] * self.cell_size
        g1_y = self.ghost1_pos[0] * self.cell_size
        self.canvas.create_rectangle(g1_x+2, g1_y+2, g1_x+self.cell_size-2, g1_y+self.cell_size-2, fill="magenta", outline="white", tags="entity")
        
        # Ghost 2 (Cyan - targets P2)
        g2_x = self.ghost2_pos[1] * self.cell_size
        g2_y = self.ghost2_pos[0] * self.cell_size
        self.canvas.create_rectangle(g2_x+2, g2_y+2, g2_x+self.cell_size-2, g2_y+self.cell_size-2, fill="cyan", outline="white", tags="entity")
        
        # P1 (Blue Pacman)
        p1_x = self.p1_pos[1] * self.cell_size
        p1_y = self.p1_pos[0] * self.cell_size
        self.canvas.create_arc(p1_x+2, p1_y+2, p1_x+self.cell_size-2, p1_y+self.cell_size-2, start=30, extent=300, fill="#00a8ff", tags="entity")
        
        # P2 (Red Pacman)
        p2_x = self.p2_pos[1] * self.cell_size
        p2_y = self.p2_pos[0] * self.cell_size
        self.canvas.create_arc(p2_x+2, p2_y+2, p2_x+self.cell_size-2, p2_y+self.cell_size-2, start=210, extent=300, fill="#ff4757", tags="entity")


class ChickenCrossDialog(tk.Toplevel):
    """
    Minigame: Chicken Cross the Road (Frogger style)
    DSA Technique: Circular Queues (using collections.deque) / Object Pooling.
    Instead of constantly creating and destroying car objects (which leaks memory),
    we use a Double-Ended Queue. When a car goes off-screen, it is popped from 
    the front of the Queue and recycled into the back of the Queue!
    Player 1 (WASD) vs Player 2 (Arrows). First to the Top Safe Zone wins!
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Chicken Cross (Circular Queue)")
        self.geometry("600x550")
        self.resizable(False, False)
        self.callback = callback
        
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.info_label = tk.Label(self, text="Race to the Top! Dodge Cars!\nP1: WASD | P2: Arrows", font=("Arial", 12, "bold"), fg="darkgreen")
        self.info_label.pack(pady=5)

        self.canvas = tk.Canvas(self, width=600, height=450, bg="#2ecc71")  # Green grass background
        self.canvas.pack()

        # Players
        self.p1_pos = [200, 420]
        self.p2_pos = [400, 420]
        self.player_size = 20
        self.move_dist = 25

        # Circular Queues (Deques) for Object Pooling the cars in each lane
        from collections import deque
        self.lanes = []
        
        # Lane config: y_pos, speed (positive=right, negative=left), colors
        lane_configs = [
            (360, 4, "red"),
            (320, -5, "blue"),
            (280, 6, "purple"),
            (240, -4, "orange"),
            (200, 7, "black"),
            (160, -6, "white"),
            (120, 8, "darkred")
        ]

        for y, speed, color in lane_configs:
            # Each lane gets a deque queue of recycled car dictionaries
            q = deque()
            # Spread 3 cars in the queue initially
            for x_offset in [0, 200, 400]:
                q.append({"x": x_offset, "y": y, "w": 40, "h": 20, "speed": speed, "color": color})
            self.lanes.append(q)

        self.running = True
        self.bind("<KeyPress>", self.key_press)
        
        self.draw_frame()
        self.game_loop()

    def key_press(self, event):
        if not self.running: return
        sym = event.keysym
        
        # P1 Movement
        if sym in ['w', 'a', 's', 'd']:
            if sym == 'w': self.p1_pos[1] -= self.move_dist
            elif sym == 's' and self.p1_pos[1] < 430: self.p1_pos[1] += self.move_dist
            elif sym == 'a' and self.p1_pos[0] > 0: self.p1_pos[0] -= self.move_dist
            elif sym == 'd' and self.p1_pos[0] < 580: self.p1_pos[0] += self.move_dist
                
        # P2 Movement
        elif sym in ['Up', 'Down', 'Left', 'Right']:
            if sym == 'Up': self.p2_pos[1] -= self.move_dist
            elif sym == 'Down' and self.p2_pos[1] < 430: self.p2_pos[1] += self.move_dist
            elif sym == 'Left' and self.p2_pos[0] > 0: self.p2_pos[0] -= self.move_dist
            elif sym == 'Right' and self.p2_pos[0] < 580: self.p2_pos[0] += self.move_dist
            
        self.check_win()

    def check_win(self):
        # Top safe zone is y < 80
        if self.p1_pos[1] < 80:
            self.end_game(1)
        elif self.p2_pos[1] < 80:
            self.end_game(2)

    def draw_frame(self):
        self.canvas.delete("all")
        
        # Draw roads (gray backgrounds behind the car queues)
        self.canvas.create_rectangle(0, 110, 600, 390, fill="#7f8c8d", outline="")
        
        # Draw Top Safe Zone / Finish Line
        self.canvas.create_rectangle(0, 0, 600, 80, fill="#f1c40f", outline="")
        self.canvas.create_text(300, 40, text="FINISH LINE", font=("Arial", 20, "bold"), fill="black")
        
        # Draw Start Zone
        self.canvas.create_text(300, 435, text="START ZONE", font=("Arial", 16, "bold"), fill="#27ae60")

        # Draw Cars from Circular Queues
        for lane_q in self.lanes:
            for car in lane_q:
                cx, cy, cw, ch = car["x"], car["y"], car["w"], car["h"]
                self.canvas.create_rectangle(cx, cy, cx+cw, cy+ch, fill=car["color"], outline="white")

        # Draw P1 (Blue Chicken)
        px1, py1 = self.p1_pos
        self.canvas.create_oval(px1, py1, px1+self.player_size, py1+self.player_size, fill="#00a8ff", outline="white", width=2)
        
        # Draw P2 (Red Chicken)
        px2, py2 = self.p2_pos
        self.canvas.create_oval(px2, py2, px2+self.player_size, py2+self.player_size, fill="#ff4757", outline="white", width=2)

    def game_loop(self):
        if not self.running: return

        # Update Queues (Object Pooling Logic)
        for lane_q in self.lanes:
            for i in range(len(lane_q)):
                car = lane_q[i]
                car["x"] += car["speed"]
                
                # O(1) Queue Modulo wrapping (If car goes off screen, wrap around)
                if car["speed"] > 0 and car["x"] > 600:
                    car["x"] = -40
                elif car["speed"] < 0 and car["x"] < -40:
                    car["x"] = 600
                
                # Collision Check
                if self.check_collision(self.p1_pos, car):
                    self.p1_pos = [200, 420] # Reset to start zone
                if self.check_collision(self.p2_pos, car):
                    self.p2_pos = [400, 420] # Reset to start zone

        self.draw_frame()
        self.after(30, self.game_loop) # Loop ~33 FPS

    def check_collision(self, player_pos, car):
        px, py = player_pos
        cx, cy, cw, ch = car["x"], car["y"], car["w"], car["h"]
        # Basic AABB collision
        return (px < cx + cw and px + self.player_size > cx and
                py < cy + ch and py + self.player_size > cy)
                
    def end_game(self, winner):
        self.running = False
        messagebox.showinfo("Chicken Cross Winner!", f"Player {winner} successfully crossed the road first!\nThey steal the Gomoku turn!", parent=self)
        self.callback(winner)
        self.destroy()


class MazeEscapeDialog(tk.Toplevel):
    """
    Minigame: Maze Escape Race
    DSA Technique: Depth-First Search (DFS) for Randomized Maze Generation
    Players race to the yellow finish zone at the bottom!
    """
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Maze Escape Race! (DFS Generation)")
        self.geometry("600x650")
        self.resizable(False, False)
        self.callback = callback
        
        self.grab_set()
        
        self.cols = 15
        self.rows = 15
        self.cell_size = 36
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        
        tk.Label(self, text="Race to the Yellow Exit!", font=("Arial", 14, "bold"), fg="#333").pack(pady=5)
        tk.Label(self, text="P1 (Blue): WASD   |   P2 (Red): Arrows", font=("Arial", 10)).pack()
        
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="white", highlightthickness=2, highlightbackground="black")
        self.canvas.pack(pady=10)
        
        self.running = True
        
        self.p1_pos = [0, 0]  # x, y in grid logic
        self.p2_pos = [self.cols - 1, 0]
        self.finish_pos = (self.cols // 2, self.rows - 1)
        
        # Grid format: cell(x, y) = {"N": True, "E": True, "S": True, "W": True, "visited": False}
        self.grid = [[{"N": True, "E": True, "S": True, "W": True, "visited": False} for _ in range(self.rows)] for _ in range(self.cols)]
        
        self.generate_maze_dfs()
        
        self.bind("<KeyPress>", self.handle_keypress)
        
        self.draw_maze()
        
        self.p1_id = self.canvas.create_oval(0, 0, 0, 0, fill="blue")
        self.p2_id = self.canvas.create_oval(0, 0, 0, 0, fill="red")
        
        self.update_player_visuals()

    def generate_maze_dfs(self):
        # DSA concept: randomized DFS for maze generation
        stack = []
        start_x, start_y = (0, 0)
        self.grid[start_x][start_y]["visited"] = True
        stack.append((start_x, start_y))
        
        while stack:
            cx, cy = stack[-1]
            unvisited = []
            
            # Check neighbors [x, y, dir, opposite_dir]
            neighbors = [
                (cx, cy-1, "N", "S"),
                (cx+1, cy, "E", "W"),
                (cx, cy+1, "S", "N"),
                (cx-1, cy, "W", "E")
            ]
            
            for nx, ny, wall, opp_wall in neighbors:
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    if not self.grid[nx][ny]["visited"]:
                        unvisited.append((nx, ny, wall, opp_wall))
                        
            if unvisited:
                nx, ny, wall, opp_wall = random.choice(unvisited)
                self.grid[cx][cy][wall] = False
                self.grid[nx][ny][opp_wall] = False
                self.grid[nx][ny]["visited"] = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def draw_maze(self):
        self.canvas.delete("maze_items")
        cs = self.cell_size
        
        # Draw finish zone
        fx, fy = self.finish_pos
        self.canvas.create_rectangle(fx * cs, fy * cs, (fx + 1) * cs, (fy + 1) * cs, fill="#FFD700", outline="", tags="maze_items")
        self.canvas.create_text((fx + 0.5) * cs, (fy + 0.5) * cs, text="★", font=("Arial", 20), tags="maze_items")
        
        for x in range(self.cols):
            for y in range(self.rows):
                cell = self.grid[x][y]
                px1, py1 = x * cs, y * cs
                px2, py2 = px1 + cs, py1 + cs
                
                if cell["N"]: self.canvas.create_line(px1, py1, px2, py1, fill="black", width=2, tags="maze_items")
                if cell["S"]: self.canvas.create_line(px1, py2, px2, py2, fill="black", width=2, tags="maze_items")
                if cell["E"]: self.canvas.create_line(px2, py1, px2, py2, fill="black", width=2, tags="maze_items")
                if cell["W"]: self.canvas.create_line(px1, py1, px1, py2, fill="black", width=2, tags="maze_items")
                
    def update_player_visuals(self):
        cs = self.cell_size
        pad = 6
        x1, y1 = self.p1_pos
        self.canvas.coords(self.p1_id, x1*cs + pad, y1*cs + pad, (x1+1)*cs - pad, (y1+1)*cs - pad)
        
        x2, y2 = self.p2_pos
        self.canvas.coords(self.p2_id, x2*cs + pad, y2*cs + pad, (x2+1)*cs - pad, (y2+1)*cs - pad)

    def handle_keypress(self, event):
        if not self.running: return
        key = event.keysym.lower()
        
        # Player 1 (WASD)
        self.move_player(self.p1_pos, key, "w", "s", "d", "a", 1)
        # Player 2 (Arrows)
        self.move_player(self.p2_pos, key, "up", "down", "right", "left", 2)
        
        self.update_player_visuals()

    def move_player(self, pos, key, k_up, k_down, k_right, k_left, player_num):
        x, y = pos
        cell = self.grid[x][y]
        
        old_x, old_y = x, y
        if key == k_up and not cell["N"]: pos[1] -= 1
        elif key == k_down and not cell["S"]: pos[1] += 1
        elif key == k_right and not cell["E"]: pos[0] += 1
        elif key == k_left and not cell["W"]: pos[0] -= 1
        
        # Prevent going out of bounds
        pos[0] = max(0, min(self.cols - 1, pos[0]))
        pos[1] = max(0, min(self.rows - 1, pos[1]))
        
        if tuple(pos) == self.finish_pos:
            self.running = False
            self.update_player_visuals()
            messagebox.showinfo("Maze Escaped!", f"Player {player_num} escaped the maze first!\nThey steal the Gomoku turn!", parent=self)
            self.callback(player_num)
            self.destroy()




class TrieNode:
    """Node for the Trie data structure used in Word Builder minigame."""
    __slots__ = ['children', 'is_end']
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    """
    Trie (Prefix Tree) data structure.
    Supports O(L) insert and search where L = word length.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True


class WordBuilderDialog(tk.Toplevel):
    """
    Minigame: Word Builder
    DSA Technique: Trie (Prefix Tree) for O(L) word validation.
    Given random letters, players take turns typing valid English words.
    The Trie dictionary validates each word in O(L) time where L = word length.
    Player with most valid words wins!
    """
    DICTIONARY = [
        "ace","act","add","age","ago","aid","aim","air","all","and","ant","any","ape","arc","are","ark",
        "arm","art","ash","ask","ate","awe","axe","bad","bag","ban","bar","bat","bay","bed","bee","bet",
        "bid","big","bin","bit","bog","bow","box","boy","bud","bug","bun","bus","but","buy","cab","cam",
        "can","cap","car","cat","cop","cow","cry","cub","cup","cur","cut","dab","dad","dam","day","den",
        "dew","did","dig","dim","dip","doe","dog","don","dot","dry","dub","dud","due","dug","dun","duo",
        "dye","ear","eat","eel","egg","ego","elm","emu","end","era","eve","ewe","eye","fad","fan","far",
        "fat","fax","fed","fee","few","fig","fin","fir","fit","fix","fly","foe","fog","for","fox","fry",
        "fun","fur","gag","gal","gap","gas","gem","get","gin","gnu","god","got","gum","gun","gut","guy",
        "gym","had","ham","has","hat","hay","hen","her","hew","hex","hid","him","hip","his","hit","hob",
        "hoe","hog","hop","hot","how","hub","hue","hug","hum","hut","ice","icy","ill","imp","ink","inn",
        "ion","ire","irk","ivy","jab","jag","jam","jar","jaw","jay","jet","jig","job","jog","jot","joy",
        "jug","jut","keg","ken","key","kid","kin","kit","lab","lad","lag","lap","law","lay","lea","led",
        "leg","let","lid","lie","lip","lit","log","lot","low","lug","mad","man","map","mar","mat","maw",
        "may","men","met","mid","mix","mob","mod","mom","mop","mow","mud","mug","mum","nab","nag","nap",
        "net","new","nil","nip","nod","nor","not","now","nun","nut","oak","oar","oat","odd","ode","off",
        "oft","oil","old","one","opt","orb","ore","our","out","owe","owl","own","pad","pal","pan","pap",
        "par","pat","paw","pay","pea","peg","pen","pep","per","pet","pew","pie","pig","pin","pit","ply",
        "pod","pop","pot","pow","pro","pry","pub","pug","pun","pup","pus","put","rag","ram","ran","rap",
        "rat","raw","ray","red","ref","rib","rid","rig","rim","rip","rob","rod","roe","rot","row","rub",
        "rug","rum","run","rut","rye","sac","sad","sag","sap","sat","saw","say","sea","set","sew","she",
        "shy","sin","sip","sir","sis","sit","six","ski","sky","sly","sob","sod","son","sop","sot","sow",
        "soy","spa","spy","sty","sub","sue","sum","sun","sup","tab","tad","tag","tan","tap","tar","tat",
        "tax","tea","ten","the","tie","tin","tip","toe","ton","too","top","tot","tow","toy","try","tub",
        "tug","tun","two","urn","use","van","vat","vet","via","vie","vim","vow","wad","wag","war","was",
        "wax","way","web","wed","wet","who","why","wig","win","wit","woe","wok","won","woo","wow","yak",
        "yam","yap","yaw","yea","yes","yet","yew","you","zap","zed","zen","zip","zoo",
        "able","also","area","army","away","back","ball","band","bank","base","bath","bean","bear","beat",
        "been","beer","bell","belt","bend","best","bird","bite","blow","blue","boat","body","bold","bomb",
        "bond","bone","book","born","boss","both","bowl","burn","busy","cafe","cage","cake","call","calm",
        "came","camp","card","care","case","cash","cast","cave","chip","city","clay","clip","club","clue",
        "coal","coat","code","coin","cold","come","cook","cool","cope","copy","core","corn","cost","crew",
        "crop","cure","cute","dale","dame","damn","dare","dark","data","date","dawn","dead","deaf","deal",
        "dear","debt","deck","deed","deem","deep","deer","deny","desk","dial","dice","diet","dirt","dish",
        "disk","dock","does","dome","done","door","dose","down","drag","draw","drew","drop","drum","dual",
        "dull","dumb","dump","dust","duty","each","earn","ease","east","easy","edge","else","emit","envy",
        "epic","even","ever","evil","exam","exit","face","fact","fade","fail","fair","fake","fall","fame",
        "farm","fast","fate","fear","feat","feed","feel","feet","fell","felt","file","fill","film","find",
        "fine","fire","firm","fish","fist","five","flag","flat","flew","flip","flow","foam","fold","folk",
        "fond","food","fool","foot","ford","fore","fork","form","fort","foul","four","free","from","fuel",
        "full","fund","fury","fuse","gain","gait","gale","game","gang","gate","gave","gaze","gear","gene",
        "gift","girl","give","glad","glow","glue","goat","goes","gold","golf","gone","good","grab","gram",
        "gray","grew","grid","grim","grin","grip","grow","gulf","guru","gust","half","hall","halt","hand",
        "hang","hard","harm","hate","haul","have","head","heal","heap","hear","heat","heel","held","hell",
        "help","herb","herd","here","hero","hide","high","hike","hill","hint","hire","hold","hole","holy",
        "home","hood","hook","hope","horn","host","hour","huge","hung","hunt","hurt","hymn","icon","idea",
        "inch","into","iron","isle","item","jack","jail","jazz","jean","jeep","jerk","jest","jobs","john",
        "join","joke","jump","june","jury","just","keen","keep","kept","kick","kill","kind","king","kiss",
        "knee","knew","knit","knob","knot","know","lace","lack","laid","lake","lamb","lame","lamp","land",
        "lane","last","late","lawn","lead","leaf","lean","leap","left","lend","lens","less","lick","lied",
        "life","lift","like","limb","lime","limp","line","link","lion","list","live","load","loan","lock",
        "logo","lone","long","look","lord","lose","loss","lost","lots","loud","love","luck","lump","lung",
        "lure","lurk","made","mail","main","make","male","mall","malt","mane","many","mare","mark","mask",
        "mass","mast","mate","maze","mead","meal","mean","meat","meet","melt","memo","mend","menu","mere",
        "mesh","mess","mild","mile","milk","mill","mind","mine","miss","mist","mode","mold","mood","moon",
        "more","moss","most","moth","move","much","must","myth","nail","name","navy","near","neat","neck",
        "need","nest","news","next","nice","nine","node","none","noon","norm","nose","note","noun","nude"
    ]

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Word Builder (Trie)")
        self.geometry("600x500")
        self.resizable(False, False)
        self.callback = callback
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        # Build Trie from dictionary
        self.trie = Trie()
        for word in self.DICTIONARY:
            self.trie.insert(word.lower())

        # Generate random letters (vowels + consonants balanced)
        vowels = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"
        self.letters = [random.choice(vowels) for _ in range(4)] + \
                       [random.choice(consonants) for _ in range(8)]
        random.shuffle(self.letters)

        self.current_player = 1
        self.p1_words = []
        self.p2_words = []
        self.p1_score = 0
        self.p2_score = 0
        self.time_limit = 30
        self.time_left = self.time_limit
        self.running = False
        self.used_words = set()

        # UI
        tk.Label(self, text="WORD BUILDER", font=("Arial", 18, "bold"), fg="#8e44ad").pack(pady=5)
        self.info_label = tk.Label(self, text="Player 1: Press Start!", font=("Arial", 14, "bold"), fg="#e63946")
        self.info_label.pack(pady=5)

        self.timer_label = tk.Label(self, text=f"Time: {self.time_limit}s", font=("Arial", 16, "bold"), fg="#2c3e50")
        self.timer_label.pack(pady=3)

        letters_text = "  ".join([c.upper() for c in self.letters])
        self.letters_label = tk.Label(self, text=f"Letters: {letters_text}",
                                      font=("Arial", 16, "bold"), fg="#2980b9", bg="#ecf0f1",
                                      relief=tk.RIDGE, padx=10, pady=5)
        self.letters_label.pack(pady=8)

        tk.Label(self, text="Type a word using ONLY these letters and press Enter:",
                font=("Arial", 10)).pack()
        self.entry = tk.Entry(self, font=("Arial", 16), width=20, justify=tk.CENTER)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self._submit_word)
        self.entry.config(state=tk.DISABLED)

        self.feedback = tk.Label(self, text="", font=("Arial", 11, "italic"), fg="gray")
        self.feedback.pack(pady=3)

        self.words_label = tk.Label(self, text="Words found: (none)", font=("Arial", 10), fg="#555", wraplength=550)
        self.words_label.pack(pady=3)

        self.score_label = tk.Label(self, text="P1: 0 | P2: 0", font=("Arial", 13, "bold"), fg="#2c3e50")
        self.score_label.pack(pady=3)

        self.start_btn = tk.Button(self, text="Start (Player 1)", font=("Arial", 13, "bold"),
                                    bg="#2ecc71", fg="white", command=self._start_turn)
        self.start_btn.pack(pady=8)

    def _start_turn(self):
        self.start_btn.config(state=tk.DISABLED)
        self.entry.config(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.entry.focus()
        self.time_left = self.time_limit
        self.running = True
        self.used_words = set()
        if self.current_player == 1:
            self.p1_words = []
        else:
            self.p2_words = []
        self.words_label.config(text="Words found: (none)")
        self.feedback.config(text="")
        self._tick()

    def _tick(self):
        if not self.running:
            return
        self.time_left -= 1
        self.timer_label.config(text=f"Time: {self.time_left}s")
        if self.time_left <= 5:
            self.timer_label.config(fg="#e74c3c")
        else:
            self.timer_label.config(fg="#2c3e50")
        if self.time_left <= 0:
            self._end_round()
        else:
            self.after(1000, self._tick)

    def _submit_word(self, event):
        if not self.running:
            return
        word = self.entry.get().strip().lower()
        self.entry.delete(0, tk.END)

        if len(word) < 2:
            self.feedback.config(text="Word must be at least 2 letters!", fg="red")
            return
        if word in self.used_words:
            self.feedback.config(text=f"'{word}' already used!", fg="orange")
            return

        # Check letters are available
        avail = list(self.letters)
        valid_letters = True
        for ch in word:
            if ch in avail:
                avail.remove(ch)
            else:
                valid_letters = False
                break

        if not valid_letters:
            self.feedback.config(text=f"'{word}' uses letters not available!", fg="red")
            return

        # Trie lookup - O(L) validation
        if self.trie.search(word):
            self.used_words.add(word)
            score = len(word) * len(word)  # longer words = more points
            if self.current_player == 1:
                self.p1_words.append(word)
                self.p1_score += score
            else:
                self.p2_words.append(word)
                self.p2_score += score
            cur_words = self.p1_words if self.current_player == 1 else self.p2_words
            self.words_label.config(text="Words: " + ", ".join(cur_words))
            self.feedback.config(text=f"'{word}' +{score} pts!", fg="green")
            self.score_label.config(text=f"P1: {self.p1_score} | P2: {self.p2_score}")
        else:
            # Check prefix for hint
            if self.trie.starts_with(word):
                self.feedback.config(text=f"'{word}' is a prefix but not a word!", fg="orange")
            else:
                self.feedback.config(text=f"'{word}' not in dictionary!", fg="red")

    def _end_round(self):
        self.running = False
        self.entry.config(state=tk.DISABLED)
        if self.current_player == 1:
            self.info_label.config(text=f"P1 scored {self.p1_score}! Player 2 get ready!", fg="#457b9d")
            self.current_player = 2
            # New letters for player 2
            vowels = "aeiou"
            consonants = "bcdfghjklmnpqrstvwxyz"
            self.letters = [random.choice(vowels) for _ in range(4)] + \
                           [random.choice(consonants) for _ in range(8)]
            random.shuffle(self.letters)
            letters_text = "  ".join([c.upper() for c in self.letters])
            self.letters_label.config(text=f"Letters: {letters_text}")
            self.start_btn.config(text="Start (Player 2)", state=tk.NORMAL, bg="#3498db")
        else:
            winner = 1 if self.p1_score > self.p2_score else (2 if self.p2_score > self.p1_score else random.choice([1, 2]))
            from tkinter import messagebox
            messagebox.showinfo("Word Builder Results",
                f"Player 1: {self.p1_score} pts ({len(self.p1_words)} words)\n"
                f"Player 2: {self.p2_score} pts ({len(self.p2_words)} words)\n\n"
                f"Player {winner} wins!", parent=self)
            self.callback(winner)
            self.destroy()


class SnakeNode:
    """Singly Linked List node for the Snake body."""
    __slots__ = ['x', 'y', 'next']
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.next = None

class SnakeLinkedList:
    """
    Singly Linked List representing a snake.
    Head insertions O(1), tail removals O(n) - demonstrating linked list traversal.
    """
    def __init__(self, x, y):
        self.head = SnakeNode(x, y)
        self.length = 1

    def push_front(self, x, y):
        """Insert new head node - O(1)."""
        new_node = SnakeNode(x, y)
        new_node.next = self.head
        self.head = new_node
        self.length += 1

    def pop_tail(self):
        """Remove tail node - O(n) linked list traversal."""
        if self.head is None or self.head.next is None:
            return
        current = self.head
        while current.next.next is not None:
            current = current.next
        current.next = None
        self.length -= 1

    def get_positions(self):
        """Traverse the linked list to get all positions."""
        positions = []
        current = self.head
        while current:
            positions.append((current.x, current.y))
            current = current.next
        return positions

    def contains(self, x, y):
        """Search linked list for a position - O(n)."""
        current = self.head
        while current:
            if current.x == x and current.y == y:
                return True
            current = current.next
        return False


class SnakeRaceDialog(tk.Toplevel):
    """
    Minigame: Snake Race
    DSA Technique: Singly Linked List for snake body management.
    Each snake segment is a node in a linked list.
    Head insertion O(1) for growth, tail removal O(n) for movement,
    and O(n) traversal for collision detection.
    Two players race to eat the most food in 30 seconds!
    P1: WASD, P2: Arrow keys.
    """
    CELL = 20
    COLS = 30
    ROWS = 25

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Minigame: Snake Race (Linked List)")
        w = self.COLS * self.CELL
        h = self.ROWS * self.CELL + 60
        self.geometry(f"{w}x{h}")
        self.resizable(False, False)
        self.callback = callback
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.info = tk.Label(self, text="P1 (WASD): 0  |  P2 (Arrows): 0",
                             font=("Arial", 13, "bold"), fg="#2c3e50")
        self.info.pack(pady=2)
        self.timer_label = tk.Label(self, text="Time: 30s", font=("Arial", 12, "bold"))
        self.timer_label.pack(pady=2)
        self.canvas = tk.Canvas(self, width=w, height=self.ROWS * self.CELL, bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack()

        # Snake 1 (left side)
        self.snake1 = SnakeLinkedList(5, self.ROWS // 2)
        self.dir1 = (1, 0)
        self.next_dir1 = (1, 0)
        self.score1 = 0

        # Snake 2 (right side)
        self.snake2 = SnakeLinkedList(self.COLS - 6, self.ROWS // 2)
        self.dir2 = (-1, 0)
        self.next_dir2 = (-1, 0)
        self.score2 = 0

        # Food
        self.foods = []
        for _ in range(5):
            self._spawn_food()

        self.time_left = 30
        self.running = True

        self.bind("<KeyPress>", self._key)
        self.focus_set()
        self._tick()
        self._timer_tick()

    def _spawn_food(self):
        for _ in range(100):
            x = random.randint(1, self.COLS - 2)
            y = random.randint(1, self.ROWS - 2)
            if not self.snake1.contains(x, y) and not self.snake2.contains(x, y) and (x, y) not in self.foods:
                self.foods.append((x, y))
                return

    def _key(self, e):
        k = e.keysym.lower()
        # P1: WASD
        if k == 'w' and self.dir1 != (0, 1): self.next_dir1 = (0, -1)
        elif k == 's' and self.dir1 != (0, -1): self.next_dir1 = (0, 1)
        elif k == 'a' and self.dir1 != (1, 0): self.next_dir1 = (-1, 0)
        elif k == 'd' and self.dir1 != (-1, 0): self.next_dir1 = (1, 0)
        # P2: Arrows
        elif k == 'up' and self.dir2 != (0, 1): self.next_dir2 = (0, -1)
        elif k == 'down' and self.dir2 != (0, -1): self.next_dir2 = (0, 1)
        elif k == 'left' and self.dir2 != (1, 0): self.next_dir2 = (-1, 0)
        elif k == 'right' and self.dir2 != (-1, 0): self.next_dir2 = (1, 0)

    def _move_snake(self, snake, direction):
        """Move snake: push new head (O(1)), pop tail (O(n) traversal)."""
        hx = snake.head.x + direction[0]
        hy = snake.head.y + direction[1]
        # Wrap around
        hx %= self.COLS
        hy %= self.ROWS
        snake.push_front(hx, hy)
        return hx, hy

    def _tick(self):
        if not self.running:
            return
        self.dir1 = self.next_dir1
        self.dir2 = self.next_dir2

        # Move snake 1
        hx1, hy1 = self._move_snake(self.snake1, self.dir1)
        ate1 = False
        if (hx1, hy1) in self.foods:
            self.foods.remove((hx1, hy1))
            self.score1 += 1
            ate1 = True
            self._spawn_food()
        if not ate1:
            self.snake1.pop_tail()

        # Check self-collision snake1 (O(n) linked list search)
        positions1 = self.snake1.get_positions()
        if positions1[0] in positions1[1:]:
            # Reset snake 1
            self.snake1 = SnakeLinkedList(5, self.ROWS // 2)
            self.dir1 = (1, 0)
            self.next_dir1 = (1, 0)

        # Move snake 2
        hx2, hy2 = self._move_snake(self.snake2, self.dir2)
        ate2 = False
        if (hx2, hy2) in self.foods:
            self.foods.remove((hx2, hy2))
            self.score2 += 1
            ate2 = True
            self._spawn_food()
        if not ate2:
            self.snake2.pop_tail()

        positions2 = self.snake2.get_positions()
        if positions2[0] in positions2[1:]:
            self.snake2 = SnakeLinkedList(self.COLS - 6, self.ROWS // 2)
            self.dir2 = (-1, 0)
            self.next_dir2 = (-1, 0)

        # Cross collision
        if self.snake2.contains(hx1, hy1):
            self.snake1 = SnakeLinkedList(5, self.ROWS // 2)
            self.dir1 = (1, 0); self.next_dir1 = (1, 0)
        if self.snake1.contains(hx2, hy2):
            self.snake2 = SnakeLinkedList(self.COLS - 6, self.ROWS // 2)
            self.dir2 = (-1, 0); self.next_dir2 = (-1, 0)

        self._draw()
        self.info.config(text=f"P1 (WASD): {self.score1}  |  P2 (Arrows): {self.score2}")
        self.after(100, self._tick)

    def _timer_tick(self):
        if not self.running:
            return
        self.time_left -= 1
        self.timer_label.config(text=f"Time: {self.time_left}s")
        if self.time_left <= 5:
            self.timer_label.config(fg="#e74c3c")
        if self.time_left <= 0:
            self.running = False
            winner = 1 if self.score1 > self.score2 else (2 if self.score2 > self.score1 else random.choice([1, 2]))
            from tkinter import messagebox
            messagebox.showinfo("Snake Race Over!",
                f"Player 1: {self.score1} food\nPlayer 2: {self.score2} food\n\nPlayer {winner} wins!",
                parent=self)
            self.callback(winner)
            self.destroy()
            return
        self.after(1000, self._timer_tick)

    def _draw(self):
        c = self.canvas
        c.delete("all")
        cs = self.CELL
        # Grid
        for x in range(0, self.COLS * cs, cs):
            c.create_line(x, 0, x, self.ROWS * cs, fill="#16213e", width=1)
        for y in range(0, self.ROWS * cs, cs):
            c.create_line(0, y, self.COLS * cs, y, fill="#16213e", width=1)
        # Food
        for fx, fy in self.foods:
            c.create_oval(fx*cs+3, fy*cs+3, fx*cs+cs-3, fy*cs+cs-3, fill="#f1c40f", outline="#f39c12", width=2)
        # Snake 1 (red)
        for i, (sx, sy) in enumerate(self.snake1.get_positions()):
            color = "#e63946" if i == 0 else "#c0392b"
            c.create_rectangle(sx*cs+1, sy*cs+1, sx*cs+cs-1, sy*cs+cs-1, fill=color, outline="#fff", width=1)
        # Snake 2 (blue)
        for i, (sx, sy) in enumerate(self.snake2.get_positions()):
            color = "#3498db" if i == 0 else "#2980b9"
            c.create_rectangle(sx*cs+1, sy*cs+1, sx*cs+cs-1, sy*cs+cs-1, fill=color, outline="#fff", width=1)
