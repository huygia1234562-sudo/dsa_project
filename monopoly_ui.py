import tkinter as tk
from tkinter import messagebox
import random, math
from monopoly_logic import MonopolyLogic
from monopoly_dialogs import CardDialog, JailDialog
from minigame_ui import (
    TypingRaceDialog, PingPongDialog, QuickMathDialog, CoinCatcherDialog,
    MemoryCardDialog, PacmanDialog, ChickenCrossDialog, MazeEscapeDialog,
    WordBuilderDialog, SnakeRaceDialog
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
        self.setup_ui()
        self.draw_static_board()
        self.draw_dynamic()
        self.update_info()
        self.update_prop_list()
        self.animate_tick()

    def setup_ui(self):
        self.toolbar = tk.Frame(self.parent, bg="#2c3e50", height=50)
        self.toolbar.pack(fill=tk.X)
        self.toolbar.pack_propagate(False)
        tk.Button(self.toolbar, text="< Back", command=self.on_back, bg="#34495e", fg="white",
                  font=("Arial",10)).pack(side=tk.LEFT, padx=10, pady=10)
        self.info_label = tk.Label(self.toolbar, text="", font=("Arial", 13, "bold"), bg="#2c3e50", fg="white")
        self.info_label.pack(side=tk.LEFT, padx=20)
        # Money displays
        mf = tk.Frame(self.toolbar, bg="#2c3e50")
        mf.pack(side=tk.RIGHT, padx=10)
        self.p1_money_lbl = tk.Label(mf, text="P1: $1500", font=("Arial",11,"bold"), fg="#e63946", bg="#2c3e50")
        self.p1_money_lbl.pack(side=tk.LEFT, padx=8)
        self.p2_money_lbl = tk.Label(mf, text="P2: $1500", font=("Arial",11,"bold"), fg="#457b9d", bg="#2c3e50")
        self.p2_money_lbl.pack(side=tk.LEFT, padx=8)

        self.body_frame = tk.Frame(self.parent, bg="#eef2f3")
        self.body_frame.pack(expand=True, fill=tk.BOTH)
        self.canvas = tk.Canvas(self.body_frame, bg="#cbf0cd", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", self.on_resize)
        self.board_size = 1100
        self.space_size = self.board_size / 11

        self.btn_roll = tk.Button(self.canvas, text="ROLL", font=("Arial",14,"bold"),
            bg="#e63946", fg="white", activebackground="#d62828", relief=tk.RAISED, bd=5, command=self.handle_roll)
        self.btn_roll.place(x=self.board_size-130, y=self.board_size-130, width=100, height=100)

        # Right panel
        self.right_panel = tk.Frame(self.body_frame, bg="white", width=280)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.right_panel.pack_propagate(False)

        # Alert log
        tk.Label(self.right_panel, text="Game Log", font=("Arial",12,"bold"), bg="white").pack(pady=5)
        self.alert_box = tk.Text(self.right_panel, font=("Arial",9), height=6, width=30, state=tk.DISABLED, wrap=tk.WORD)
        self.alert_box.pack(padx=5, fill=tk.X)

        # Landed info
        self.landed_label = tk.Label(self.right_panel, text="", font=("Arial",10), bg="#f0f0f0",
                                     wraplength=260, justify=tk.CENTER)
        self.landed_label.pack(fill=tk.X, padx=5, pady=5)

        # Properties
        tk.Label(self.right_panel, text="Your Properties", font=("Arial",12,"bold"), bg="white").pack(pady=5)
        self.prop_list = tk.Listbox(self.right_panel, font=("Arial",9), height=8)
        self.prop_list.pack(fill=tk.X, padx=5)

        # Buttons frame
        bf = tk.Frame(self.right_panel, bg="white")
        bf.pack(fill=tk.X, padx=5, pady=3)
        self.btn_buy_house = tk.Button(bf, text="Buy House", font=("Arial",9), bg="#2ecc71", fg="white",
                                        command=self.buy_house)
        self.btn_buy_house.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        self.btn_sell_house = tk.Button(bf, text="Sell House", font=("Arial",9), bg="#e67e22", fg="white",
                                        command=self.sell_house)
        self.btn_sell_house.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)



        self.btn_resign = tk.Button(self.right_panel, text="Resign", font=("Arial",9),
                                     bg="#e74c3c", fg="white", command=self.resign)
        self.btn_resign.pack(fill=tk.X, padx=5, pady=5)

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

    def draw_static_board(self):
        self.canvas.delete("board_item")
        cb1,cb2,cb3,cb4=self.to_iso(1,1,0),self.to_iso(10,1,0),self.to_iso(10,10,0),self.to_iso(1,10,0)
        self.canvas.create_polygon(cb1[0],cb1[1],cb2[0],cb2[1],cb3[0],cb3[1],cb4[0],cb4[1],fill="#9ec52d",outline="#9ec52d",tags="board_item")
        mb1,mb2,mb3,mb4=self.to_iso(2,4.5,1),self.to_iso(9,4.5,1),self.to_iso(9,6.5,1),self.to_iso(2,6.5,1)
        self.canvas.create_polygon(mb1[0],mb1[1],mb2[0],mb2[1],mb3[0],mb3[1],mb4[0],mb4[1],fill="#e9322e",outline="white",width=4,tags="board_item")
        tx,ty=self.to_iso(5.5,5.5,5)
        self.canvas.create_text(tx,ty,text="MONOPOLY",font=("Arial",26,"bold"),fill="white",angle=28,tags="board_item")
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
            self.canvas.create_polygon(c1[0],c1[1],b1[0],b1[1],b2[0],b2[1],c2[0],c2[1],fill="#777",outline="black",tags="board_item")
            self.canvas.create_polygon(c2[0],c2[1],b2[0],b2[1],b3[0],b3[1],c3[0],c3[1],fill="#555",outline="black",tags="board_item")
            self.canvas.create_polygon(c4[0],c4[1],b4[0],b4[1],b1[0],b1[1],c1[0],c1[1],fill="#999",outline="black",tags="board_item")
            self.canvas.create_polygon(c3[0],c3[1],b3[0],b3[1],b4[0],b4[1],c4[0],c4[1],fill="#666",outline="black",tags="board_item")
            fill_col = "#d0d0d0" if sp.mortgage else col
            self.canvas.create_polygon(c1[0],c1[1],c2[0],c2[1],c3[0],c3[1],c4[0],c4[1],fill=fill_col,outline="black",tags="board_item")
            if sp.owner>0:
                pc=self.logic.players[sp.owner-1].color
                self.canvas.create_polygon(c1[0],c1[1],c2[0],c2[1],c3[0],c3[1],c4[0],c4[1],fill=pc,outline="black",stipple="gray50",tags="board_item")
            dt=sp.name
            if sp.price>0 and sp.group_number>=3:
                dt+=f"\n${sp.price}"
                if sp.house==5: dt+="\nHOTEL"
                elif sp.house>0: dt+=f"\n{sp.house}H"
            elif sp.group_number in (1,2) and sp.price>0: dt+=f"\n${sp.price}"
            elif i==4: dt+="\n-$200"
            elif i==38: dt+="\n-$100"
            ct_x,ct_y=self.to_iso(tx2+0.5,ty2+0.5,zt+4)
            self.canvas.create_text(ct_x,ct_y,text=dt,font=("Arial",6,"bold"),justify=tk.CENTER,tags="board_item")
            # Draw houses
            if sp.house>0 and sp.house<5:
                for h in range(sp.house):
                    hx,hy=self.to_iso(tx2+0.15+h*0.2,ty2+0.15,zt+2)
                    self.canvas.create_rectangle(hx-3,hy-5,hx+3,hy,fill="#2ecc71",outline="black",tags="board_item")
            elif sp.house==5:
                hx,hy=self.to_iso(tx2+0.5,ty2+0.15,zt+2)
                self.canvas.create_rectangle(hx-5,hy-6,hx+5,hy,fill="#e74c3c",outline="black",tags="board_item")
            self.space_centers[i]=(ct_x,ct_y)

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
            if sp.owner == 0:
                self._offer_buy(p, sp)
            elif sp.owner != p.index:
                self.spawn_float(tx,ty-30,"MINIGAME!","orange")
                popup = tk.Toplevel(self.parent)
                popup.title("Railroad!")
                popup.geometry("300x150")
                tk.Label(popup,text=f"Railroad!\nWin to steal from opponent!").pack(pady=20)
                tk.Button(popup,text="Play Minigame",command=lambda:self._launch_minigame(popup,p)).pack()
            else:
                self._end_turn()
        # Utility
        elif sp.group_number == 2:
            if sp.owner == 0:
                self._offer_buy(p, sp)
            elif sp.owner != p.index:
                rent = self.logic.calc_rent(sp)
                p.money -= rent
                self.logic.players[sp.owner-1].money += rent
                self.spawn_float(tx,ty-30,f"-${rent}","red")
                self.add_log(f"{p.name} paid ${rent} rent to {self.logic.players[sp.owner-1].name}")
                self._check_bankrupt_or_end()
            else:
                self._end_turn()
        # Property
        elif sp.group_number >= 3:
            if sp.owner == 0:
                self._offer_buy(p, sp)
            elif sp.owner != p.index:
                rent = self.logic.calc_rent(sp)
                p.money -= rent
                self.logic.players[sp.owner-1].money += rent
                self.spawn_float(tx,ty-30,f"-${rent}","red")
                self.add_log(f"{p.name} paid ${rent} rent to {self.logic.players[sp.owner-1].name}")
                self._check_bankrupt_or_end()
            else:
                self._end_turn()
        else:
            self._end_turn()

    def _handle_landing_after_card(self, p, increased):
        sp = self.logic.board[p.position]
        if sp.owner > 0 and sp.owner != p.index:
            rent = self.logic.calc_rent(sp, increased)
            p.money -= rent
            self.logic.players[sp.owner-1].money += rent
            tx,ty = self.space_centers[p.position]
            self.spawn_float(tx,ty-30,f"-${rent}","red")
            self.add_log(f"{p.name} paid ${rent} rent.")
        elif sp.owner == 0 and sp.price > 0:
            self._offer_buy(p, sp)
            return
        self._check_bankrupt_or_end()

    def _offer_buy(self, p, sp):
        name = sp.name.replace(chr(10)," ")
        if p.money >= sp.price:
            if messagebox.askyesno("Buy Property?", f"Buy {name} for ${sp.price}?\n\nYou have ${p.money}"):
                self.logic.buy_property(p, sp)
                self.flush_alerts()
                self.draw_static_board()
                self.update_info()
        self._end_turn()

    def _launch_minigame(self, popup, player):
        popup.destroy()
        games = [TypingRaceDialog, PingPongDialog, QuickMathDialog, CoinCatcherDialog,
                 MemoryCardDialog, PacmanDialog, ChickenCrossDialog, MazeEscapeDialog,
                 WordBuilderDialog, SnakeRaceDialog]
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
                 MemoryCardDialog, PacmanDialog, ChickenCrossDialog, MazeEscapeDialog,
                 WordBuilderDialog, SnakeRaceDialog]
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
