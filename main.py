import tkinter as tk
from monopoly_ui import MonopolyUI

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Monopoly - IT003 Project")
        self.root.geometry("1400x1100")
        self.root.resizable(True, True)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.show_menu()

    def show_menu(self):
        for w in self.main_frame.winfo_children():
            w.destroy()
        tk.Label(self.main_frame, text="MONOPOLY", font=("Arial", 36, "bold"), fg="#e63946").pack(pady=(60, 10))
        tk.Label(self.main_frame, text="IT003.Q21.TTNT Project", font=("Arial", 14, "italic"), fg="#457b9d").pack(pady=(0, 10))
        tk.Label(self.main_frame, text="Full Classic Rules + 8 DSA Minigames", font=("Arial", 11), fg="gray").pack(pady=(0, 30))
        tk.Button(self.main_frame, text="Start Monopoly", font=("Arial", 18, "bold"),
                  width=25, bg="#e63946", fg="white", activebackground="#d62828",
                  command=self.start_monopoly).pack(pady=20)

    def start_monopoly(self):
        for w in self.main_frame.winfo_children():
            w.destroy()
        MonopolyUI(self.main_frame, on_back=self.show_menu)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
