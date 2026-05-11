import tkinter as tk
from tkinter import messagebox, simpledialog

class CardDialog(tk.Toplevel):
    def __init__(self, parent, title, text, callback=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.callback = callback
        tk.Label(self, text=title, font=("Arial", 14, "bold"), fg="#c0392b").pack(pady=10)
        tk.Label(self, text=text, font=("Arial", 11), wraplength=360, justify=tk.CENTER).pack(pady=10)
        tk.Button(self, text="OK", font=("Arial", 12, "bold"), width=10,
                  command=self._ok).pack(pady=10)
    def _ok(self):
        self.destroy()
        if self.callback:
            self.callback()

class AuctionDialog(tk.Toplevel):
    def __init__(self, parent, sq, players, callback):
        super().__init__(parent)
        self.title("Auction: " + sq.name.replace("\n", " "))
        self.geometry("380x280")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.sq = sq
        self.players = players
        self.callback = callback
        self.bids = [0, 0]
        self.current = 0
        self.passed = [False, False]
        tk.Label(self, text=f"Auction: {sq.name.replace(chr(10),' ')}", font=("Arial", 14, "bold")).pack(pady=5)
        self.info = tk.Label(self, text="", font=("Arial", 11))
        self.info.pack(pady=5)
        self.bid_var = tk.StringVar(value="0")
        f = tk.Frame(self)
        f.pack(pady=5)
        tk.Label(f, text="Your bid: $", font=("Arial", 12)).pack(side=tk.LEFT)
        self.entry = tk.Entry(f, textvariable=self.bid_var, font=("Arial", 12), width=8)
        self.entry.pack(side=tk.LEFT)
        bf = tk.Frame(self)
        bf.pack(pady=10)
        tk.Button(bf, text="Bid", font=("Arial", 11, "bold"), bg="#2ecc71", fg="white",
                  command=self._bid, width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(bf, text="Pass", font=("Arial", 11), bg="#e74c3c", fg="white",
                  command=self._pass, width=8).pack(side=tk.LEFT, padx=5)
        self._update()

    def _update(self):
        p = self.players[self.current]
        highest = max(self.bids)
        self.info.config(text=f"{p.name}'s turn to bid\nHighest bid: ${highest}\n{p.name} has ${p.money}")

    def _bid(self):
        try:
            amt = int(self.bid_var.get())
        except ValueError:
            return
        p = self.players[self.current]
        if amt <= max(self.bids):
            messagebox.showwarning("Invalid", "Bid must be higher than current highest!", parent=self)
            return
        if amt > p.money:
            messagebox.showwarning("Invalid", "Not enough money!", parent=self)
            return
        self.bids[self.current] = amt
        self._next()

    def _pass(self):
        self.passed[self.current] = True
        self._next()

    def _next(self):
        other = 1 - self.current
        if self.passed[other]:
            self._finish()
            return
        self.current = other
        self.bid_var.set("0")
        self._update()

    def _finish(self):
        winner_idx = 0 if self.bids[0] >= self.bids[1] else 1
        if self.passed[0] and self.passed[1]:
            self.destroy()
            self.callback(None, 0)
            return
        if self.passed[winner_idx]:
            winner_idx = 1 - winner_idx
        bid = self.bids[winner_idx]
        self.destroy()
        self.callback(self.players[winner_idx], bid)

class TradeDialog(tk.Toplevel):
    def __init__(self, parent, logic, callback):
        super().__init__(parent)
        self.title("Trade")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.logic = logic
        self.callback = callback
        p1, p2 = logic.players
        tk.Label(self, text="Trade Properties", font=("Arial", 16, "bold")).pack(pady=5)
        main = tk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=10)
        # Left side (current player)
        lf = tk.LabelFrame(main, text=p1.name if logic.turn == 1 else p2.name, font=("Arial", 11, "bold"))
        lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.left_money = tk.Entry(lf, font=("Arial", 11), width=8)
        tk.Label(lf, text="Offer $:", font=("Arial", 10)).pack(anchor=tk.W)
        self.left_money.pack(anchor=tk.W, padx=5)
        self.left_money.insert(0, "0")
        self.left_vars = {}
        self.left_p = logic.p
        for sq in logic.get_tradeable_properties(self.left_p):
            v = tk.BooleanVar()
            tk.Checkbutton(lf, text=sq.name.replace("\n", " "), variable=v,
                          font=("Arial", 9)).pack(anchor=tk.W)
            self.left_vars[sq.index] = v
        # Right side (other player)
        self.right_p = logic.other()
        rf = tk.LabelFrame(main, text=self.right_p.name, font=("Arial", 11, "bold"))
        rf.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.right_money = tk.Entry(rf, font=("Arial", 11), width=8)
        tk.Label(rf, text="Request $:", font=("Arial", 10)).pack(anchor=tk.W)
        self.right_money.pack(anchor=tk.W, padx=5)
        self.right_money.insert(0, "0")
        self.right_vars = {}
        for sq in logic.get_tradeable_properties(self.right_p):
            v = tk.BooleanVar()
            tk.Checkbutton(rf, text=sq.name.replace("\n", " "), variable=v,
                          font=("Arial", 9)).pack(anchor=tk.W)
            self.right_vars[sq.index] = v
        bf = tk.Frame(self)
        bf.pack(pady=10)
        tk.Button(bf, text="Propose Trade", font=("Arial", 12, "bold"), bg="#2ecc71",
                  fg="white", command=self._propose).pack(side=tk.LEFT, padx=5)
        tk.Button(bf, text="Cancel", font=("Arial", 12), bg="#e74c3c",
                  fg="white", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _propose(self):
        try:
            lm = int(self.left_money.get())
            rm = int(self.right_money.get())
        except ValueError:
            messagebox.showwarning("Invalid", "Money must be a number!", parent=self)
            return
        lp = [i for i, v in self.left_vars.items() if v.get()]
        rp = [i for i, v in self.right_vars.items() if v.get()]
        if not lp and not rp and lm == 0 and rm == 0:
            messagebox.showwarning("Invalid", "Select something to trade!", parent=self)
            return
        if lm > self.left_p.money:
            messagebox.showwarning("Invalid", f"{self.left_p.name} doesn't have ${lm}!", parent=self)
            return
        if rm > self.right_p.money:
            messagebox.showwarning("Invalid", f"{self.right_p.name} doesn't have ${rm}!", parent=self)
            return
        desc_l = ", ".join(self.logic.board[i].name.replace("\n"," ") for i in lp)
        desc_r = ", ".join(self.logic.board[i].name.replace("\n"," ") for i in rp)
        msg = f"{self.left_p.name} offers:\n  ${lm}" + (f", {desc_l}" if desc_l else "")
        msg += f"\n\nFor {self.right_p.name}'s:\n  ${rm}" + (f", {desc_r}" if desc_r else "")
        msg += f"\n\n{self.right_p.name}, accept this trade?"
        if messagebox.askyesno("Trade Proposal", msg, parent=self):
            self.logic.execute_trade(self.left_p, self.right_p, lm, rm, lp, rp)
            self.destroy()
            self.callback()
        else:
            messagebox.showinfo("Rejected", "Trade was rejected.", parent=self)

class JailDialog(tk.Toplevel):
    def __init__(self, parent, player, has_card, callback):
        super().__init__(parent)
        self.title("You're in Jail!")
        self.geometry("350x220")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.callback = callback
        tk.Label(self, text=f"{player.name} is in Jail!", font=("Arial", 14, "bold"),
                fg="#e74c3c").pack(pady=10)
        tk.Label(self, text=f"Turn {player.jail_turns + 1} of 3",
                font=("Arial", 11)).pack(pady=5)
        tk.Button(self, text="Roll for Doubles", font=("Arial", 11, "bold"),
                  bg="#3498db", fg="white", width=20,
                  command=lambda: self._choose("roll")).pack(pady=3)
        tk.Button(self, text="Pay $50 Fine", font=("Arial", 11),
                  bg="#e67e22", fg="white", width=20,
                  command=lambda: self._choose("pay")).pack(pady=3)
        if has_card:
            tk.Button(self, text="Use Get Out of Jail Free Card", font=("Arial", 11),
                      bg="#2ecc71", fg="white", width=20,
                      command=lambda: self._choose("card")).pack(pady=3)
    def _choose(self, choice):
        self.destroy()
        self.callback(choice)

class DeedDialog(tk.Toplevel):
    def __init__(self, parent, sq, logic):
        super().__init__(parent)
        self.title("Title Deed")
        self.geometry("280x350")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        name = sq.name.replace("\n", " ")
        hdr = tk.Frame(self, bg=sq.color, height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="TITLE DEED", font=("Arial", 9), bg=sq.color).pack()
        tk.Label(hdr, text=name, font=("Arial", 12, "bold"), bg=sq.color).pack()
        f = tk.Frame(self)
        f.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        if sq.group_number >= 3:
            rows = [("Rent", f"${sq.rent[0]}"), ("With 1 House", f"${sq.rent[1]}"),
                    ("With 2 Houses", f"${sq.rent[2]}"), ("With 3 Houses", f"${sq.rent[3]}"),
                    ("With 4 Houses", f"${sq.rent[4]}"), ("With HOTEL", f"${sq.rent[5]}"),
                    ("Mortgage Value", f"${sq.price//2}"), ("Houses cost", f"${sq.house_price} each")]
            for label, val in rows:
                r = tk.Frame(f)
                r.pack(fill=tk.X)
                tk.Label(r, text=label, font=("Arial", 9), anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(r, text=val, font=("Arial", 9, "bold"), anchor=tk.E).pack(side=tk.RIGHT)
        elif sq.group_number == 1:
            tk.Label(f, text="Railroad", font=("Arial", 11, "bold")).pack()
            for n, r in [(1, 25), (2, 50), (3, 100), (4, 200)]:
                r2 = tk.Frame(f); r2.pack(fill=tk.X)
                tk.Label(r2, text=f"If {n} RR owned", font=("Arial", 9)).pack(side=tk.LEFT)
                tk.Label(r2, text=f"${r}", font=("Arial", 9, "bold")).pack(side=tk.RIGHT)
        elif sq.group_number == 2:
            tk.Label(f, text="Utility\n\nIf 1 utility owned:\nRent = 4x dice\n\nIf 2 utilities owned:\nRent = 10x dice",
                    font=("Arial", 10), justify=tk.LEFT).pack()
        owner_txt = "Unowned"
        if sq.owner > 0:
            owner_txt = f"Owner: {logic.players[sq.owner-1].name}"
        tk.Label(f, text=owner_txt, font=("Arial", 10, "italic"), fg="gray").pack(pady=5)
        if sq.mortgage:
            tk.Label(f, text="MORTGAGED", font=("Arial", 14, "bold"), fg="red").pack()
        tk.Button(self, text="Close", command=self.destroy).pack(pady=5)
