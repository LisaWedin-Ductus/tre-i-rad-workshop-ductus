"""
3-i-rad — GUI-version med tkinter

Kör med: python tic_tac_toe.py
"""

import tkinter as tk
import random

EMPTY = " "

WINNING_LINES: list[tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

COLOR_BG         = "#F5F5F0"
COLOR_CELL       = "#FFFFFF"
COLOR_CELL_HOVER = "#EAEAEA"
COLOR_X          = "#C0392B"
COLOR_O          = "#2980B9"
COLOR_WIN        = "#F9E79F"
COLOR_BUTTON     = "#2C3E50"
COLOR_SUBTEXT    = "#555555"

DIFFICULTY_EASY   = "Lätt"
DIFFICULTY_MEDIUM = "Medel"
DIFFICULTY_HARD   = "Svår"


# ---------------------------------------------------------------------------
# Pure game logic
# ---------------------------------------------------------------------------

def check_winner(board: list[str]) -> tuple[str, tuple[int, int, int]] | tuple[None, None]:
    for line in WINNING_LINES:
        a, b, c = line
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], line
    return None, None


def is_board_full(board: list[str]) -> bool:
    return EMPTY not in board


def _empty_cells(board: list[str]) -> list[int]:
    return [i for i, v in enumerate(board) if v == EMPTY]


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------

def _winning_move(board: list[str], mark: str) -> int | None:
    """Returns the index that wins immediately for `mark`, or None."""
    for line in WINNING_LINES:
        a, b, c = line
        vals = [board[a], board[b], board[c]]
        if vals.count(mark) == 2 and vals.count(EMPTY) == 1:
            return line[vals.index(EMPTY)]
    return None


def _minimax(board: list[str], is_maximizing: bool, ai_mark: str, human_mark: str) -> int:
    winner, _ = check_winner(board)
    if winner == ai_mark:
        return 10
    if winner == human_mark:
        return -10
    if is_board_full(board):
        return 0

    scores = []
    for i in _empty_cells(board):
        board[i] = ai_mark if is_maximizing else human_mark
        scores.append(_minimax(board, not is_maximizing, ai_mark, human_mark))
        board[i] = EMPTY
    return max(scores) if is_maximizing else min(scores)


def get_ai_move(board: list[str], difficulty: str, ai_mark: str, human_mark: str) -> int:
    available = _empty_cells(board)

    if difficulty == DIFFICULTY_EASY:
        return random.choice(available)

    if difficulty == DIFFICULTY_MEDIUM:
        move = _winning_move(board, ai_mark)
        if move is not None:
            return move
        move = _winning_move(board, human_mark)
        if move is not None:
            return move
        return random.choice(available)

    # Hard: minimax — never loses
    best_score, best_move = -100, available[0]
    for i in available:
        board[i] = ai_mark
        score = _minimax(board, False, ai_mark, human_mark)
        board[i] = EMPTY
        if score > best_score:
            best_score, best_move = score, i
    return best_move


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class TreIRad:
    HUMAN    = "X"
    AI       = "O"
    AI_DELAY = 500  # ms — short pause so the AI doesn't feel instant

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("3-i-rad")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        self.board: list[str]   = []
        self.current_player     = self.HUMAN
        self.game_over          = False
        self.game_started       = False
        self.ai_thinking        = False
        self._ai_after_id: str | None = None
        self.cells: list[tk.Label] = []
        self.diff_buttons: list[tk.Radiobutton] = []
        self.difficulty = tk.StringVar(value=DIFFICULTY_MEDIUM)

        self._build_ui()
        self._new_game()

    # ------------------------------------------------------------------
    # UI construction (called once)
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._build_difficulty_bar()

        self.status_label = tk.Label(
            self.root, text="", font=("Helvetica", 16), bg=COLOR_BG, pady=8,
        )
        self.status_label.grid(row=1, column=0, columnspan=3, sticky="ew")

        for i in range(9):
            cell = tk.Label(
                self.root,
                text="",
                font=("Helvetica", 36, "bold"),
                width=4, height=2,
                bg=COLOR_CELL, relief="solid", bd=1, cursor="hand2",
            )
            cell.grid(row=i // 3 + 2, column=i % 3, padx=4, pady=4)
            cell.bind("<Button-1>", lambda e, idx=i: self._on_cell_click(idx))
            cell.bind("<Enter>",    lambda e, idx=i: self._on_hover(idx, True))
            cell.bind("<Leave>",    lambda e, idx=i: self._on_hover(idx, False))
            self.cells.append(cell)

        tk.Button(
            self.root,
            text="Nytt spel",
            font=("Helvetica", 13),
            bg=COLOR_BUTTON, fg="#000000",
            activebackground="#3D5166", activeforeground="#000000",
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=self._new_game,
        ).grid(row=5, column=0, columnspan=3, pady=12)

    def _build_difficulty_bar(self) -> None:
        bar = tk.Frame(self.root, bg=COLOR_BG, pady=8)
        bar.grid(row=0, column=0, columnspan=3)

        tk.Label(
            bar, text="Svårighetsgrad:", font=("Helvetica", 11),
            bg=COLOR_BG, fg="black",
        ).pack(side="left", padx=(8, 6))

        for level in [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]:
            btn = tk.Radiobutton(
                bar,
                text=level,
                variable=self.difficulty,
                value=level,
                font=("Helvetica", 11),
                fg="black",
                bg=COLOR_BG, activebackground=COLOR_BG,
                selectcolor=COLOR_BG,
            )
            btn.pack(side="left", padx=4)
            self.diff_buttons.append(btn)

    # ------------------------------------------------------------------
    # Game flow
    # ------------------------------------------------------------------

    def _set_difficulty_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for btn in self.diff_buttons:
            btn.config(state=state)

    def _new_game(self) -> None:
        if self._ai_after_id is not None:
            self.root.after_cancel(self._ai_after_id)
            self._ai_after_id = None

        self.board          = [EMPTY] * 9
        self.current_player = self.HUMAN
        self.game_over      = False
        self.game_started   = False
        self.ai_thinking    = False

        self._set_difficulty_enabled(True)
        for cell in self.cells:
            cell.config(text="", bg=COLOR_CELL, fg="black", cursor="hand2")
        self._update_status()

    def _update_status(self) -> None:
        if self.current_player == self.HUMAN:
            self.status_label.config(text="Din tur (X)", fg="black")
        else:
            self.status_label.config(text="Datorns tur (O)…", fg="black")

    # ------------------------------------------------------------------
    # Human interaction
    # ------------------------------------------------------------------

    def _on_hover(self, index: int, entering: bool) -> None:
        if self.game_over or self.ai_thinking or self.board[index] != EMPTY:
            return
        self.cells[index].config(bg=COLOR_CELL_HOVER if entering else COLOR_CELL)

    def _on_cell_click(self, index: int) -> None:
        if self.game_over or self.ai_thinking or self.board[index] != EMPTY:
            return

        if not self.game_started:
            self.game_started = True
            self._set_difficulty_enabled(False)

        self._place_mark(index, self.HUMAN)

        if not self.game_over:
            self.current_player = self.AI
            self.ai_thinking    = True
            self._update_status()
            self._ai_after_id = self.root.after(self.AI_DELAY, self._do_ai_move)

    # ------------------------------------------------------------------
    # AI turn
    # ------------------------------------------------------------------

    def _do_ai_move(self) -> None:
        self._ai_after_id = None
        if self.game_over:
            self.ai_thinking = False
            return

        index = get_ai_move(self.board, self.difficulty.get(), self.AI, self.HUMAN)
        self._place_mark(index, self.AI)
        self.ai_thinking = False

        if not self.game_over:
            self.current_player = self.HUMAN
            self._update_status()

    # ------------------------------------------------------------------
    # Shared move logic
    # ------------------------------------------------------------------

    def _place_mark(self, index: int, player: str) -> None:
        self.board[index] = player
        color = COLOR_X if player == self.HUMAN else COLOR_O
        self.cells[index].config(text=player, fg=color, cursor="arrow", bg=COLOR_CELL)

        winner, winning_line = check_winner(self.board)
        if winner is not None:
            for i in winning_line:
                self.cells[i].config(bg=COLOR_WIN)
            label = "Du vinner! 🎉" if winner == self.HUMAN else "Datorn vinner!"
            self.status_label.config(text=label, fg="black")
            self.game_over = True
            self._set_difficulty_enabled(True)
            return

        if is_board_full(self.board):
            self.status_label.config(text="Oavgjort!", fg="black")
            self.game_over = True
            self._set_difficulty_enabled(True)


if __name__ == "__main__":
    root = tk.Tk()
    TreIRad(root)
    root.mainloop()
