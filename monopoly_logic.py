import random

class Space:
    """Represents a single square on the Monopoly board."""
    def __init__(self, index, name, price_text, color, price=0, group_number=0,
                 base_rent=0, rent1=0, rent2=0, rent3=0, rent4=0, rent5=0):
        self.index = index
        self.name = name
        self.price_text = price_text
        self.color = color
        self.price = price
        self.group_number = group_number  # 0=special, 1=railroad, 2=utility, 3-10=property
        self.rent = [base_rent, rent1, rent2, rent3, rent4, rent5]
        self.owner = 0  # 0=unowned, 1 or 2=player index
        self.house = 0  # 0-4 houses, 5=hotel
        self.mortgage = False
        self.group = []  # indices sharing same group_number
        if group_number in (3, 4):
            self.house_price = 50
        elif group_number in (5, 6):
            self.house_price = 100
        elif group_number in (7, 8):
            self.house_price = 150
        elif group_number in (9, 10):
            self.house_price = 200
        else:
            self.house_price = 0


class Player:
    """Represents a player in the game."""
    def __init__(self, name, color, index):
        self.name = name
        self.color = color
        self.index = index
        self.position = 0
        self.money = 1500
        self.jail = False
        self.jail_turns = 0
        self.cc_jail_card = False
        self.chance_jail_card = False
        self.creditor = 0


class MonopolyLogic:
    """Complete Monopoly game logic matching the classic board game rules."""
    BOARD_DATA = [
        # (name, price_text, color, price, group, base, r1, r2, r3, r4, r5)
        ("GO", "COLLECT $200", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Mediterranean\nAvenue", "$60", "#8B4513", 60, 3, 2,10,30,90,160,250),
        ("Community\nChest", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Baltic\nAvenue", "$60", "#8B4513", 60, 3, 4,20,60,180,320,450),
        ("Income\nTax", "Pay $200", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Reading\nRailroad", "$200", "#FFFFFF", 200, 1, 0,0,0,0,0,0),
        ("Oriental\nAvenue", "$100", "#87CEEB", 100, 4, 6,30,90,270,400,550),
        ("Chance", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Vermont\nAvenue", "$100", "#87CEEB", 100, 4, 6,30,90,270,400,550),
        ("Connecticut\nAvenue", "$120", "#87CEEB", 120, 4, 8,40,100,300,450,600),
        ("JAIL /\nVisiting", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("St. Charles\nPlace", "$140", "#D02090", 140, 5, 10,50,150,450,625,750),
        ("Electric\nCompany", "$150", "#FFFFFF", 150, 2, 0,0,0,0,0,0),
        ("States\nAvenue", "$140", "#D02090", 140, 5, 10,50,150,450,625,750),
        ("Virginia\nAvenue", "$160", "#D02090", 160, 5, 12,60,180,500,700,900),
        ("Pennsylvania\nRailroad", "$200", "#FFFFFF", 200, 1, 0,0,0,0,0,0),
        ("St. James\nPlace", "$180", "#FFA500", 180, 6, 14,70,200,550,750,950),
        ("Community\nChest", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Tennessee\nAvenue", "$180", "#FFA500", 180, 6, 14,70,200,550,750,950),
        ("New York\nAvenue", "$200", "#FFA500", 200, 6, 16,80,220,600,800,1000),
        ("Free\nParking", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Kentucky\nAvenue", "$220", "#FF0000", 220, 7, 18,90,250,700,875,1050),
        ("Chance", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Indiana\nAvenue", "$220", "#FF0000", 220, 7, 18,90,250,700,875,1050),
        ("Illinois\nAvenue", "$240", "#FF0000", 240, 7, 20,100,300,750,925,1100),
        ("B. & O.\nRailroad", "$200", "#FFFFFF", 200, 1, 0,0,0,0,0,0),
        ("Atlantic\nAvenue", "$260", "#FFFF00", 260, 8, 22,110,330,800,975,1150),
        ("Ventnor\nAvenue", "$260", "#FFFF00", 260, 8, 22,110,330,800,975,1150),
        ("Water\nWorks", "$150", "#FFFFFF", 150, 2, 0,0,0,0,0,0),
        ("Marvin\nGardens", "$280", "#FFFF00", 280, 8, 24,120,360,850,1025,1200),
        ("GO TO\nJAIL", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Pacific\nAvenue", "$300", "#008000", 300, 9, 26,130,390,900,1100,1275),
        ("North Carolina\nAvenue", "$300", "#008000", 300, 9, 26,130,390,900,1100,1275),
        ("Community\nChest", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Pennsylvania\nAvenue", "$320", "#008000", 320, 9, 28,150,450,1000,1200,1400),
        ("Short\nLine", "$200", "#FFFFFF", 200, 1, 0,0,0,0,0,0),
        ("Chance", "", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Park\nPlace", "$350", "#0000FF", 350, 10, 35,175,500,1100,1300,1500),
        ("Luxury\nTax", "Pay $100", "#FFFFFF", 0, 0, 0,0,0,0,0,0),
        ("Boardwalk", "$400", "#0000FF", 400, 10, 50,200,600,1400,1700,2000),
    ]

    CHANCE_CARDS = [
        ("GET OUT OF JAIL FREE.\nThis card may be kept until needed.", "jail_card"),
        ("Make General Repairs on All Your Property.\nFor each house pay $25. For each hotel $100.", "repairs"),
        ("Speeding fine $15.", "fine"),
        ("You have been elected Chairman of the Board.\nPay each player $50.", "pay_each"),
        ("Go back three spaces.", "go_back_3"),
        ("ADVANCE TO THE NEAREST UTILITY.\nIf UNOWNED, you may buy it.\nIf OWNED, throw dice and pay owner 10x amount.", "nearest_utility"),
        ("Bank pays you dividend of $50.", "dividend"),
        ("ADVANCE TO THE NEAREST RAILROAD.\nIf UNOWNED, you may buy it.\nIf OWNED, pay owner twice the rental.", "nearest_railroad"),
        ("Pay poor tax of $15.", "poor_tax"),
        ("Take a trip to Reading Railroad.\nIf you pass GO collect $200.", "advance_to"),
        ("ADVANCE to Boardwalk.", "advance_to"),
        ("ADVANCE to Illinois Avenue.\nIf you pass GO collect $200.", "advance_to"),
        ("Your building loan matures. Collect $150.", "collect"),
        ("ADVANCE TO THE NEAREST RAILROAD.\n(Pay owner twice the rental if owned.)", "nearest_railroad"),
        ("ADVANCE to St. Charles Place.\nIf you pass GO collect $200.", "advance_to"),
        ("Go to Jail. Go directly to Jail.\nDo not pass GO. Do not collect $200.", "go_to_jail"),
    ]

    # Destinations for "advance_to" chance cards (indices 9,10,11,14)
    CHANCE_DESTINATIONS = {9: 5, 10: 39, 11: 24, 14: 11}
    # Repair costs for chance card index 1
    CHANCE_REPAIR_COSTS = (25, 100)
    # Fine amounts
    CHANCE_FINE = {2: 15, 8: 15}
    CHANCE_PAY_EACH = {3: 50}
    CHANCE_COLLECT = {6: 50, 12: 150}

    CC_CARDS = [
        ("Get Out of Jail Free.\nThis card may be kept until needed.", "jail_card"),
        ("You have won second prize in a beauty contest.\nCollect $10.", "collect"),
        ("From sale of stock you get $50.", "collect"),
        ("Life insurance matures. Collect $100.", "collect"),
        ("Income tax refund. Collect $20.", "collect"),
        ("Holiday fund matures. Receive $100.", "collect"),
        ("You inherit $100.", "collect"),
        ("Receive $25 consultancy fee.", "collect"),
        ("Pay hospital fees of $100.", "pay"),
        ("Bank error in your favor. Collect $200.", "collect"),
        ("Pay school fees of $50.", "pay"),
        ("Doctor's fee. Pay $50.", "pay"),
        ("It is your birthday.\nCollect $10 from every player.", "collect_from_each"),
        ("Advance to GO. (Collect $200)", "advance_go"),
        ("You are assessed for street repairs.\n$40 per house. $115 per hotel.", "repairs"),
        ("Go to Jail. Go directly to Jail.\nDo not pass GO. Do not collect $200.", "go_to_jail"),
    ]
    CC_COLLECT = {1: 10, 2: 50, 3: 100, 4: 20, 5: 100, 6: 100, 7: 25, 9: 200}
    CC_PAY = {8: 100, 10: 50, 11: 50}
    CC_COLLECT_EACH = {12: 10}
    CC_REPAIR_COSTS = (40, 115)

    def __init__(self):
        self.players = [Player("Player 1", "#e63946", 1), Player("Player 2", "#457b9d", 2)]
        self.turn = 1
        self.double_count = 0
        self.dice = (0, 0)
        self.board = [Space(i, *d) for i, d in enumerate(self.BOARD_DATA)]
        self._init_groups()
        self.chance_deck = list(range(16))
        random.shuffle(self.chance_deck)
        self.chance_idx = 0
        self.cc_deck = list(range(16))
        random.shuffle(self.cc_deck)
        self.cc_idx = 0
        self.game_over = False
        self.winner = None
        self.alerts = []

    @property
    def p(self):
        return self.players[self.turn - 1]

    def other(self, player=None):
        if player is None:
            player = self.p
        return self.players[0] if player.index == 2 else self.players[1]

    def _init_groups(self):
        groups = {}
        for sq in self.board:
            if sq.group_number > 0:
                groups.setdefault(sq.group_number, []).append(sq.index)
        for sq in self.board:
            if sq.group_number > 0:
                sq.group = groups[sq.group_number]

    def add_alert(self, text):
        self.alerts.append(text)

    def roll_dice(self):
        self.dice = (random.randint(1, 6), random.randint(1, 6))
        return self.dice

    def is_doubles(self):
        return self.dice[0] == self.dice[1]

    def dice_sum(self):
        return self.dice[0] + self.dice[1]

    def next_turn(self):
        self.turn = 2 if self.turn == 1 else 1
        self.double_count = 0

    # ── Rent Calculation ──

    def calc_rent(self, sq, increased_rent=False):
        """Calculate rent for a space. increased_rent is for Chance card effects."""
        if sq.mortgage:
            return 0
        if sq.group_number == 1:  # Railroad
            if increased_rent:
                base = 25
            else:
                base = 12.5
            count = sum(1 for idx in sq.group if self.board[idx].owner == sq.owner)
            return int(base * (2 ** count))
        elif sq.group_number == 2:  # Utility
            dice_total = self.dice_sum()
            other_util = 12 if sq.index == 28 else 28
            if increased_rent or self.board[other_util].owner == sq.owner:
                return dice_total * 10
            else:
                return dice_total * 4
        elif sq.group_number >= 3:  # Property
            if sq.house > 0:
                return sq.rent[min(sq.house, 5)]
            group_owned = all(self.board[idx].owner == sq.owner for idx in sq.group)
            if group_owned:
                return sq.rent[0] * 2
            return sq.rent[0]
        return 0

    # ── Property Actions ──

    def can_buy_property(self, sq):
        return sq.price > 0 and sq.owner == 0

    def buy_property(self, player, sq):
        if player.money >= sq.price and sq.owner == 0:
            player.money -= sq.price
            sq.owner = player.index
            self.add_alert(f"{player.name} bought {sq.name.replace(chr(10),' ')} for ${sq.price}.")
            return True
        return False



    # ── Housing ──

    def total_houses(self):
        return sum(sq.house for sq in self.board if sq.house < 5)

    def total_hotels(self):
        return sum(1 for sq in self.board if sq.house == 5)

    def can_buy_house(self, sq):
        if sq.group_number < 3 or sq.owner == 0:
            return False
        if sq.house >= 5:
            return False
        p = self.players[sq.owner - 1]
        if p.money < sq.house_price:
            return False
        # All group must be owned by same player
        for idx in sq.group:
            s = self.board[idx]
            if s.owner != sq.owner:
                return False
        # Even building: this property can't have more houses than any other in group
        min_houses = min(self.board[idx].house for idx in sq.group)
        if sq.house > min_houses:
            return False
        # Global limits
        if sq.house < 4 and self.total_houses() >= 32:
            return False
        if sq.house == 4 and self.total_hotels() >= 12:
            return False
        return True

    def do_buy_house(self, sq):
        p = self.players[sq.owner - 1]
        p.money -= sq.house_price
        sq.house += 1
        kind = "hotel" if sq.house == 5 else "house"
        self.add_alert(f"{p.name} placed a {kind} on {sq.name.replace(chr(10),' ')}.")

    def can_sell_house(self, sq):
        if sq.group_number < 3 or sq.house <= 0:
            return False
        max_houses = max(self.board[idx].house for idx in sq.group)
        if sq.house < max_houses:
            return False
        return True

    def do_sell_house(self, sq):
        p = self.players[sq.owner - 1]
        kind = "hotel" if sq.house == 5 else "house"
        sq.house -= 1
        p.money += sq.house_price // 2
        self.add_alert(f"{p.name} sold a {kind} on {sq.name.replace(chr(10),' ')}.")


    # ── Jail ──

    def send_to_jail(self, player):
        player.position = 10
        player.jail = True
        player.jail_turns = 0
        self.double_count = 0
        self.add_alert(f"{player.name} was sent to Jail!")

    def pay_jail_fine(self, player):
        player.money -= 50
        player.jail = False
        player.jail_turns = 0
        self.add_alert(f"{player.name} paid $50 to get out of jail.")

    def use_jail_card(self, player):
        player.jail = False
        player.jail_turns = 0
        if player.cc_jail_card:
            player.cc_jail_card = False
            self.cc_deck.insert(self.cc_idx, 0)
            self.cc_idx = (self.cc_idx + 1) % len(self.cc_deck)
        elif player.chance_jail_card:
            player.chance_jail_card = False
            self.chance_deck.insert(self.chance_idx, 0)
            self.chance_idx = (self.chance_idx + 1) % len(self.chance_deck)
        self.add_alert(f'{player.name} used a "Get Out of Jail Free" card.')

    # ── Card Drawing ──

    def draw_chance(self):
        card_idx = self.chance_deck[self.chance_idx]
        text, action = self.CHANCE_CARDS[card_idx]
        if action == "jail_card":
            self.chance_deck.pop(self.chance_idx)
            if self.chance_idx >= len(self.chance_deck):
                self.chance_idx = 0
        else:
            self.chance_idx = (self.chance_idx + 1) % len(self.chance_deck)
        return card_idx, text, action

    def draw_community_chest(self):
        card_idx = self.cc_deck[self.cc_idx]
        text, action = self.CC_CARDS[card_idx]
        if action == "jail_card":
            self.cc_deck.pop(self.cc_idx)
            if self.cc_idx >= len(self.cc_deck):
                self.cc_idx = 0
        else:
            self.cc_idx = (self.cc_idx + 1) % len(self.cc_deck)
        return card_idx, text, action

    def apply_chance(self, card_idx):
        """Apply a Chance card effect. Returns (action_type, extra_data) for UI to handle."""
        p = self.p
        _, action = self.CHANCE_CARDS[card_idx]

        if action == "jail_card":
            p.chance_jail_card = True
            return ("done", None)
        elif action == "go_to_jail":
            self.send_to_jail(p)
            return ("jail", None)
        elif action == "go_back_3":
            p.position -= 3
            return ("land", p.position)
        elif action == "advance_to":
            dest = self.CHANCE_DESTINATIONS[card_idx]
            if p.position > dest:
                p.money += 200
                self.add_alert(f"{p.name} collected $200 for passing GO.")
            p.position = dest
            return ("land", dest)
        elif action == "nearest_railroad":
            pos = p.position
            rr = [5, 15, 25, 35]
            dest = next((r for r in rr if r > pos), rr[0])
            if dest <= pos:
                p.money += 200
                self.add_alert(f"{p.name} collected $200 for passing GO.")
            p.position = dest
            return ("land_increased", dest)
        elif action == "nearest_utility":
            pos = p.position
            if pos < 12 or pos >= 28:
                dest = 12
            else:
                dest = 28
            if dest < pos:
                p.money += 200
                self.add_alert(f"{p.name} collected $200 for passing GO.")
            p.position = dest
            return ("land_increased", dest)
        elif action == "repairs":
            cost = self._calc_repairs(p, 25, 100)
            p.money -= cost
            self.add_alert(f"{p.name} paid ${cost} for street repairs.")
            return ("done", None)
        elif action == "fine" or action == "poor_tax":
            amt = self.CHANCE_FINE.get(card_idx, 15)
            p.money -= amt
            self.add_alert(f"{p.name} paid ${amt}.")
            return ("done", None)
        elif action == "pay_each":
            amt = self.CHANCE_PAY_EACH.get(card_idx, 50)
            other = self.other(p)
            p.money -= amt
            other.money += amt
            self.add_alert(f"{p.name} paid ${amt} to {other.name}.")
            return ("done", None)
        elif action == "dividend" or action == "collect":
            amt = self.CHANCE_COLLECT.get(card_idx, 50)
            p.money += amt
            self.add_alert(f"{p.name} collected ${amt}.")
            return ("done", None)
        return ("done", None)

    def apply_community_chest(self, card_idx):
        """Apply a Community Chest card effect."""
        p = self.p
        _, action = self.CC_CARDS[card_idx]

        if action == "jail_card":
            p.cc_jail_card = True
            return ("done", None)
        elif action == "go_to_jail":
            self.send_to_jail(p)
            return ("jail", None)
        elif action == "advance_go":
            if p.position > 0:
                p.money += 200
                self.add_alert(f"{p.name} collected $200 for passing GO.")
            p.position = 0
            return ("land", 0)
        elif action == "collect":
            amt = self.CC_COLLECT.get(card_idx, 0)
            p.money += amt
            self.add_alert(f"{p.name} collected ${amt}.")
            return ("done", None)
        elif action == "pay":
            amt = self.CC_PAY.get(card_idx, 0)
            p.money -= amt
            self.add_alert(f"{p.name} paid ${amt}.")
            return ("done", None)
        elif action == "collect_from_each":
            amt = self.CC_COLLECT_EACH.get(card_idx, 10)
            other = self.other(p)
            transfer = min(amt, other.money)
            other.money -= transfer
            p.money += transfer
            self.add_alert(f"{p.name} collected ${transfer} from {other.name}.")
            return ("done", None)
        elif action == "repairs":
            cost = self._calc_repairs(p, 40, 115)
            p.money -= cost
            self.add_alert(f"{p.name} paid ${cost} for street repairs.")
            return ("done", None)
        return ("done", None)

    def _calc_repairs(self, player, house_cost, hotel_cost):
        total = 0
        for sq in self.board:
            if sq.owner == player.index:
                if sq.house == 5:
                    total += hotel_cost
                else:
                    total += sq.house * house_cost
        return total


    # ── Bankruptcy ──

    def check_bankruptcy(self, player):
        return player.money < 0

    def force_bankruptcy(self, player):
        """Transfer all assets to creditor (other player) or bank."""
        creditor = self.other(player)
        for sq in self.board:
            if sq.owner == player.index:
                if sq.house > 0:
                    creditor.money += (sq.house_price // 2) * sq.house
                    sq.house = 0
                sq.owner = creditor.index
        if player.money < 0:
            creditor.money += player.money  # reduce by debt amount
        player.money = 0
        self.game_over = True
        self.winner = creditor
        self.add_alert(f"{player.name} is bankrupt! {creditor.name} wins!")

    def get_owned_properties(self, player):
        return [sq for sq in self.board if sq.owner == player.index]

