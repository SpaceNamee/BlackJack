from numpy import random
import time
import math
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox

THEME_COLOR = "#0f5132"

class Cards:
    """Представляє об'єкт: Карта"""
    CARD_VALUES = {
        "2" : 2,
        "3" : 3,
        "4" : 4,
        "5" : 5,
        "6" : 6,
        "7" : 7,
        "8" : 8,
        "9" : 9,
        "10" : 10,
        "J" : 10,
        "Q" : 10,
        "K" : 10,
        "A" : 11
    }
    SUITS = ["Spades","Hearts" ,"Diamonds", "Clubs" ]
    """Піка, Черва. Бубна, Хреста"""

    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self):
        self.ranks_index = []
        self.suits_index = []
        self.cards_amount = 0


    # Перевірка для особливої карти "A"
    def is_ace(self, rank_index):
        return self.CARD_VALUES[self.RANKS[rank_index]] == "A"

    def get_value(self, rank_index):
        return self.CARD_VALUES[self.RANKS[rank_index]]

    def add_card(self, rank_index, suit_index):
        self.ranks_index.append(rank_index)
        self.suits_index.append(suit_index)
        self.cards_amount += 1

    def get_formated_cards_for_printing(self):
        cards = []
        for rank_inx, suit_inx in zip(self.ranks_index, self.suits_index):
            cards.append((rank_inx, suit_inx))

        return cards

class Deck:
    """Відповідає за об'єкт: ігрова колода"""
    def __init__(self):
        self.is_using_pairs = Cards()

    def get_card(self):
        """Повертає карту з колоди так, щоб не було дублікатів"""
        switch = True

        while switch:
            switch = False

            rank_index = random.randint(len(Cards.RANKS)-1)
            suit_index = random.randint(len(Cards.SUITS)-1)

            for rank_idx, suit_idx in zip(self.is_using_pairs.ranks_index, self.is_using_pairs.suits_index):
                if rank_idx == rank_index and suit_idx == suit_index:
                    switch = True
                    break

        self.is_using_pairs.ranks_index.append(rank_index)
        self.is_using_pairs.suits_index.append(suit_index)

        # print(self.is_using_pairs.ranks_index)
        return [rank_index, suit_index]

    def reset(self):
        """Оновлення колоди кард"""
        self.is_using_pairs = Cards()

class Dealer:
    def __init__(self):
        self.cards = Cards()
        self.is_blackjack = False
        self.is_over_21 = False
        self.score = 0

    def start_cards(self, deck):
        for _ in range(2):
            card = deck.get_card()
            self.cards.add_card(card[0], card[1])

        self.is_blackjack = self.is_blackjack_checker()

    def hit(self, deck):
        card = deck.get_card()
        self.cards.add_card(card[0], card[1])
        self.is_over_21 = self.is_over_21_checker()

    def is_blackjack_checker(self):
        first_card = self.cards.ranks_index[0]
        second_card = self.cards.ranks_index[1]
        return True if ((self.cards.is_ace(first_card)
                        and self.cards.get_value(second_card) == 10)
                        or (self.cards.is_ace(second_card)
                        and self.cards.get_value(first_card) == 10))\
                    else False

    def is_over_21_checker(self):
        if self.calc_score(mode=0) > 21:
            return True
        return False

    def calc_score(self, mode = 0):
        score = 0
        count_a = 0
        for i in range(mode, self.cards.cards_amount):
            card = self.cards.ranks_index[i]
            if self.cards.is_ace(card):
                if score + self.cards.get_value(card) > 21:
                    count_a += 1
            score += self.cards.get_value(card)

        while count_a and score > 21:
            score -= 10
            count_a -= 1

        print(f"SCORE: {score}")
        return score

    def reset(self):
        self.cards = Cards()
        self.is_blackjack = False
        self.is_over_21 = False
        self.score = 0

class Player(Dealer):
    def __init__(self, name, bid, balance):
        super().__init__()
        self.bid = bid
        self.balance = balance
        self.is_winner = False
        self.splitting = []
        self.name = name
        self.is_splitted = False
        self.end_turn = False
        self.ace_exception = False
        self.need_to_show_splitted_card = 0

    def stay(self, deck, dealer):
        self.score = self.calc_score(mode=0)
        score_dealer = dealer.calc_score(mode=0)

        while True:
            if score_dealer < 17:
                dealer.hit(deck)
                score_dealer = dealer.calc_score(mode=0)
            else:
                break

        if score_dealer > 21 or score_dealer < self.score:
            self.balance += self.bid
            self.is_winner = True
        elif score_dealer > self.score:
            self.balance -= self.bid
            self.is_winner = False
        elif score_dealer == self.score:
            self.is_winner = None

    def condition_split_or_double_down(self):
        return True if self.cards.cards_amount == 2 else False

    def split(self):
        for i in range(2):
            if self.cards.is_ace(self.cards.ranks_index[0]) \
                and self.cards.is_ace(self.cards.ranks_index[1]):
                self.ace_exception = True
            player = Player(name = f'Hand', bid = self.bid, balance = self.balance)
            player.cards.add_card(self.cards.ranks_index[i], self.cards.suits_index[i])
            self.splitting.append(player)
            self.is_splitted = True
            self.need_to_show_splitrd_card = 2
        self.cards = 0

    def double_down(self):
        self.bid *= 2

    def reset(self):
        super().reset()
        self.is_winner = False
        self.splitting = []

class GamePLay:
    """Головний клас, який відповідає за логіку гри"""
    def __init__(self, blackjack_pays=3/2):
        self.players = []
        self.deck = Deck()
        self.dealer = Dealer()
        self.blackjack_pays = blackjack_pays

    def add_player(self, name, bid, balance = 1000):
        """Додає гравця в гру"""
        player = Player(name, bid, balance)
        self.players.append(player)

    def get_splitting_result(self, split_player, split_players_winner_list):
        """ Підрахунок кількості виграшів та проіграшів в гравця під час 'splitting'"""
        if split_player.splitting:
            current_split_player = split_player.splitting
        else:
            return split_player.is_winner

        split_players_winner_list.append(self.get_splitting_result(current_split_player[0], split_players_winner_list))
        split_players_winner_list.append(self.get_splitting_result(current_split_player[1], split_players_winner_list))

    def print_win_rate(self):
        for i, player in enumerate(self.players):
            print("====================== WIN RATE ======================")
            print(f"\n{player.name} {i + 1}")

            winner_list = []
            self.get_splitting_result(player, winner_list)

            def print_res(results):
                if results:
                    print("You: WIN")
                    print("Dealer: LOOSE")
                elif results is None:
                    print("Draw")
                else:
                    print("You: LOOSE")
                    print("Dealer: WIN")

            if winner_list:
                for j, res in enumerate(winner_list):
                    print(f"Hand {j + 1}")
                    print_res(res)
            else:
                print_res(player.is_winner)

            print("======================================================")

    def calc_balance(self, player, dealer):
        """Обраховує новий баланс гравця"""
        if player.is_blackjack and not dealer.is_blackjack:
            if player.is_splitted:
                player.balance += player.bid
            else:
                player.balance += player.bid * self.blackjack_pays
        elif player.is_winner:
            player.balance += player.bid
        else:
            player.balance -= player.bid

    # TODO НОТАТКА: моя програма не дозволяє подвоювати ставку під час splitting
    def calc_balance_in_splitted_player(self, player, res_list):
        """Обраховує баланс гравця у якого було 'split'"""
        for res in res_list:
            if res:
                player.balance += player.bid
            else:
                player.balance -= player.bid

    def print_balance(self):
        for i, player in enumerate(self.players):
            if player.splitting:
                win_list = []
                self.get_splitting_result(player, win_list)
                self.calc_balance_in_splitted_player(player, win_list)
                print(f"{player.name} {i + 1}: {player.balance}")
            else:
                self.calc_balance(player, self.dealer)
                print(f"{player.name} {i + 1}: {player.balance}")

class BlackJackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("BlackJack Game")
        self.root.geometry("800x600")
        self.root.configure(bg=THEME_COLOR) # зелений колір фону
        self.root.resizable(False, False)

        # Початкові налаштування гри
        self.number_of_decks = 1 # Кількість колод
        self.blackjack_pays = 1.5 # В скільки разів більше казино виплатить при блекджеку
        self.current_bid = 10 # Значення ставки по замовчуванні
        self.players_count_var = tk.StringVar(value="1")

        # Символи карт
        self.suit_symbols = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠'
        }

        # Кольори символів
        self.suit_colors = {
            'Hearts': '#dc3545',
            'Diamonds': '#dc3545',
            'Clubs': '#000000',
            'Spades': '#000000'
        }

        # Ініціалізація гри
        self.game = GamePLay()
        self.players_data = 0

        # Центрування вікна на екрані
        self.center_window(self.root, 800, 600)

        self.players_data = []
        self.create_welcome_window()

        # GUI елементи
        self.canvas = None
        self.dealer_cards_positions = []
        self.players_cards_positions = []
        self.buttons = {}
        self.info_labels = {}

        # Налаштування карт
        self.card_width = 60
        self.card_height = 85
        self.card_spacing = 15

    def center_window(self, window, width, height):
        """Функція центрування вікна"""
        screen_width = window.winfo_screenwidth() # Довжина екрана
        screen_height = window.winfo_screenheight() # Висота екрана
        x = (screen_width - width) // 2 # Відступ зверху для вікна
        y = (screen_height - height) // 2 # Відступ збоку для вікна
        window.geometry(f"{width}x{height}+{x}+{y}") # Задання розміщення вікну

    def create_welcome_window(self):
        """Створює головний фрейм"""

        # Головний фрейм
        self.welcome_frame = tk.Frame(self.root, bg=THEME_COLOR)
        self.welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Зелене полотно
        canvas = tk.Canvas(self.welcome_frame, bg="#0f5132", height=300, bd=10, relief="groove", highlightthickness=0)
        canvas.pack(fill="both", expand=True, pady=(0, 20))

        # Додаємо текст на полотно
        canvas.create_text(400, 300, text="BlackJack", font=("Arial", 60, "bold"),
                           fill="#dc3545")

        canvas.create_text(465+80, 120, text=self.suit_symbols['Hearts'], font=("Arial", 200, "bold"),
                           fill=self.suit_colors['Hearts'], tags="title", )

        canvas.create_text(425+20, 120, text=self.suit_symbols['Clubs'], font=("Arial", 200, "bold"),
                           fill=self.suit_colors['Clubs'], tags="title", )

        canvas.create_text(375-20, 120, text=self.suit_symbols['Diamonds'], font=("Arial", 200, "bold"),
                           fill=self.suit_colors['Diamonds'], tags="title", )

        canvas.create_text(325-80, 120, text=self.suit_symbols['Spades'], font=("Arial", 200, "bold"),
                           fill=self.suit_colors['Spades'], tags="title", )

        # Кнопка Start
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Start.TButton',
                        font=('Arial', 20, 'bold'),
                        foreground='white',
                        background='#d4af37',
                        borderwidth=0,
                        focuscolor='', # забирає ободок при натисканні
                        padding=(50, 20), # збільшує кнопку
                        )


        style.map('Start.TButton',
                  background=[('active', '#b8941f')],)

        start_button = ttk.Button(self.welcome_frame, text="START", style='Start.TButton',
                                  command=self.create_setup_window)
        start_button.pack(pady=20)

    def create_setup_window(self):
        """Створює випадне вікно налаштувань"""

        # Випадне вікно налаштувань
        self.setup_window = tk.Toplevel(self.root)
        self.setup_window.title("Налаштування гри")
        self.setup_window.geometry("500x600")
        self.setup_window.configure(bg="white")
        self.setup_window.resizable(False, False)
        self.setup_window.grab_set()  # Робимо вікно модальним (захоплює всі події миші та клавіатури)

        # Центруємо вікно
        self.center_window(self.setup_window, 500, 600)

        # Головний фрейм
        main_frame = tk.Frame(self.setup_window, bg="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        title_label = tk.Label(main_frame, text="Налаштування гравців",
                               font=("Arial", 18, "bold"), bg="white", fg=THEME_COLOR)
        title_label.pack(pady=(0, 20))

        # Поле для кількості гравців
        players_frame = tk.Frame(main_frame, bg="white")
        players_frame.pack(fill="x", pady=(0, 20))

        tk.Label(players_frame, text="Кількість гравців:", font=("Arial", 12),
                 bg="white").pack(side="left", fill='x')

        count_players_spinbox = tk.Spinbox(players_frame, from_=1, to=5, width=5,
                                          textvariable=self.players_count_var,
                                          command=self.update_players_fields,
                                          font=("Arial", 12),
                                          state="readonly")
        count_players_spinbox.pack(side="right", fill="x")

        # Frame для правил введення символів
        self.label_status_frame = tk.Frame(main_frame, bg="white")
        self.label_status_frame.pack(fill="x")

        # Розміщуються у вікні при помилці
        self.label_status_name = tk.Label(self.label_status_frame,text="", bg="white")
        self.label_status_bat_and_balance = tk.Label(self.label_status_frame,text="", bg="white")

        # Фрейм для динамічних полів гравців
        self.canvas_frame = tk.Frame(main_frame, bg="white")
        self.canvas_frame.pack(fill="both", expand=True)

        # self.canvas_frame -> players_canvas
        # Frame у Tkinter не підтримує прокрутку напряму, тому ми вставляємо Frame у Canvas, а скролбар — до Canvas.
        self.players_canvas = tk.Canvas(self.canvas_frame, bg="white", highlightthickness=0)

        # Додавання скролбару до players_canvas
        scrollbar = ttk.Scrollbar(self.players_canvas, orient="vertical", command=self.players_canvas.yview)
        self.players_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Кастомізація скролбар для заборони прокрутки вверх
        def yview(*args):
            if self.players_canvas.yview() == (0.0, 1.0):
                return
            self.players_canvas.yview(*args)

        # Додавання дії прокрутки при прокручуванню колеса мишки
        self.players_canvas.bind_all('<MouseWheel>', lambda event: yview('scroll', int(-1 * (event.delta / 120)), 'units'))

        # Frame, що буде прокручуватися
        self.scrollable_frame = tk.Frame(self.players_canvas, bg="white")

        # Коли вміст scrollable_frame змінюється (наприклад, додаються нові поля), Canvas оновлює зону прокрутки.
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.players_canvas.configure(scrollregion=self.players_canvas.bbox("all"))
        )

        # Вставляємо scrollable_frame в полотно canvas
        self.players_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame_window")

        def resize_scrollable_frame(event):
            self.players_canvas.itemconfig("frame_window", width=event.width-20)

        # Прив'язка до
        self.players_canvas.bind("<Configure>", resize_scrollable_frame)

        self.players_canvas.pack(fill="both", expand=True)


        # Кнопки внизу
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack(fill="x", pady=(20, 0))

        start_game_button = tk.Button(buttons_frame, text="Продовжити",
                                      font=("Arial", 12, "bold"), bg="#28a745", fg="white",
                                      command=self.create_players, pady=8)
        start_game_button.pack(side="right", padx=(10, 0))

        cancel_button = tk.Button(buttons_frame, text="Скасувати",
                                  font=("Arial", 12), bg="#dc3545", fg="white",
                                  command=self.cancel_game, pady=8)
        cancel_button.pack(side="right")

        self.setup_window.protocol("WM_DELETE_WINDOW", self.cancel_game)

        # Ініціалізуємо поля для одного гравця
        self.update_players_fields()

    def cancel_game(self):
        """Функція скасування ведення початку налаштувань гри"""

        self.setup_window.destroy()
        self.players_count_var.set(value="1")
        self.update_players_fields()

    def update_players_fields(self):
        """Оновлює додану кількість гравців. """

        # Очищуємо попередні поля
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.player_entries = []

        try:
            num_players = int(self.players_count_var.get())
        except ValueError:
            num_players = 1

        for i in range(num_players):
            # Фрейм для кожного гравця
            player_frame = tk.LabelFrame(self.scrollable_frame, text=f"Гравець {i + 1}",
                                         font=("Arial", 12, "bold"), bg="white",
                                         fg=THEME_COLOR, padx=10, pady=10)
            player_frame.pack(fill="x", expand=True, pady=5)

            # Поля для введення даних
            entries = {}

            # Валідація імені
            def validate_name(symbol, text):
                if len(symbol) > 1:
                    symbol = ' '
                res = (symbol.isalpha() or symbol.isnumeric() or symbol in [" ", "-"]) and  len(text) < 21
                if res:
                    self.label_status_name.pack_forget()
                    self.label_status_frame.pack_forget()
                return res

            def invalidate_name():
                self.label_status_frame.pack(fill='x',before=self.canvas_frame)
                self.label_status_name.pack()

                self.label_status_name.config(fg="red", text="Прізвище: тільки літери, пробіл або '-' або менше 20 літер")

            name_vcmd = player_frame.register(validate_name)
            name_invcmd = player_frame.register(invalidate_name)

            # Валідація балансу та ставки
            def validate_balance_or_bid(text):
                res = text.isnumeric() or text == ''
                if res:
                    self.label_status_bat_and_balance.pack_forget()
                    self.label_status_bat_and_balance.pack_forget()
                return res

            def invalidate_balance_or_bid():
                self.label_status_frame.pack(fill='x', before=self.canvas_frame)
                self.label_status_bat_and_balance.pack()

                self.label_status_bat_and_balance.config(fg="red", text="Тільки цілі числа (без пробілів)")

            balance_or_bid_vcmd = player_frame.register(validate_balance_or_bid)
            balance_or_bid_invcmd = player_frame.register(invalidate_balance_or_bid)

            # Ім'я
            name_frame = tk.Frame(player_frame, bg="white")
            name_frame.pack(fill="x", pady=2)
            tk.Label(name_frame, text="Ім'я:", width=10, anchor="w",
                     font=("Arial", 10), bg="white",).pack(side="left")
            entries['name'] = tk.Entry(name_frame, font=("Arial", 10), validate="key",
                                       validatecommand=(name_vcmd, "%S", "%P"), invalidcommand=name_invcmd)
            entries['name'].insert(0, f"Гравець {i + 1}")
            entries['name'].pack(side="right", fill="x", expand=True)

            # Баланс
            balance_frame = tk.Frame(player_frame, bg="white")
            balance_frame.pack(fill="x", pady=2)
            tk.Label(balance_frame, text="Баланс:", width=10, anchor="w",
                     font=("Arial", 10), bg="white").pack(side="left")
            entries['balance'] = tk.Entry(balance_frame, font=("Arial", 10), validate="key",
                                       validatecommand=(balance_or_bid_vcmd, "%P"), invalidcommand=balance_or_bid_invcmd)
            entries['balance'].insert(0, "1000")
            entries['balance'].pack(side="right", fill="x", expand=True)

            # Ставка
            bid_frame = tk.Frame(player_frame, bg="white")
            bid_frame.pack(fill="x", pady=2)
            tk.Label(bid_frame, text="Ставка:", width=10, anchor="w",
                     font=("Arial", 10), bg="white").pack(side="left")
            entries['bid'] = tk.Entry(bid_frame, font=("Arial", 10),  validate="key",
                                       validatecommand=(balance_or_bid_vcmd, "%P"), invalidcommand=balance_or_bid_invcmd)
            entries['bid'].insert(0, "100")
            entries['bid'].pack(side="right", fill="x", expand=True)

            self.player_entries.append(entries)

    def collect_player_data(self):
        """Повертає масив з даними гравцями. В разі помилки повертає пустий масив []"""

        players_data = []

        for i, entries in enumerate(self.player_entries):

            # Перевірка на коректно введені дані
            try:
                name = entries['name'].get().strip()
                balance = int(entries['balance'].get())
                bid = int(entries['bid'].get())

                if not name:
                    name = f"Гравець {i + 1}"

                if balance <= 0:
                    raise ValueError(f"Баланс гравця {i + 1} повинен бути більше 0")

                if bid <= 0 or bid > balance:
                    raise ValueError(f"Ставка гравця {i + 1} повинна бути від 1 до {balance}")

                players_data.append({
                    'name': name,
                    'balance': balance,
                    'bid': bid
                })

            except ValueError as e:
                if "invalid literal" in str(e):
                    messagebox.showerror("Помилка",
                                         f"Некоректні дані для гравця {i + 1}. Баланс та ставка повинні бути цілими числами.")
                else:
                    messagebox.showerror("Помилка", str(e))
                return None

        return players_data

    def create_players(self):
        """Запускає гру з зібраними даними"""
        if not self.players_data:
            self.players_data = self.collect_player_data()

            if self.players_data:
                self.setup_window.destroy()
                self.welcome_frame.destroy()

        # Очищуємо гравців
        self.game.players = []
        self.game.dealer.cards = Cards()
        self.game.deck.reset()

        for i, player in enumerate(self.players_data, 1):
            self.game.add_player(name = player["name"], bid = player["bid"], balance = player["balance"])

        for i, player in enumerate(self.game.players, 1):
            player.start_cards(self.game.deck)

        self.game.dealer.start_cards(self.game.deck)
        self.create_game_interface()

    def create_game_interface(self):
        """Створює основний ігровий інтерфейс"""
        # pass
        self.root.geometry("1200x800")
        self.center_window(self.root, 1200, 800)

        # Головне полотно для гри
        self.canvas = tk.Canvas(self.root, bg="#0f5132", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # заголовок та інформацію про виплати через canvas.create_text
        self.canvas.create_text(600, 300, text="BlackJack",
                                font=("Arial", 150, "bold"), fill="#1f9960")
        self.canvas.create_text(600, 450, text="BlackJack Pays 3 to 2",
                                font=("Arial", 30), fill="#1f9960")

        # Створюємо зони для карт
        self.setup_card_areas()

        # Створюємо кнопки управління
        self.create_control_buttons()

        # Створюємо інформаційні лейбли для гравців
        self.create_player_info_labels()

        # Початкове оновлення інтерфейсу
        self.update_all_cards()

        self.next_player(self.game.players[0])

    def setup_card_areas(self):
        """Налаштовує зони для розміщення карт дилера та гравців"""
        # Зона дилера (верх, по центру)
        dealer_y = 150
        dealer_x = 600
        self.dealer_area = {"x": dealer_x, "y": dealer_y}

        # Зони гравців (низ, напівколом)
        players_y = 550
        players_count = len(self.game.players)

        if players_count == 1:
            # Один гравець по центру
            self.players_areas = [{"x": 600, "y": players_y}]
        else:
            if players_count == 2:
                minus = 900
            else:
                minus = 1000
            # Кілька гравців напівколом
            center_x = 600
            radius = 500
            angle_step = math.pi / (players_count + 1)

            self.players_areas = []
            for i in range(players_count):
                angle = math.pi - angle_step * (i + 1)
                x = center_x + radius * math.cos(angle)
                y = players_y - radius * math.sin(angle) * -2 - minus  # Зменшуємо висоту для кращого вигляду
                self.players_areas.append({"x": int(x), "y": int(y)})

    def create_card_image(self, rank_index, suit_index, is_face_down=False):
        """Створює візуальне представлення карти"""
        if is_face_down:
            # Зворотна сторона карти
            return {
                "type": "face_down",
                "fill": "#8b0000",
                "outline": "#ffffff",
                "text": "🂠",
                "text_color": "#ffffff"
            }

        # дані карти
        rank = Cards.RANKS[rank_index]
        suit = Cards.SUITS[suit_index]

        return {
            "type": "face_up",
            "fill": "#ffffff",
            "outline": "#000000",
            "rank": rank,
            "suit_symbol": self.suit_symbols[suit],
            "text_color": self.suit_colors[suit]
        }

    def draw_card(self, x, y, card_data, card_id=None):
        """Малює карту на полотні"""
        # Видаляємо стару карту якщо є ID
        if card_id:
            self.canvas.delete(card_id)

        # Прямокутник карти
        card_rect = self.canvas.create_rectangle(
            x, y, x + self.card_width, y + self.card_height,
            fill=card_data["fill"], outline=card_data["outline"], width=2,
        )

        text_cards = []
        if card_data["type"] == "face_down":
            # Зворотна сторона карти
            text_cards.append(self.canvas.create_text(
                x + self.card_width / 2, y + self.card_height / 2,
                text=card_data["text"], font=("Arial", 16),
                fill=card_data["text_color"]
            ))
        else:
            # Лицева сторона карти
            # Ранг у верхньому лівому куті
            text_cards.append(self.canvas.create_text(
                x + 8, y + 12, text=card_data["rank"],
                font=("Arial", 10, "bold"), fill=card_data["text_color"], anchor="nw",
            ))

            # Символ масті у верхньому лівому куті
            text_cards.append(self.canvas.create_text(
                x + 8, y + 25, text=card_data["suit_symbol"],
                font=("Arial", 12), fill=card_data["text_color"], anchor="nw"
            ))

            # Великий символ по центру
            text_cards.append(self.canvas.create_text(
                x + self.card_width / 2, y + self.card_height / 2,
                text=card_data["suit_symbol"], font=("Arial", 20),
                fill=card_data["text_color"]
            ))

            # Ранг у нижньому правому куті (перевернутий)
            text_cards.append(self.canvas.create_text(
                x + self.card_width - 8, y + self.card_height - 12,
                text=card_data["rank"], font=("Arial", 10, "bold"),
                fill=card_data["text_color"], anchor="se"
            ))

        return [card_rect,text_cards]

    def update_dealer_cards(self, cards, hide_first=True):
        """Оновлює карти дилера"""
        # Очищаємо попередні карти дилера
        self.canvas.delete("cards")

        if not cards:
            return

        # Малюємо карти дилера
        start_x = self.dealer_area["x"] - (len(cards) * (self.card_width + self.card_spacing)) // 2

        for i, (rank_idx, suit_idx) in enumerate(cards):
            x = start_x + i * (self.card_width + self.card_spacing)
            y = self.dealer_area["y"]

            # Перша карта може бути прихована
            is_hidden = (i == 0 and hide_first)
            card_data = self.create_card_image(rank_idx, suit_idx, is_hidden)

            card_info = self.draw_card(x, y, card_data)
            card_id = card_info[0]
            card_texts = card_info[1]

            self.canvas.addtag("cards", "withtag",card_id)
            for card_text in card_texts:
                self.canvas.addtag("cards", "withtag",card_text)

        #  підпис "Dealer"
        self.canvas.delete("dealer_label")
        dealer_label = self.canvas.create_text(
            self.dealer_area["x"], self.dealer_area["y"] - 30,
            text="Dealer", font=("Arial", 14, "bold"), fill="#ffffff"
        )
        self.canvas.addtag("dealer_label", "withtag", dealer_label)

    def update_all_cards(self, hide_first_dealer_cards=True):
        """Оновлює всі карти на столі"""
        # Очищаємо все полотно від карт
        self.update_dealer_cards(self.game.dealer.cards.get_formated_cards_for_printing(), hide_first=hide_first_dealer_cards)

        for i, player in enumerate(self.game.players):
            self.update_player_cards(i, player.cards.get_formated_cards_for_printing())

    def update_player_cards(self, player_index, player_cards=None, is_spllited=False):
        """Оновлює карти конкретного гравця"""
        card_tag = f"player_{player_index}_cards"
        card_text_tag = f"player_{player_index}_text_cards"
        self.canvas.delete(card_tag)
        self.canvas.delete(card_text_tag)

        if not player_cards:
            return

        if player_index >= len(self.players_areas):
            return

        area = self.players_areas[player_index]
        start_x = area["x"] - (len(player_cards) * (self.card_width + self.card_spacing)) // 2

        for i, (rank_idx, suit_idx) in enumerate(player_cards):
            x = start_x + i * (self.card_width + self.card_spacing)
            y = area["y"]

            card_data = self.create_card_image(rank_idx, suit_idx, False)
            card_info = self.draw_card(x, y, card_data)
            card_id = card_info[0]
            card_texts = card_info[1]
            self.canvas.addtag(card_tag, "withtag", card_id)
            for card_text in card_texts:
                self.canvas.addtag(card_text_tag, "withtag",card_text)

    def delete_player_cards(self, player_index):
        card_tag = f"player_{player_index}_cards"
        card_text_tag = f"player_{player_index}_text_cards"
        self.canvas.delete(card_tag)
        self.canvas.delete(card_text_tag)

        return [card_tag, card_text_tag]

    def flip_dealer_first_card(self, dealer_cards):
        """Перевертає першу карту дилера лицевою стороною"""
        if not dealer_cards:
            return

        # Перемальовуємо карти дилера без приховування
        self.update_dealer_cards(dealer_cards, hide_first=False)

    def create_control_buttons(self):
        """Створює кнопки управління грою"""
        # Фрейм для кнопок (по центру)
        button_frame = tk.Frame(self.root, bg=THEME_COLOR)
        button_frame.place(x=600, y=400, anchor="center")

        # Стиль кнопок
        button_style = {
            "font": ("Arial", 12, "bold"),
            "width": 10,
            "height": 2,
            "relief": "raised",
            "bd": 3
        }

        # Кнопка Hit
        self.buttons["hit"] = tk.Button(
            button_frame, text="HIT", bg="#28a745", fg="white", **button_style
        )
        self.buttons["hit"].grid(row=0, column=0, padx=5, pady=5)

        # Кнопка Stay
        self.buttons["stay"] = tk.Button(
            button_frame, text="STAY", bg="#dc3545", fg="white", **button_style
        )
        self.buttons["stay"].grid(row=0, column=1, padx=5, pady=5)

        # Кнопка Split
        self.buttons["split"] = tk.Button(
            button_frame, text="SPLIT", bg="#ffc107", fg="black", **button_style
        )
        self.buttons["split"].grid(row=1, column=0, padx=5, pady=5)

        # Кнопка Double Down
        self.buttons["double_down"] = tk.Button(
            button_frame, text="DOUBLE\nDOWN", bg="#17a2b8", fg="white", **button_style
        )
        self.buttons["double_down"].grid(row=1, column=1, padx=5, pady=5)

        # Початково ховаємо всі кнопки
        self.hide_all_buttons()

    def create_player_info_labels(self):
        """Створює інформаційні лейбли для гравців"""
        for i, player in enumerate(self.game.players):
            if i >= len(self.players_areas):
                continue

            area = self.players_areas[i]
            self.update_player_cards(i, player.cards.get_formated_cards_for_printing())

            # Створюємо фрейм для інформації гравця
            info_frame = tk.Frame(self.root, bg="#1f9960", relief="solid", bd=0)
            info_frame.place(x=area["x"]+10, y=area["y"] + 150, anchor="center")

            # Ім'я гравця
            name_label = tk.Label(
                info_frame, text=player.name,
                font=("Arial", 12, "bold"), bg="#1f9960", fg="#ffffff"
            )
            name_label.pack()

            # Баланс
            balance_label = tk.Label(
                info_frame, text=f"Balance: ${player.balance}",
                font=("Arial", 10), bg="#1f9960", fg="#ffd700"
            )
            balance_label.pack()

            # Ставка
            bet_label = tk.Label(
                info_frame, text=f"Bet: ${player.bid}",
                font=("Arial", 10), bg="#1f9960", fg="#ff6b6b"
            )
            bet_label.pack()

            turn_identification = tk.Label(self.root,  text = '', font=("Arial", 13), anchor="center", bg=THEME_COLOR, fg=THEME_COLOR)
            turn_identification.place(x=area["x"]+10, y=area["y"] + 200, anchor="center")

            # Зберігаємо посилання на лейбли
            self.info_labels[i] = {
                "frame": info_frame,
                "name": name_label,
                "balance": balance_label,
                "bet": bet_label,
                "turn_identification": turn_identification,
            }

    def update_player_info(self, player, name=None, balance=None, bet=None, turn_identification=''):
        """Оновлює інформацію про гравця"""
        player_index = self.game.players.index(player)
        if player_index not in self.info_labels:
            return
        print(player_index)
        labels = self.info_labels[player_index]

        if name is not None:
            labels["name"].config(text=name)
        if balance is not None:
            labels["balance"].config(text=f"Balance: ${balance}")
        if bet is not None:
            labels["bet"].config(text=f"Bet: ${bet}")
        if turn_identification == '':
            labels["turn_identification"].config(text=turn_identification, bg=THEME_COLOR, fg=THEME_COLOR)
        else:
            labels["turn_identification"].config(text=turn_identification,  bg="black", fg="red")

    def show_buttons(self, buttons_list):
        """Показує вказані кнопки"""
        for button_name in buttons_list:
            if button_name in self.buttons:
                self.buttons[button_name].config(state="normal")

    def hide_buttons(self, buttons_list):
        """Ховає вказані кнопки"""

        for button_name in buttons_list:
            if button_name in self.buttons:
                self.buttons[button_name].config(state="disabled")

    def hide_all_buttons(self):
        """Ховає всі кнопки"""
        self.hide_buttons(["hit", "stay", "split", "double_down"])

    def show_all_buttons(self):
        """Показує всі кнопки"""
        self.show_buttons(["hit", "stay", "split", "double_down"])

    def next_player(self, player, father_root=None):
        #     Налаштування кнопок
        self.show_buttons(['hit', 'stay', 'split', 'double_down'])
        self.buttons["hit"].configure(command=lambda pl=player: self.hit_action(pl, self.game.deck))
        self.buttons["stay"].configure(command=lambda pl=player: self.stay_action(pl, self.game.deck))
        self.buttons["split"].configure(command=lambda pl=player: self.split_action(pl, self.game.deck))
        self.buttons["double_down"].configure(command=lambda pl=player: self.double_down_action(pl))
        self.play_player_turn(player)
        if father_root:
            self.update_player_info(father_root, turn_identification="Your turn")
        else:
            self.update_player_info(player, turn_identification="Your turn")

    def play_player_turn(self, player, father_root = None):
        if player.is_blackjack:
            self.stay_action(player, self.game.deck)
            messagebox.showinfo(title=f"{player.name}", message=f"{player.name}: BLACKJACK!!!")
            return None

        if player.is_over_21:
            messagebox.showinfo(title=f"{player.name}", message=f"{player.name}: Over 21!!!")
            self.stay_action(player, self.game.deck)
            return None

        if player.cards.cards_amount == 2:
            if Cards.RANKS[player.cards.ranks_index[0]] != Cards.RANKS[player.cards.ranks_index[1]]:
                self.hide_buttons(["split"])
            else:
                self.show_buttons(["split"])
        else:
            self.hide_buttons(["split"])

        if father_root:
            if father_root.need_to_show_splitted_card:
                self.next_player(father_root.splitting[father_root.need_to_show_splitted_card-1],  father_root)

    # === ОБРОБНИКИ ПОДІЙ КНОПОК ===
    def hit_action(self, player, deck):
        player.hit(deck)
        player_index = self.game.players.index(player)

        self.update_player_cards(player_index, player.cards.get_formated_cards_for_printing())
        self.play_player_turn(player)

    def stay_action(self, player, deck):
        """Обробник кнопки Stay"""

        self.update_player_info(player)
        if self.game.players.index(player) == len(self.game.players) - 1:
            player.stay(deck, self.game.dealer)
            self.update_all_cards(False)
            self.end_round()
        else:
            self.next_player(self.game.players[self.game.players.index(player) + 1])

    def split_action(self, player, deck):
        player.split()
        if player.ace_exception:
            for splited_player in player.splitting:
                splited_player.hit(deck)

            self.hide_buttons(["hit"])

        self.next_player(player.splitting[0])

    def double_down_action(self, player):
        player.double_down()
        self.update_player_info(player, bet=player.bid)

    def end_round(self):
        self.game.print_win_rate()
        self.canvas.destroy()
        self.create_players()
        self.update_all_cards()

def main():
    root = tk.Tk()
    app = BlackJackGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()

