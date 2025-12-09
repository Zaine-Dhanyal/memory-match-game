import tkinter as tk
from tkinter import messagebox, ttk
import random

# ---------- EMOJIS ----------
EMOJIS = ["🍎","🍌","🍇","🍓","🍒","🍑","🍍","🥝",
          "🍉","🍊","🍋","🍐","🥭","🍈","🍏","🥥",
          "🥑","🥕","🌽","🥔","🍠","🫐","🍅","🍆"]  # 24 emojis
CARD_BACK = "🎀"
REVEAL_MS = 700

class MemoryGame:
    def __init__(self, master, rows, cols, total_time, diff_callback):
        self.master = master
        self.diff_callback = diff_callback
        master.title("Memory Pairs Game")
        master.resizable(True, True)

        self.rows = rows
        self.cols = cols
        self.total_time = total_time

        self.frame = tk.Frame(master, padx=12, pady=12, bg="#0b1030")
        self.frame.pack(fill="both", expand=True)

        # ---------- top info ----------
        top = tk.Frame(self.frame, bg="#0b1030")
        top.pack(fill="x", pady=(0,8))
        self.timer_label = tk.Label(top, text=f"Time: {self.total_time}", font=("Comic Sans MS", 14, "bold"), bg="#0b1030", fg="white")
        self.timer_label.pack(side="left")
        self.moves_label = tk.Label(top, text="Moves: 0", font=("Comic Sans MS", 14), bg="#0b1030", fg="white")
        self.moves_label.pack(side="left", padx=12)
        self.restart_btn = tk.Button(top, text="Restart", command=self.restart, bg="white", fg="#0b1030")
        self.restart_btn.pack(side="right", padx=(5,0))
        self.back_btn = tk.Button(top, text="Back", command=self.go_back, bg="#d32f2f", fg="white")
        self.back_btn.pack(side="right", padx=(0,5))

        # ---------- progress bar ----------
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TProgressbar", thickness=18, troughcolor='#1a2b57', background='white')
        self.progress = ttk.Progressbar(self.frame, length=320, mode='determinate', maximum=self.total_time, style="TProgressbar")
        self.progress.pack(pady=(0,10))

        # ---------- board ----------
        self.board_frame = tk.Frame(self.frame, bg="#0b1030")
        self.board_frame.pack(fill="both", expand=True)

        self.total_cards = self.rows * self.cols
        self.pairs_needed = self.total_cards // 2

        self.first = None
        self.lock = False
        self.matches = 0
        self.moves = 0
        self.remaining_time = self.total_time
        self.timer_job = None

        self.build_deck()
        self.build_ui()
        self.start_timer()

        # ---------- make board responsive ----------
        for r in range(self.rows):
            self.board_frame.rowconfigure(r, weight=1)
        for c in range(self.cols):
            self.board_frame.columnconfigure(c, weight=1)

    def build_deck(self):
        symbols = EMOJIS[:]
        while len(symbols) < self.pairs_needed:
            symbols *= 2
        random.shuffle(symbols)
        chosen = symbols[:self.pairs_needed]
        deck = chosen * 2
        random.shuffle(deck)
        self.deck = deck

    def build_ui(self):
        for w in self.board_frame.winfo_children():
            w.destroy()
        self.cards = []
        k = 0
        for r in range(self.rows):
            for c in range(self.cols):
                b = tk.Button(self.board_frame, text=CARD_BACK, font=("Comic Sans MS", 28, "bold"),
                              bg="white", fg="black",
                              activebackground="#f0f0f0", relief="raised", bd=4,
                              command=lambda idx=k: self.on_card_click(idx))
                b.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
                self.cards.append({"button": b, "symbol": self.deck[k], "flipped": False, "matched": False})
                k += 1

    def on_card_click(self, idx):
        if self.lock:
            return
        card = self.cards[idx]
        if card["flipped"] or card["matched"]:
            return
        card["button"].config(text=card["symbol"], fg="black")
        card["flipped"] = True
        if self.first is None:
            self.first = idx
        else:
            self.moves += 1
            self.moves_label.config(text=f"Moves: {self.moves}")
            first_card = self.cards[self.first]
            if first_card["symbol"] == card["symbol"]:
                first_card["matched"] = True
                card["matched"] = True
                first_card["button"].config(bg="#ffeb3b")
                card["button"].config(bg="#ffeb3b")
                self.matches += 1
                self.first = None
                if self.matches == self.pairs_needed:
                    self.win()
            else:
                self.lock = True
                self.master.after(REVEAL_MS, lambda: self.hide_cards(idx))

    def hide_cards(self, idx2):
        idx1 = self.first
        self.cards[idx1]["button"].config(text=CARD_BACK, fg="black", bg="white")
        self.cards[idx2]["button"].config(text=CARD_BACK, fg="black", bg="white")
        self.cards[idx1]["flipped"] = False
        self.cards[idx2]["flipped"] = False
        self.first = None
        self.lock = False

    def start_timer(self):
        if self.timer_job:
            self.master.after_cancel(self.timer_job)
        self.remaining_time = self.total_time
        self.progress['value'] = self.total_time
        self.timer_tick()

    def timer_tick(self):
        self.timer_label.config(text=f"Time: {self.remaining_time}")
        self.progress['value'] = self.remaining_time
        if self.remaining_time <= 0:
            self.time_up()
            return
        self.remaining_time -= 1
        self.timer_job = self.master.after(1000, self.timer_tick)

    def time_up(self):
        for c in self.cards:
            c["button"].config(text=c["symbol"])
        messagebox.showinfo("Game Over", "⏰ Time's up!")

    def win(self):
        # Stop timer when game is won
        if self.timer_job:
            self.master.after_cancel(self.timer_job)
        messagebox.showinfo("Winner!", "🎉 You matched all pairs!")

    def restart(self):
        self.build_deck()
        self.build_ui()
        self.start_timer()

    def go_back(self):
        self.master.destroy()
        self.diff_callback()

# ---------- NAVY DIFFICULTY SELECTION WITH ROUNDED CARDS ----------
def choose_difficulty():
    window = tk.Tk()
    window.title("Memory Game")
    window.geometry("650x500")
    window.configure(bg="#0b1030")

    def start_game(level):
        if level == "Easy":
            rows, cols, time_limit = 2, 3, 90
        elif level == "Medium":
            rows, cols, time_limit = 3, 4, 150
        else:
            rows, cols, time_limit = 4, 5, 120

        game_win = tk.Toplevel(window)
        game_win.title("Memory Pairs Game")
        game_win.configure(bg="#0b1030")
        game_win.state("zoomed")  # full screen
        MemoryGame(game_win, rows, cols, time_limit, lambda: (game_win.destroy(), window.deiconify()))
        window.withdraw()  # hide difficulty window

    main_frame = tk.Frame(window, bg="#0b1030")
    main_frame.pack(expand=True)

    tk.Label(main_frame, text="🧠 Memory Match Game", font=("Comic Sans MS", 28, "bold"), bg="#0b1030", fg="white").pack(pady=10)
    tk.Label(main_frame, text="✨ Flip Tiles & Match Creative Fruits ✨", font=("Comic Sans MS", 16), bg="#0b1030", fg="white").pack(pady=6)
    tk.Label(main_frame, text="Choose Your Difficulty", font=("Comic Sans MS", 18, "bold"), bg="#0b1030", fg="white").pack(pady=20)

    card_frame = tk.Frame(main_frame, bg="#0b1030")
    card_frame.pack()

    difficulties = [("Easy", "🌟"), ("Medium", "🚀"), ("Hard", "🎯")]

    for name, icon in difficulties:
        card = tk.Frame(card_frame, bg="white", width=130, height=160)
        card.pack(side="left", padx=20, pady=10)
        card.pack_propagate(False)
        tk.Label(card, text=icon, font=("Comic Sans MS", 40), bg="white").pack(pady=10)
        tk.Button(card, text=name, font=("Comic Sans MS", 14, "bold"), bg="#0b1030", fg="white",
                  relief="flat", command=lambda lvl=name: start_game(lvl)).pack(pady=10, ipadx=12, ipady=6)

    window.mainloop()

choose_difficulty()
