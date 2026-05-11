
import re

with open("monopoly_ui.py", "r", encoding="utf-8") as f:
    text = f.read()

start_str = "    def get_space_coords(self, index):"
end_str = "    def update_info(self):"

start_idx = text.find(start_str)
end_idx = text.find(end_str)

new_text = text[:start_idx] + """    def get_logical_coords(self, index):
        if 0 <= index <= 10: return 10 - index, 10
        elif 11 <= index <= 20: return 0, 20 - index
        elif 21 <= index <= 30: return index - 20, 0
        else: return 10, index - 30

    def to_iso(self, x, y, z=0):
        scale = 32
        x *= scale
        y *= scale
        # Isometric projection angles
        iso_x = 350 + (x - y) * 0.866
        iso_y = 100 + (x + y) * 0.5 - z
        return iso_x, iso_y

    def draw_board(self):
        self.canvas.delete("board_item")
        
        # Map players to their tiles
        players_on_tile = {i: [] for i in range(len(self.logic.board))}
        for idx, player in enumerate(self.logic.players):
            players_on_tile[player.position].append((idx, player))

        # Sort spaces by depth to draw back-to-front
        space_draw_order = []
        for i, space in enumerate(self.logic.board):
            tx, ty = self.get_logical_coords(i)
            space_draw_order.append((tx + ty, i, space, tx, ty))
        
        space_draw_order.sort(key=lambda item: item[0])
        
        for depth, i, space, tx, ty in space_draw_order:
            z_top = 10
            color = getattr(space, "color", "white")
            
            c1 = self.to_iso(tx, ty, z_top)     # top
            c2 = self.to_iso(tx+1, ty, z_top)   # right
            c3 = self.to_iso(tx+1, ty+1, z_top) # bottom
            c4 = self.to_iso(tx, ty+1, z_top)   # left

            b1 = self.to_iso(tx, ty, 0)
            b2 = self.to_iso(tx+1, ty, 0)
            b3 = self.to_iso(tx+1, ty+1, 0)
            b4 = self.to_iso(tx, ty+1, 0)
            
            # Base of the tile (3D effect)
            self.canvas.create_polygon(c4[0], c4[1], b4[0], b4[1], b1[0], b1[1], c1[0], c1[1], fill="#999999", outline="black", tags="board_item")
            self.canvas.create_polygon(c3[0], c3[1], b3[0], b3[1], b4[0], b4[1], c4[0], c4[1], fill="#666666", outline="black", tags="board_item")
            
            # Top of the tile
            self.canvas.create_polygon(c1[0], c1[1], c2[0], c2[1], c3[0], c3[1], c4[0], c4[1], fill=color, outline="black", width=1, tags="board_item")
            
            # Ownership tag
            if getattr(space, "owner", None):
                oc1 = self.to_iso(tx+0.1, ty+0.1, z_top)
                oc2 = self.to_iso(tx+0.9, ty+0.1, z_top)
                oc3 = self.to_iso(tx+0.9, ty+0.3, z_top)
                oc4 = self.to_iso(tx+0.1, ty+0.3, z_top)
                self.canvas.create_polygon(oc1[0], oc1[1], oc2[0], oc2[1], oc3[0], oc3[1], oc4[0], oc4[1], fill=space.owner.color, tags="board_item")

            # Houses / Hotel
            houses = getattr(space, "houses", 0)
            if houses == 5:
                h_iso = self.to_iso(tx+0.5, ty+0.8, z_top)
                self.canvas.create_polygon(*h_iso, self.to_iso(tx+0.7, ty+0.8, z_top), self.to_iso(tx+0.7, ty+0.9, z_top+10), self.to_iso(tx+0.5, ty+0.9, z_top+10), fill="red", outline="black", tags="board_item")
            elif houses > 0:
                for h in range(houses):
                    h1 = self.to_iso(tx+0.2 + h*0.15, ty+0.8, z_top)
                    self.canvas.create_rectangle(h1[0]-3, h1[1]-6, h1[0]+3, h1[1], fill="#2ecc71", outline="black", tags="board_item")

            # Text
            display_text = space.name.replace(" ", "\\n")
            if getattr(space, "price", 0) > 0:
                display_text += f"\\n${space.price}"
            ct_x, ct_y = self.to_iso(tx+0.5, ty+0.5, z_top+4)
            self.canvas.create_text(ct_x, ct_y, text=display_text, font=("Arial", 6, "bold"), justify=tk.CENTER, tags="board_item")

            # Players on this tile
            for p_idx, player in players_on_tile[i]:
                ox = 0.3 + (p_idx * 0.4)
                oy = 0.5
                px, py = self.to_iso(tx+ox, ty+oy, z_top+20) # Hovering token
                pin_base = self.to_iso(tx+ox, ty+oy, z_top)
                # Shadow/Line connecting token to board
                self.canvas.create_line(px, py, pin_base[0], pin_base[1], fill="black", width=2, tags="board_item")
                # Player Token
                self.canvas.create_oval(px-8, py-16, px+8, py, fill=player.color, outline="white", width=2, tags="board_item")

""" + text[end_idx:]

with open("monopoly_ui.py", "w", encoding="utf-8") as f:
    f.write(new_text)
print("Updated successfully")

