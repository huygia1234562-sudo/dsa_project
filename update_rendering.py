
import re

with open("monopoly_ui.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update draw_board to draw inner green board and MONOPOLY logo
draw_board_start = text.find("    def draw_board(self):")
draw_board_body_start = text.find("        self.canvas.delete(\"board_item\")\n", draw_board_start) + 40

inner_board_code = """
        # Draw central green board
        cb1 = self.to_iso(1, 1, 0)
        cb2 = self.to_iso(10, 1, 0)
        cb3 = self.to_iso(10, 10, 0)
        cb4 = self.to_iso(1, 10, 0)
        self.canvas.create_polygon(cb1[0], cb1[1], cb2[0], cb2[1], cb3[0], cb3[1], cb4[0], cb4[1], fill="#9ec52d", outline="#9ec52d", tags="board_item")

        # Draw red MONOPOLY center banner
        mb1 = self.to_iso(2, 4.5, 1)
        mb2 = self.to_iso(9, 4.5, 1)
        mb3 = self.to_iso(9, 6.5, 1)
        mb4 = self.to_iso(2, 6.5, 1)
        self.canvas.create_polygon(mb1[0], mb1[1], mb2[0], mb2[1], mb3[0], mb3[1], mb4[0], mb4[1], fill="#e9322e", outline="white", width=4, tags="board_item")
        
        tx, ty = self.to_iso(5.5, 5.5, 5)
        self.canvas.create_text(tx, ty, text="MONOPOLY", font=("Arial", 28, "bold"), fill="white", angle=28, tags="board_item")
"""
text = text[:draw_board_body_start] + inner_board_code + text[draw_board_body_start:]


# 2. Update draw_die_face to draw 3D isometric dice
die_func_start = text.find("    def draw_die_face(self, x, y, value):")
die_func_end = text.find("    def animate_dice_throw", die_func_start)

iso_die_code = """    def draw_die_face(self, x, y, value):
        # We simulate a 3D die at screen coordinates (x, y)
        # Actually x, y from the physics engine are flat screen coords
        # We manually draw a cube using polygons
        s = 25 # scale
        
        # Colors
        top_color = "white"
        left_color = "#e0e0e0"
        right_color = "#cccccc"
        
        # Points for top face
        t1 = (x, y - s)
        t2 = (x + s * 1.2, y - s * 0.4)
        t3 = (x, y + s * 0.2)
        t4 = (x - s * 1.2, y - s * 0.4)
        self.canvas.create_polygon(*t1, *t2, *t3, *t4, fill=top_color, outline="black", width=2, tags="dice_anim")
        
        # Points for left face
        l1 = t4
        l2 = t3
        l3 = (x, y + s * 1.4)
        l4 = (x - s * 1.2, y + s * 0.8)
        self.canvas.create_polygon(*l1, *l2, *l3, *l4, fill=left_color, outline="black", width=2, tags="dice_anim")
        
        # Points for right face
        r1 = t3
        r2 = t2
        r3 = (x + s * 1.2, y + s * 0.8)
        r4 = (x, y + s * 1.4)
        self.canvas.create_polygon(*r1, *r2, *r3, *r4, fill=right_color, outline="black", width=2, tags="dice_anim")
        
        # Draw pips on Top Face
        r = 3
        # Simple local mapping for isometric top face
        def draw_pip(px, py):
            # px, py in -10 to 10 local grid
            # map to isometric top plane
            ix = x + px * 1.2
            iy = y - s * 0.4 + py * 0.6
            self.canvas.create_oval(ix - r, iy - r, ix + r, iy + r, fill="black", tags="dice_anim")
        
        dots = {
            1: [(0,0)],
            2: [(-8,-8), (8,8)],
            3: [(-8,-8), (0,0), (8,8)],
            4: [(-8,-8), (-8,8), (8,-8), (8,8)],
            5: [(-8,-8), (-8,8), (8,-8), (8,8), (0,0)],
            6: [(-8,-10), (-8,0), (-8,10), (8,-10), (8,0), (8,10)] # Adjusted for top face
        }
        for dx, dy in dots.get(value, []):
            draw_pip(dx, dy)

"""

text = text[:die_func_start] + iso_die_code + text[die_func_end:]

# Adjust button to not hide the MONOPOLY logo
btn_pos_start = text.find("self.btn_roll.place(")
btn_pos_end = text.find(")", btn_pos_start)
# We move the roll button to the bottom-right corner rather than the middle
text = text[:btn_pos_start] + "self.btn_roll.place(x=self.board_size - 130, y=self.board_size - 130, width=btn_size, height=btn_size" + text[btn_pos_end:]

with open("monopoly_ui.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated successfully")

