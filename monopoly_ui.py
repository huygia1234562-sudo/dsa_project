import tkinter as tk
from tkinter import messagebox
import random, math
from PIL import Image, ImageDraw, ImageFont, ImageTk
from monopoly_logic import MonopolyLogic
from monopoly_dialogs import CardDialog, JailDialog
from minigame_ui import (
    TypingRaceDialog, PingPongDialog, QuickMathDialog, CoinCatcherDialog,
    PacmanDialog, SnakeRaceDialog
)

class FloatingText:
    def __init__(s, c, x, y, t, col):
        s.canvas=c; s.id=c.create_text(x,y,text=t,fill=col,font=("Arial",14,"bold"),tags="dynamic"); s.y=y; s.life=30
    def update(s):
        s.y-=2; s.canvas.coords(s.id,s.canvas.coords(s.id)[0],s.y); s.life-=1
        if s.life<=0: s.canvas.delete(s.id)
        return s.life>0

class MonopolyUI:
    def __init__(self, parent, on_back):
        self.parent = parent
        self.on_back = on_back
        self.logic = MonopolyLogic()
        self.floating_texts = []
        self.animating = False
        self.tile_image_cache = {}
        self.tile_photo_refs = []
        self.setup_ui()
        self.draw_static_board()
        self.draw_dynamic()
        self.update_info()
        self.update_prop_list()
        self.animate_tick()

    def setup_ui(self):
        self.toolbar = tk.Frame(self.parent, bg="#1f2933", height=56)
        self.toolbar.pack(fill=tk.X)
        self.toolbar.pack_propagate(False)
        tk.Button(self.toolbar, text="< Back", command=self.on_back, bg="#314153", fg="white",
                  activebackground="#40546a", activeforeground="white", relief=tk.FLAT,
                  font=("Arial",10,"bold")).pack(side=tk.LEFT, padx=12, pady=12)
        self.info_label = tk.Label(self.toolbar, text="", font=("Arial", 14, "bold"), bg="#1f2933", fg="white")
        self.info_label.pack(side=tk.LEFT, padx=20)
        # Money displays
        mf = tk.Frame(self.toolbar, bg="#1f2933")
        mf.pack(side=tk.RIGHT, padx=12)
        self.p1_money_lbl = tk.Label(mf, text="P1: $1500", font=("Arial",11,"bold"),
                                     fg="#ff6b6b", bg="#111820", padx=10, pady=5)
        self.p1_money_lbl.pack(side=tk.LEFT, padx=8)
        self.p2_money_lbl = tk.Label(mf, text="P2: $1500", font=("Arial",11,"bold"),
                                     fg="#74b9ff", bg="#111820", padx=10, pady=5)
        self.p2_money_lbl.pack(side=tk.LEFT, padx=8)

        self.body_frame = tk.Frame(self.parent, bg="#d8e3e8")
        self.body_frame.pack(expand=True, fill=tk.BOTH)
        self.canvas = tk.Canvas(self.body_frame, bg="#b7dcc8", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", self.on_resize)
        self.board_size = 1100
        self.space_size = self.board_size / 11

        self.btn_roll = tk.Button(self.canvas, text="ROLL", font=("Arial",14,"bold"),
            bg="#e63946", fg="white", activebackground="#b51f2c", activeforeground="white",
            relief=tk.RAISED, bd=4, command=self.handle_roll)
        self.btn_roll.place(x=self.board_size-130, y=self.board_size-130, width=100, height=100)

        # Right panel
        self.right_panel = tk.Frame(self.body_frame, bg="#f8fbfd", width=330)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        self.right_panel.pack_propagate(False)

        # Alert log
        tk.Label(self.right_panel, text="Game Log", font=("Arial",12,"bold"), bg="#f8fbfd", fg="#1f2933").pack(pady=(8, 4))
        self.alert_box = tk.Text(self.right_panel, font=("Arial",9), height=6, width=34, state=tk.DISABLED,
                                 wrap=tk.WORD, bg="#eef4f7", fg="#1f2933", relief=tk.FLAT, padx=8, pady=6)
        self.alert_box.pack(padx=10, fill=tk.X)

        # Landed info
        self.landed_label = tk.Label(self.right_panel, text="", font=("Arial",10,"bold"), bg="#e6f1f4", fg="#243447",
                                     wraplength=290, justify=tk.CENTER, padx=8, pady=8)
        self.landed_label.pack(fill=tk.X, padx=10, pady=8)

        # Properties
        tk.Label(self.right_panel, text="Your Properties", font=("Arial",12,"bold"), bg="#f8fbfd", fg="#1f2933").pack(pady=(8, 5))
        self.prop_list = tk.Listbox(self.right_panel, font=("Arial",9), height=8, bg="#ffffff",
                                    fg="#243447", relief=tk.FLAT, highlightthickness=1,
                                    highlightbackground="#d8e3e8", selectbackground="#74b9ff")
        self.prop_list.pack(fill=tk.X, padx=10)

        # Buttons frame
        bf = tk.Frame(self.right_panel, bg="#f8fbfd")
        bf.pack(fill=tk.X, padx=10, pady=6)
        self.btn_buy_house = tk.Button(bf, text="Buy House", font=("Arial",9), bg="#2ecc71", fg="white",
                                        activebackground="#27ae60", activeforeground="white",
                                        relief=tk.FLAT, command=self.buy_house)
        self.btn_buy_house.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        self.btn_sell_house = tk.Button(bf, text="Sell House", font=("Arial",9), bg="#e67e22", fg="white",
                                        activebackground="#ca6f1e", activeforeground="white",
                                        relief=tk.FLAT, command=self.sell_house)
        self.btn_sell_house.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)



        self.btn_resign = tk.Button(self.right_panel, text="Resign", font=("Arial",9),
                                     bg="#e74c3c", fg="white", activebackground="#c0392b",
                                     activeforeground="white", relief=tk.FLAT, command=self.resign)
        self.btn_resign.pack(fill=tk.X, padx=10, pady=8)

    def spawn_float(self, x, y, text, color):
        self.floating_texts.append(FloatingText(self.canvas, x, y, text, color))

    def animate_tick(self):
        self.floating_texts = [ft for ft in self.floating_texts if ft.update()]
        self.parent.after(40, self.animate_tick)

    def on_resize(self, event):
        ns = min(event.width, event.height)
        if hasattr(self,"board_size") and abs(self.board_size-ns)<10: return
        if ns<100: return
        self.board_size = ns
        self.space_size = ns/11
        self.btn_roll.place(x=event.width-130, y=event.height-130, width=100, height=100)
        if not self.animating:
            self.draw_static_board()
            self.draw_dynamic()

    def get_logical_coords(self, index):
        if 0<=index<=10: return 10-index, 10
        elif 11<=index<=20: return 0, 20-index
        elif 21<=index<=30: return index-20, 0
        else: return 10, index-30

    def to_iso(self, x, y, z=0):
        sc=55; x*=sc; y*=sc
        return 550+(x-y)*0.866, 150+(x+y)*0.5-z

    def _poly_iso(self, pts, fill, outline="#1f2933", width=1, tags="board_item"):
        flat = []
        for x, y, z in pts:
            px, py = self.to_iso(x, y, z)
            flat.extend([px, py])
        self.canvas.create_polygon(*flat, fill=fill, outline=outline, width=width, tags=tags)

    def _draw_city_backdrop(self):
        w = max(self.canvas.winfo_width(), self.board_size)
        h = max(self.canvas.winfo_height(), self.board_size)
        self.canvas.create_rectangle(0, 0, w, h, fill="#b9c8c7", outline="", tags="board_item")
        self.canvas.create_polygon(-80, 80, 260, -70, w+80, 520, w+80, 690, 240, 40,
                                   fill="#8f9b96", outline="", tags="board_item")
        self.canvas.create_polygon(-80, h-210, 220, h+70, w+80, 220, w+80, 360, 200, h-50,
                                   fill="#7e8984", outline="", tags="board_item")
        for x in range(-80, int(w)+120, 110):
            self.canvas.create_line(x, 0, x-220, h, fill="#cdd7d6", width=2, tags="board_item")
        for y in range(-40, int(h)+120, 95):
            self.canvas.create_line(0, y, w, y+210, fill="#cdd7d6", width=2, tags="board_item")

    def _draw_board_platform(self):
        top = [(-0.35, -0.35, -4), (11.35, -0.35, -4), (11.35, 11.35, -4), (-0.35, 11.35, -4)]
        bottom = [(-0.35, -0.35, -34), (11.35, -0.35, -34), (11.35, 11.35, -34), (-0.35, 11.35, -34)]
        for side, fill in [([top[1], top[2], bottom[2], bottom[1]], "#7f9094"),
                           ([top[2], top[3], bottom[3], bottom[2]], "#6d7d82"),
                           ([top[0], top[1], bottom[1], bottom[0]], "#aab8ba"),
                           ([top[3], top[0], bottom[0], bottom[3]], "#95a5a8")]:
            self._poly_iso(side, fill, outline="#5a676a", width=1)
        self._poly_iso(top, "#c7d5d6", outline="#6d7d82", width=3)

    def draw_static_board(self):
        self.canvas.delete("board_item")
        self.tile_photo_refs = []
        self._draw_city_backdrop()
        self._draw_board_platform()
        self._poly_iso([(1.05,1.05,6),(9.95,1.05,6),(9.95,9.95,6),(1.05,9.95,6)], "#d0a86d",
                       outline="#b6894d", width=2)
        self._poly_iso([(1.45,1.45,7),(9.55,1.45,7),(9.55,9.55,7),(1.45,9.55,7)], "#83a642",
                       outline="#83a642", width=1)
        mb1,mb2,mb3,mb4=self.to_iso(2.5,4.45,9),self.to_iso(8.5,4.45,9),self.to_iso(8.5,6.35,9),self.to_iso(2.5,6.35,9)
        self.canvas.create_polygon(mb1[0],mb1[1],mb2[0],mb2[1],mb3[0],mb3[1],mb4[0],mb4[1],fill="#f05a47",outline="#f8fbfd",width=4,tags="board_item")
        tx,ty=self.to_iso(5.5,5.4,13)
        self.canvas.create_text(tx,ty,text="MONOPOLY",font=("Arial",24,"bold"),fill="white",angle=28,tags="board_item")
        sdo=[]
        for i,sp in enumerate(self.logic.board):
            tx2,ty2=self.get_logical_coords(i)
            sdo.append((tx2+ty2,i,sp,tx2,ty2))
        sdo.sort(key=lambda x:x[0])
        self.space_centers={}
        for _,i,sp,tx2,ty2 in sdo:
            zt=10; col=sp.color
            c1,c2,c3,c4=self.to_iso(tx2,ty2,zt),self.to_iso(tx2+1,ty2,zt),self.to_iso(tx2+1,ty2+1,zt),self.to_iso(tx2,ty2+1,zt)
            b1,b2,b3,b4=self.to_iso(tx2,ty2,0),self.to_iso(tx2+1,ty2,0),self.to_iso(tx2+1,ty2+1,0),self.to_iso(tx2,ty2+1,0)
            self.canvas.create_polygon(c1[0],c1[1],b1[0],b1[1],b2[0],b2[1],c2[0],c2[1],fill="#8fa0a2",outline="#5e6d70",tags="board_item")
            self.canvas.create_polygon(c2[0],c2[1],b2[0],b2[1],b3[0],b3[1],c3[0],c3[1],fill="#6f8084",outline="#5e6d70",tags="board_item")
            self.canvas.create_polygon(c4[0],c4[1],b4[0],b4[1],b1[0],b1[1],c1[0],c1[1],fill="#aab8ba",outline="#5e6d70",tags="board_item")
            self.canvas.create_polygon(c3[0],c3[1],b3[0],b3[1],b4[0],b4[1],c4[0],c4[1],fill="#829296",outline="#5e6d70",tags="board_item")
            name_text, price_text, status_text = self._tile_label_parts(sp, i)
            self._draw_tile_image(i, tx2, ty2, zt+2, sp, name_text, price_text, status_text)
            if sp.owner > 0:
                pc = self.logic.players[sp.owner-1].color
                if sp.house == 5:
                    hx, hy = self._tile_lane_house_pos(i, tx2, ty2)
                    self._draw_tile_house(hx, hy, zt+8, pc, scale=1.05, hotel=True)
                elif sp.house > 0:
                    for h in range(sp.house):
                        hx, hy = self._tile_lane_house_pos(i, tx2, ty2, h, sp.house)
                        self._draw_tile_house(hx, hy, zt+8, pc, scale=0.65)
                else:
                    hx, hy = self._tile_lane_house_pos(i, tx2, ty2)
                    self._draw_tile_house(hx, hy, zt+8, pc, scale=0.58)
            self.space_centers[i]=self.to_iso(tx2+0.5, ty2+0.5, zt+4)

    def _tile_lane_house_pos(self, index, tx, ty, slot=0, count=1):
        lane = 0.115
        spread = (slot - (count - 1) / 2) * 0.18 if count > 1 else 0
        angle = self._tile_card_rotation(index)
        if angle == 90:
            u, v = lane, 0.5 + spread
        elif angle == 180:
            u, v = 0.5 + spread, 1 - lane
        elif angle == 270:
            u, v = 1 - lane, 0.5 + spread
        else:
            u, v = 0.5 + spread, lane
        return tx + max(0.08, min(0.92, u)), ty + max(0.08, min(0.92, v))

    def _draw_property_color_strip(self, index, tx, ty, z, color):
        if 0 <= index <= 10:
            pts = [(tx, ty, z), (tx+1, ty, z), (tx+1, ty+0.22, z), (tx, ty+0.22, z)]
        elif 11 <= index <= 20:
            pts = [(tx, ty, z), (tx+0.22, ty, z), (tx+0.22, ty+1, z), (tx, ty+1, z)]
        elif 21 <= index <= 30:
            pts = [(tx, ty, z), (tx+1, ty, z), (tx+1, ty+0.22, z), (tx, ty+0.22, z)]
        else:
            pts = [(tx, ty, z), (tx+0.22, ty, z), (tx+0.22, ty+1, z), (tx, ty+1, z)]
        self._poly_iso(pts, color, outline="#5e6d70", width=1)

    def _draw_tile_image(self, index, tx, ty, z, sp, name, price, status):
        fill = "#d0d5d2" if sp.mortgage else "#f7fbed"
        if sp.group_number == 0 and sp.price == 0:
            fill = "#f9fbf1"
        strip = sp.color if sp.group_number >= 3 and not sp.mortgage else None
        corners = [
            self.to_iso(tx, ty, z),
            self.to_iso(tx+1, ty, z),
            self.to_iso(tx+1, ty+1, z),
            self.to_iso(tx, ty+1, z),
        ]
        image, anchor = self._get_tile_image(index, fill, strip, corners, name, price, status)
        self.canvas.create_image(anchor[0], anchor[1], image=image, anchor=tk.NW, tags="board_item")
        self.tile_photo_refs.append(image)

    def _get_tile_image(self, index, fill, strip, corners, name, price, status):
        qcorners = tuple((round(x, 1), round(y, 1)) for x, y in corners)
        key = (index, fill, strip, qcorners, name, price, status)
        cached = self.tile_image_cache.get(key)
        if cached is not None:
            return cached

        min_x = math.floor(min(x for x, _ in corners)) - 5
        min_y = math.floor(min(y for _, y in corners)) - 5
        max_x = math.ceil(max(x for x, _ in corners)) + 5
        max_y = math.ceil(max(y for _, y in corners)) + 5
        w, h = max_x - min_x, max_y - min_y
        poly = [(x - min_x, y - min_y) for x, y in corners]
        card = self._render_tile_card(index, fill, strip, "", "", "")
        card = self._orient_tile_card(card, index)
        img = self._warp_tile_card(card, poly, (w, h))
        self._draw_crisp_tile_text(img, index, name, price, status, poly)
        draw = ImageDraw.Draw(img)
        draw.line(poly + [poly[0]], fill="#405155", width=3, joint="curve")

        photo = ImageTk.PhotoImage(img)
        result = (photo, (min_x, min_y))
        self.tile_image_cache[key] = result
        return result

    def _render_tile_card(self, index, fill, strip, name, price, status):
        w = h = 360
        img = Image.new("RGBA", (w, h), fill)
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, w-1, h-1), outline="#405155", width=9)

        if strip:
            draw.rectangle((0, 0, w, 82), fill=strip)
            draw.line((0, 82, w, 82), fill="#405155", width=5)

        color = "#c2188f" if index in (7, 22, 36) else "#111820"
        name_lines = self._wrap_tile_lines(name.replace("\n", " "), 11)
        name_area_h = 136 if strip else 164
        name_font = self._fit_tile_font(name_lines, 62, 34, w-30, name_area_h)
        price_font = self._tile_font(54 if price else 38)
        status_font = self._tile_font(28)

        top_pad = 104 if strip else 70
        name_boxes = [draw.textbbox((0, 0), line, font=name_font) for line in name_lines]
        name_h = sum(b[3]-b[1] for b in name_boxes) + max(0, len(name_boxes)-1) * 5
        name_y = top_pad + max(0, (name_area_h - name_h) // 2)
        for line, box in zip(name_lines, name_boxes):
            tw = box[2] - box[0]
            th = box[3] - box[1]
            draw.text(((w-tw)/2, name_y-box[1]), line, font=name_font, fill=color,
                      stroke_width=1, stroke_fill=color)
            name_y += th + 5

        if price:
            box = draw.textbbox((0, 0), price, font=price_font)
            draw.text(((w-(box[2]-box[0]))/2, 284-box[1]), price, font=price_font,
                      fill="#111820", stroke_width=1, stroke_fill="#111820")

        if status:
            box = draw.textbbox((0, 0), status, font=status_font)
            draw.text(((w-(box[2]-box[0]))/2, 326-box[1]), status, font=status_font, fill="#32424d")
        return img

    def _wrap_tile_lines(self, text, max_chars):
        words = text.split()
        if not words:
            return [""]
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else f"{cur} {word}"
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines[:3]

    def _fit_tile_font(self, lines, start, stop, max_width, max_height=None):
        probe = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(probe)
        for size in range(start, stop-1, -2):
            font = self._tile_font(size)
            boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
            widths = [box[2] - box[0] for box in boxes]
            heights = [box[3] - box[1] for box in boxes]
            total_h = sum(heights) + max(0, len(heights)-1) * 5
            if max(widths or [0]) <= max_width and (max_height is None or total_h <= max_height):
                return font
        return self._tile_font(stop)

    def _orient_tile_card(self, card, index):
        angle = self._tile_card_rotation(index)
        return card.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC) if angle else card

    def _tile_side_rotation(self, index):
        if 11 <= index <= 20:
            return 270
        if 21 <= index <= 30:
            return 180
        if 31 <= index <= 39:
            return 90
        return 0

    def _tile_card_rotation(self, index):
        angle = self._tile_side_rotation(index)
        if index in {11, 13, 14, 16, 18, 19, 21, 23, 24, 26, 27, 29}:
            angle += 180
        return angle % 360

    def _draw_crisp_tile_text(self, img, index, name, price, status, poly):
        c1, c2, _, c4 = poly
        vx = (c2[0] - c1[0], c2[1] - c1[1])
        vy = (c4[0] - c1[0], c4[1] - c1[1])
        rotation = self._tile_side_rotation(index)
        if rotation == 90:
            base = (-vy[0], -vy[1])
            depth = (vx[0], vx[1])
        elif rotation == 180:
            base = (-vx[0], -vx[1])
            depth = (-vy[0], -vy[1])
        elif rotation == 270:
            base = (vy[0], vy[1])
            depth = (-vx[0], -vx[1])
        else:
            base = (vx[0], vx[1])
            depth = (vy[0], vy[1])

        bw = max(42, int(math.hypot(*base) * 0.82))
        bh = max(26, int(math.hypot(*depth) * 0.72))
        lines = name.split("\n")
        if price:
            lines.append(price)
        if status:
            lines.append(status)
        fill = "#c2188f" if index in (7, 22, 36) else "#111820"

        probe = ImageDraw.Draw(img)
        for size in range(14, 7, -1):
            fonts = []
            for line in lines:
                fonts.append(self._tile_font(size + 1 if line.startswith("$") or line.startswith("-$") else size))
            boxes = [probe.textbbox((0, 0), line, font=font) for line, font in zip(lines, fonts)]
            widths = [b[2] - b[0] for b in boxes]
            heights = [b[3] - b[1] for b in boxes]
            total_h = sum(heights) + max(0, len(lines)-1) * 2
            if max(widths or [0]) <= bw - 4 and total_h <= bh - 2:
                break

        scale = 3
        text_img = Image.new("RGBA", (bw * scale, bh * scale), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        scaled_fonts = [
            self._tile_font((size + 1 if line.startswith("$") or line.startswith("-$") else size) * scale)
            for line in lines
        ]
        scaled_boxes = [
            text_draw.textbbox((0, 0), line, font=font)
            for line, font in zip(lines, scaled_fonts)
        ]
        scaled_heights = [box[3] - box[1] for box in scaled_boxes]
        scaled_total_h = sum(scaled_heights) + max(0, len(lines)-1) * 2 * scale
        y = (bh * scale - scaled_total_h) / 2
        for line, font, box in zip(lines, scaled_fonts, scaled_boxes):
            tw = box[2] - box[0]
            th = box[3] - box[1]
            text_draw.text(((bw * scale - tw) / 2, y - box[1]), line, font=font, fill=fill)
            y += th + 2 * scale

        screen_angle = math.degrees(math.atan2(base[1], base[0]))
        if screen_angle > 90:
            screen_angle -= 180
        elif screen_angle < -90:
            screen_angle += 180
        text_img = text_img.rotate(-screen_angle, expand=True, resample=Image.Resampling.BICUBIC)
        text_img = text_img.resize(
            (max(1, text_img.width // scale), max(1, text_img.height // scale)),
            Image.Resampling.LANCZOS,
        )
        cx = sum(p[0] for p in poly) / 4
        cy = sum(p[1] for p in poly) / 4
        img.alpha_composite(text_img, (int(cx - text_img.width / 2), int(cy - text_img.height / 2)))

    def _warp_tile_card(self, card, poly, size):
        c1, c2, _, c4 = poly
        vx = (c2[0] - c1[0], c2[1] - c1[1])
        vy = (c4[0] - c1[0], c4[1] - c1[1])
        det = vx[0] * vy[1] - vx[1] * vy[0]
        if abs(det) < 0.001:
            return Image.new("RGBA", size, (0, 0, 0, 0))

        sw, sh = card.size
        a = sw * vy[1] / det
        b = -sw * vy[0] / det
        c = sw * (-c1[0] * vy[1] + c1[1] * vy[0]) / det
        d = -sh * vx[1] / det
        e = sh * vx[0] / det
        f = sh * (vx[1] * c1[0] - vx[0] * c1[1]) / det
        return card.transform(
            size,
            Image.Transform.AFFINE,
            (a, b, c, d, e, f),
            resample=Image.Resampling.BICUBIC,
            fillcolor=(0, 0, 0, 0),
        )

    def _tile_font(self, size):
        for name in ("arialbd.ttf", "arial.ttf"):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                pass
        return ImageFont.load_default()

    def _tile_label_parts(self, sp, index):
        display_names = {
            0: "GO", 1: "An Giang", 2: "Mũi Né", 3: "Đồng Tháp",
            4: "Đánh thuế", 5: "Phú Quốc", 6: "Vĩnh Long", 7: "Cơ hội",
            8: "Cần Thơ", 9: "Tây Ninh", 10: "Thanh Hóa\n(JAIL)",
            11: "Đồng Nai", 12: "Sầm Sơn", 13: "Đắk Lắk",
            14: "Lâm Đồng", 15: "Côn Đảo", 16: "Khánh Hòa",
            17: "Mini\nGames", 18: "Gia Lai", 19: "Đà Nẵng",
            20: "Nam\nĐịnh", 21: "Quảng Trị", 22: "Cơ hội",
            23: "Ninh Bình", 24: "Hải Phòng", 25: "Nha Trang",
            26: "Hưng Yên", 27: "Bắc Ninh", 28: "Water\nWorks",
            29: "Phú Thọ", 30: "Ăn nem\nChua", 31: "Thái Nguyên",
            32: "Lào Cai", 33: "Mini\nGames", 34: "Hà Nội",
            35: "Mỹ Khê", 36: "Cơ hội", 37: "TP.HCM",
            38: "Đánh thuế", 39: "Quảng Ngãi",  
        }                
        name = display_names.get(index, sp.name)
        price = sp.price_text
        if index == 4:
            price = "-$200"
        elif index == 38:
            price = "-$100"
        return name, price, ""
        names = {
            0: "GO", 1: "An Giang", 2: "Mũi Né", 3: "Đồng Tháp",
            4: "Đánh thuế", 5: "Phú Quốc", 6: "Vĩnh Long", 7: "Cơ hội",
            8: "Cần Thơ", 9: "Tây Ninh", 10: "Thanh Hóa\n(JAIL)",
            11: "Đồng Nai", 12: "Sầm Sơn", 13: "Đắk Lắk",
            14: "Lâm Đồng", 15: "Côn Đảo", 16: "Khánh Hòa",
            17: "Minigame", 18: "Gia Lai", 19: "Đà Nẵng",
            20: "Nam\nĐịnh", 21: "Quảng Trị", 22: "Cơ hội",
            23: "Ninh Bình", 24: "Hải Phòng", 25: "Nha Trang",
            26: "Hưng Yên", 27: "Bắc Ninh", 28: "Water\nWorks",
            29: "Phú Thọ", 30: "Ăn nem\nChua", 31: "Thái Nguyên",
            32: "Lào Cai", 33: "Chest", 34: "Hà Nội",
            35: "Mỹ Khê", 36: "Chance", 37: "TP.HCM",
            38: "Đánh thuế", 39: "Quảng Ngãi",
        }
        name = names.get(index, sp.name.replace("\n", " ").replace("Avenue", "Ave").replace("Railroad", "RR"))
        price = ""
        if sp.price > 0:
            price = f"${sp.price}"
        elif index == 4:
            price = "-$200"
        elif index == 38:
            price = "-$100"
        return name, price, ""

    def _draw_tile_house(self, tx, ty, z, color, scale=1.0, hotel=False):
        sx = 0.07 * scale
        sy = 0.09 * scale
        h = (13 if hotel else 9) * scale
        base = [(tx-sx, ty-sy, z), (tx+sx, ty-sy, z), (tx+sx, ty+sy, z), (tx-sx, ty+sy, z)]
        top = [(x, y, z+h) for x, y, _ in base]
        self._poly_iso([top[1], top[2], base[2], base[1]], "#1f2933", outline="#f8fbfd", width=1)
        self._poly_iso([top[2], top[3], base[3], base[2]], color, outline="#f8fbfd", width=1)
        self._poly_iso(top, "#f8fbfd" if hotel else color, outline="#1f2933", width=1)
        if hotel:
            cx, cy = self.to_iso(tx, ty, z+h+2)
            self.canvas.create_text(cx, cy, text="H", font=("Arial", 7, "bold"),
                                    fill=color, tags="board_item")

    def draw_dynamic(self):
        self.canvas.delete("player_token")
        for idx,pl in enumerate(self.logic.players):
            if hasattr(self,"animating_player") and self.animating_player==idx:
                px,py=self.anim_x,self.anim_y
            else:
                tx,ty=self.get_logical_coords(pl.position)
                ox=0.3+(idx*0.4)
                px,py=self.to_iso(tx+ox,ty+0.5,20)
            self.canvas.create_oval(px-10,py-20,px+10,py,fill=pl.color,outline="white",width=2,tags="player_token")

    def add_log(self, text):
        self.alert_box.config(state=tk.NORMAL)
        self.alert_box.insert(tk.END, text + "\n")
        self.alert_box.see(tk.END)
        self.alert_box.config(state=tk.DISABLED)

    def update_info(self):
        p = self.logic.p
        self.info_label.config(text=f"{p.name}'s Turn | ${p.money}", fg=p.color)
        p1,p2 = self.logic.players
        self.p1_money_lbl.config(text=f"{p1.name}: ${p1.money}")
        self.p2_money_lbl.config(text=f"{p2.name}: ${p2.money}")

    def update_prop_list(self):
        self.prop_list.delete(0, tk.END)
        p = self.logic.p
        for sq in self.logic.get_owned_properties(p):
            n = sq.name.replace(chr(10)," ")
            s = "MORT" if sq.mortgage else f"{sq.house}H" if sq.house>0 else ""
            self.prop_list.insert(tk.END, f"{n} {s}")

    def flush_alerts(self):
        for a in self.logic.alerts:
            self.add_log(a)
        self.logic.alerts.clear()

    def handle_roll(self):
        p = self.logic.p
        if p.jail:
            has_card = p.cc_jail_card or p.chance_jail_card
            JailDialog(self.parent, p, has_card, self._jail_choice)
            return
        self._do_roll()

    def _jail_choice(self, choice):
        p = self.logic.p
        if choice == "pay":
            self.logic.pay_jail_fine(p)
            self.flush_alerts()
            self.update_info()
            self._do_roll()
        elif choice == "card":
            self.logic.use_jail_card(p)
            self.flush_alerts()
            self.update_info()
            self._do_roll()
        else:
            d1,d2 = self.logic.roll_dice()
            self.add_log(f"Rolled {d1}+{d2}={d1+d2}")
            if d1==d2:
                p.jail=False; p.jail_turns=0
                self.add_log(f"{p.name} rolled doubles! Free!")
                self.flush_alerts()
                self._move_player(d1+d2)
            else:
                p.jail_turns+=1
                if p.jail_turns>=3:
                    self.logic.pay_jail_fine(p)
                    self.flush_alerts()
                    self.add_log("Forced to pay $50 after 3 turns.")
                    self._move_player(d1+d2)
                else:
                    self.add_log(f"Still in jail. Turn {p.jail_turns}/3")
                    self.flush_alerts()
                    self.logic.next_turn()
                    self.update_info()
                    self.update_prop_list()
                    self.draw_static_board()
                    self.draw_dynamic()

    def _do_roll(self):
        self.btn_roll.config(state=tk.DISABLED)
        d1,d2 = self.logic.roll_dice()
        self.logic.double_count += 1
        self.add_log(f"Rolled {d1}+{d2}={d1+d2}" + (" DOUBLES!" if d1==d2 else ""))
        if d1==d2 and self.logic.double_count>=3:
            self.add_log(f"{self.logic.p.name} rolled 3 doubles - GO TO JAIL!")
            self.logic.send_to_jail(self.logic.p)
            self.flush_alerts()
            self.draw_dynamic()
            self.update_info()
            self._end_turn()
            return
        self.animate_dice_throw(25, d1, d2)

    def draw_die_face(self, x, y, value):
        s=20
        t1,t2,t3,t4=(x,y-s),(x+s*1.2,y-s*0.4),(x,y+s*0.2),(x-s*1.2,y-s*0.4)
        self.canvas.create_polygon(*t1,*t2,*t3,*t4,fill="white",outline="black",width=2,tags="dice_anim")
        self.canvas.create_polygon(*t4,*t3,(x,y+s*1.4),(x-s*1.2,y+s*0.8),fill="#e0e0e0",outline="black",width=2,tags="dice_anim")
        self.canvas.create_polygon(*t3,*t2,(x+s*1.2,y+s*0.8),(x,y+s*1.4),fill="#ccc",outline="black",width=2,tags="dice_anim")
        r=3
        def pip(px,py):
            ix,iy=x+px*1.2,y-s*0.4+py*0.6
            self.canvas.create_oval(ix-r,iy-r,ix+r,iy+r,fill="black",tags="dice_anim")
        dots={1:[(0,0)],2:[(-4,-4),(4,4)],3:[(-4,-4),(0,0),(4,4)],4:[(-4,-4),(-4,4),(4,-4),(4,4)],5:[(-4,-4),(-4,4),(4,-4),(4,4),(0,0)],6:[(-4,-6),(-4,0),(-4,6),(4,-6),(4,0),(4,6)]}
        for dx,dy in dots.get(value,[]): pip(dx,dy)

    def animate_dice_throw(self, ticks, d1, d2):
        self.canvas.delete("dice_anim")
        if ticks==25:
            self.dice_state={"d1x":self.board_size/2-20,"d1y":self.board_size-100,"d2x":self.board_size/2+20,"d2y":self.board_size-80,"d1vx":-8,"d1vy":-24,"d2vx":-3,"d2vy":-22,"g":2.5}
        if ticks>0:
            st=self.dice_state
            st["d1x"]+=st["d1vx"];st["d1y"]+=st["d1vy"];st["d1vy"]+=st["g"]
            st["d2x"]+=st["d2vx"];st["d2y"]+=st["d2vy"];st["d2vy"]+=st["g"]
            fl=self.board_size/2+30
            if st["d1y"]>fl and st["d1vy"]>0: st["d1y"]=fl;st["d1vy"]=-st["d1vy"]*0.55;st["d1vx"]*=0.65
            if st["d2y"]>fl+20 and st["d2vy"]>0: st["d2y"]=fl+20;st["d2vy"]=-st["d2vy"]*0.55;st["d2vx"]*=0.65
            self.draw_die_face(st["d1x"],st["d1y"],random.randint(1,6))
            self.draw_die_face(st["d2x"],st["d2y"],random.randint(1,6))
            self.parent.after(40,self.animate_dice_throw,ticks-1,d1,d2)
        else:
            self.draw_die_face(self.dice_state["d1x"],self.dice_state["d1y"],d1)
            self.draw_die_face(self.dice_state["d2x"],self.dice_state["d2y"],d2)
            steps=d1+d2
            self.spawn_float(self.board_size/2,self.board_size/2-50,f"MOVE {steps}!","blue")
            self.parent.after(800,lambda:self._move_player(steps))

    def _move_player(self, steps):
        self.canvas.delete("dice_anim")
        self.animating_player=self.logic.turn-1
        self.anim_steps_left=steps
        self.anim_step_progress=0.0
        self.anim_current_space=self.logic.p.position
        self.animating=True
        self._animate_token()

    def _animate_token(self):
        p=self.logic.p
        if self.anim_steps_left<=0:
            self.animating=False
            del self.animating_player
            self.draw_dynamic()
            self._handle_landing(p)
            return
        ns=(self.anim_current_space+1)%40
        self.anim_step_progress+=0.25
        if self.anim_step_progress>=1.0:
            self.anim_current_space=ns; p.position=ns; self.anim_step_progress=0.0; self.anim_steps_left-=1
            if ns==0:
                p.money+=200; self.update_info()
                tx,ty=self.space_centers[0]
                self.spawn_float(tx,ty-30,"+$200 GO","green")
        p1=self.space_centers[self.anim_current_space]; p2=self.space_centers[ns]
        t=self.anim_step_progress
        bx=p1[0]+(p2[0]-p1[0])*t; by=p1[1]+(p2[1]-p1[1])*t
        self.anim_x=bx; self.anim_y=by-15-math.sin(t*math.pi)*20
        self.draw_dynamic()
        self.parent.after(40,self._animate_token)

    def _handle_landing(self, p):
        sp = self.logic.board[p.position]
        tx,ty = self.space_centers[p.position]
        name = sp.name.replace(chr(10)," ")
        self.landed_label.config(text=f"Landed on {name}")
        self.add_log(f"{p.name} landed on {name}")

        # GO TO JAIL
        if p.position == 30:
            self.logic.send_to_jail(p)
            self.spawn_float(tx,ty-30,"JAIL!","red")
            self.flush_alerts()
            self.draw_dynamic()
            self._end_turn()
        # Income Tax
        elif p.position == 4:
            p.money -= 200
            self.spawn_float(tx,ty-30,"-$200","red")
            self.add_log(f"{p.name} paid $200 income tax.")
            self._check_bankrupt_or_end()
        # Luxury Tax
        elif p.position == 38:
            p.money -= 100
            self.spawn_float(tx,ty-30,"-$100","red")
            self.add_log(f"{p.name} paid $100 luxury tax.")
            self._check_bankrupt_or_end()
        # Chance
        elif p.position in (7,22,36):
            self.spawn_float(tx,ty-30,"CHANCE!","blue")
            ci,text,action = self.logic.draw_chance()
            def after_card():
                result,data = self.logic.apply_chance(ci)
                self.flush_alerts()
                self.update_info()
                self.draw_dynamic()
                if result=="jail": self._end_turn()
                elif result in ("land","land_increased"):
                    self.draw_static_board(); self.draw_dynamic()
                    self._handle_landing_after_card(p, result=="land_increased")
                else: self._check_bankrupt_or_end()
            CardDialog(self.parent, "Chance", text, after_card)
        # Community Chest - MINIGAME! Winner gets the card
        elif p.position in (2,17,33):
            self.spawn_float(tx,ty-30,"CHEST BATTLE!","orange")
            ci,text,action = self.logic.draw_community_chest()
            self._pending_cc = (ci, text)
            popup = tk.Toplevel(self.parent)
            popup.title("Community Chest Challenge!")
            popup.geometry("400x180")
            popup.transient(self.parent)
            popup.grab_set()
            tk.Label(popup,text="Community Chest!",font=("Arial",16,"bold"),fg="#e67e22").pack(pady=10)
            tk.Label(popup,text="Win the minigame to claim the reward!",font=("Arial",11)).pack(pady=5)
            tk.Button(popup,text="Play Minigame",font=("Arial",13,"bold"),bg="#2ecc71",fg="white",
                      command=lambda:self._launch_cc_minigame(popup,p)).pack(pady=10)
        # Railroad - MINIGAME
        elif sp.group_number == 1:
            def continue_railroad():
                if sp.owner != 0 and sp.owner != p.index:
                    self.spawn_float(tx,ty-30,"MINIGAME!","orange")
                    popup = tk.Toplevel(self.parent)
                    popup.title("Railroad!")
                    popup.geometry("300x150")
                    tk.Label(popup,text=f"Railroad!\nWin to steal from opponent!").pack(pady=20)
                    tk.Button(popup,text="Play Minigame",command=lambda:self._launch_minigame(popup,p)).pack()
                else:
                    self._end_turn()
            self._show_landing_choices(p, sp, continue_railroad)
        # Utility
        elif sp.group_number == 2:
            self._show_landing_choices(p, sp, lambda: self._continue_property_landing(p, sp))
        # Property
        elif sp.group_number >= 3:
            self._show_landing_choices(p, sp, lambda: self._continue_property_landing(p, sp))
        else:
            self._end_turn()

    def _handle_landing_after_card(self, p, increased):
        sp = self.logic.board[p.position]
        if sp.owner > 0 and sp.owner != p.index:
            self._show_landing_choices(p, sp, lambda: self._continue_property_landing(p, sp, increased))
            return
        elif sp.owner == 0 and sp.price > 0:
            self._show_landing_choices(p, sp, lambda: self._check_bankrupt_or_end())
            return
        elif sp.owner == p.index and sp.price > 0:
            self._show_landing_choices(p, sp, lambda: self._check_bankrupt_or_end())
            return
        self._check_bankrupt_or_end()

    def _continue_property_landing(self, p, sp, increased=False):
        tx,ty = self.space_centers[p.position]
        if sp.owner > 0 and sp.owner != p.index:
            rent = self.logic.calc_rent(sp, increased)
            p.money -= rent
            self.logic.players[sp.owner-1].money += rent
            self.spawn_float(tx,ty-30,f"-${rent}","red")
            self.add_log(f"{p.name} paid ${rent} rent to {self.logic.players[sp.owner-1].name}")
            self._check_bankrupt_or_end()
        else:
            self._end_turn()

    def _show_landing_choices(self, p, sp, continue_action):
        name = sp.name.replace(chr(10), " ")
        option2_label, option2_allowed = self._landing_option2_state(p, sp)
        option3_label, option3_allowed = self._landing_option3_state(p, sp)

        popup = tk.Toplevel(self.parent)
        popup.title("Tile Options")
        popup.transient(self.parent)
        popup.grab_set()
        popup.resizable(False, False)

        frame = tk.Frame(popup, bg="#f8fbfd", padx=18, pady=16)
        frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame, text=name, font=("Arial", 14, "bold"),
                 bg="#f8fbfd", fg="#1f2933", wraplength=300).pack(pady=(0, 6))
        tk.Label(frame, text=f"{p.name}: choose action", font=("Arial", 10),
                 bg="#f8fbfd", fg="#405155").pack(pady=(0, 12))

        def finish(action):
            popup.grab_release()
            popup.destroy()
            action()

        tk.Button(frame, text="1. Continue", font=("Arial", 11, "bold"),
                  bg="#40546a", fg="white", activebackground="#314153",
                  activeforeground="white", relief=tk.FLAT,
                  command=lambda: finish(continue_action)).pack(fill=tk.X, pady=4)

        b2 = tk.Button(frame, text=f"2. {option2_label}", font=("Arial", 11, "bold"),
                       bg="#2ecc71", fg="white", activebackground="#27ae60",
                       activeforeground="white", relief=tk.FLAT,
                       command=lambda: finish(lambda: self._landing_buy_or_upgrade(p, sp)))
        b2.pack(fill=tk.X, pady=4)
        if not option2_allowed:
            b2.config(state=tk.DISABLED, bg="#b9c1c4", disabledforeground="#eef4f7")

        b3 = tk.Button(frame, text=f"3. {option3_label}", font=("Arial", 11, "bold"),
                       bg="#e67e22", fg="white", activebackground="#ca6f1e",
                       activeforeground="white", relief=tk.FLAT,
                       command=lambda: finish(lambda: self._landing_sell(p, sp)))
        b3.pack(fill=tk.X, pady=4)
        if not option3_allowed:
            b3.config(state=tk.DISABLED, bg="#b9c1c4", disabledforeground="#eef4f7")

        popup.protocol("WM_DELETE_WINDOW", lambda: finish(continue_action))
        popup.update_idletasks()
        x = self.parent.winfo_rootx() + max(0, (self.parent.winfo_width() - popup.winfo_width()) // 2)
        y = self.parent.winfo_rooty() + max(0, (self.parent.winfo_height() - popup.winfo_height()) // 2)
        popup.geometry(f"+{x}+{y}")

    def _landing_option2_state(self, p, sp):
        if sp.owner == 0 and sp.price > 0:
            if p.money >= sp.price:
                return f"Buy for ${sp.price}", True
            return f"Buy for ${sp.price}", False
        if sp.owner == p.index and sp.group_number >= 3:
            if sp.house >= 5:
                return "Upgrade (Max)", False
            label = "Upgrade to Hotel" if sp.house == 4 else "Upgrade House"
            return f"{label} (${sp.house_price})", p.money >= sp.house_price
        return "Buy / Upgrade", False

    def _landing_option3_state(self, p, sp):
        if sp.owner != p.index or sp.price <= 0:
            return "Sell", False
        if sp.group_number >= 3 and sp.house > 0:
            return f"Sell Upgrade (+${sp.house_price // 2})", True
        return f"Sell Property (+${sp.price // 2})", True

    def _landing_buy_or_upgrade(self, p, sp):
        if sp.owner == 0 and sp.price > 0:
            self.logic.buy_property(p, sp)
        elif sp.owner == p.index and sp.group_number >= 3 and sp.house < 5 and p.money >= sp.house_price:
            self.logic.do_buy_house(sp)
        self.flush_alerts()
        self.update_info()
        self.update_prop_list()
        self.draw_static_board()
        self.draw_dynamic()
        self._end_turn()

    def _landing_sell(self, p, sp):
        name = sp.name.replace(chr(10), " ")
        if sp.owner != p.index or sp.price <= 0:
            self._end_turn()
            return
        if sp.group_number >= 3 and sp.house > 0:
            kind = "hotel" if sp.house == 5 else "house"
            sp.house -= 1
            p.money += sp.house_price // 2
            self.logic.add_alert(f"{p.name} sold a {kind} on {name}.")
        else:
            refund = sp.price // 2
            sp.owner = 0
            sp.house = 0
            sp.mortgage = False
            p.money += refund
            self.logic.add_alert(f"{p.name} sold {name} back to the bank for ${refund}.")
        self.flush_alerts()
        self.update_info()
        self.update_prop_list()
        self.draw_static_board()
        self.draw_dynamic()
        self._end_turn()

    def _launch_minigame(self, popup, player):
        popup.destroy()
        games = [TypingRaceDialog, PingPongDialog, QuickMathDialog, CoinCatcherDialog,
                 PacmanDialog, SnakeRaceDialog]
        mg = random.choice(games)
        def on_end(winner):
            wp = self.logic.players[winner-1]
            op = self.logic.players[1 if winner==1 else 0]
            steal = min(500, op.money)
            wp.money += steal; op.money -= steal
            tx,ty = self.space_centers[wp.position]
            self.spawn_float(tx,ty-40,f"+${steal} HEIST!","green")
            messagebox.showinfo("Heist!", f"{wp.name} won and stole ${steal} from {op.name}!")
            self._end_turn()
        mg(self.parent, on_end)

    def _check_bankrupt_or_end(self):
        self.update_info()
        p = self.logic.p
        if self.logic.check_bankruptcy(p):
            # Try auto-selling houses first
            for sq in self.logic.board:
                if p.money >= 0: break
                if sq.owner == p.index and self.logic.can_sell_house(sq):
                    self.logic.do_sell_house(sq)
            self.flush_alerts(); self.update_info(); self.draw_static_board()
            if p.money < 0:
                messagebox.showinfo("Bankrupt!", f"{p.name} is bankrupt!")
                self.logic.force_bankruptcy(p)
                self.flush_alerts(); self.update_info(); self.draw_static_board()
                messagebox.showinfo("Game Over!", f"{self.logic.winner.name} wins the game!")
                self.btn_roll.config(state=tk.DISABLED)
                return
        self._end_turn()

    def _end_turn(self):
        self.update_info()
        self.draw_static_board()
        self.draw_dynamic()
        self.update_prop_list()
        if self.logic.is_doubles() and self.logic.double_count < 3 and not self.logic.p.jail:
            self.add_log("Doubles! Roll again.")
            self.btn_roll.config(state=tk.NORMAL)
        else:
            self.logic.next_turn()
            self.logic.double_count = 0
            self.update_info()
            self.update_prop_list()
            self.draw_static_board()
            self.draw_dynamic()
            self.btn_roll.config(state=tk.NORMAL)

    def buy_house(self):
        sel = self.prop_list.curselection()
        if not sel: return
        props = self.logic.get_owned_properties(self.logic.p)
        if sel[0] >= len(props): return
        sq = props[sel[0]]
        if self.logic.can_buy_house(sq):
            self.logic.do_buy_house(sq)
            self.flush_alerts()
            self.update_info(); self.update_prop_list(); self.draw_static_board()
        else:
            messagebox.showwarning("Cannot", "Cannot buy house here.\nNeed full color group, even building.")

    def sell_house(self):
        sel = self.prop_list.curselection()
        if not sel: return
        props = self.logic.get_owned_properties(self.logic.p)
        if sel[0] >= len(props): return
        sq = props[sel[0]]
        if self.logic.can_sell_house(sq):
            self.logic.do_sell_house(sq)
            self.flush_alerts()
            self.update_info(); self.update_prop_list(); self.draw_static_board()
        else:
            messagebox.showwarning("Cannot", "Cannot sell house here.")

    def _launch_cc_minigame(self, popup, player):
        popup.destroy()
        games = [TypingRaceDialog, PingPongDialog, QuickMathDialog, CoinCatcherDialog,
                 PacmanDialog, SnakeRaceDialog]
        ci, text = self._pending_cc
        mg = random.choice(games)
        def on_end(winner):
            wp = self.logic.players[winner-1]
            self.add_log(f"{wp.name} won the Community Chest challenge!")
            # Apply card to winner: temporarily set turn to winner
            old_turn = self.logic.turn
            self.logic.turn = wp.index
            result, data = self.logic.apply_community_chest(ci)
            self.logic.turn = old_turn
            self.flush_alerts()
            CardDialog(self.parent, "Community Chest", f"{wp.name} wins!\n\n{text}",
                       lambda: self._after_cc_minigame(result, data, player))
        mg(self.parent, on_end)

    def _after_cc_minigame(self, result, data, p):
        self.update_info()
        self.draw_dynamic()
        if result == "jail":
            self._end_turn()
        elif result == "land":
            self.draw_static_board(); self.draw_dynamic()
            self._handle_landing_after_card(p, False)
        else:
            self._check_bankrupt_or_end()

    def resign(self):
        if messagebox.askyesno("Resign", f"{self.logic.p.name}, resign?"):
            self.logic.force_bankruptcy(self.logic.p)
            self.flush_alerts(); self.update_info(); self.draw_static_board()
            messagebox.showinfo("Game Over!", f"{self.logic.winner.name} wins!")
            self.btn_roll.config(state=tk.DISABLED)
