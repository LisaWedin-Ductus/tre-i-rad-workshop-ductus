"""
3-i-rad — GUI-version med tkinter
Stödjer 3×3, 7×7 och 10×10

Kör med: python tic_tac_toe.py
"""

import tkinter as tk
import random
from typing import Any

EMPTY = " "

# size: board side length, win: marks in a row needed to win
# font_size/cell_w/cell_h: tkinter Label sizing per board
# ai_depth: minimax search depth (smaller boards can afford deeper search)
BOARD_CONFIGS: dict[str, dict[str, Any]] = {
    "3×3":   {"size": 3,  "win": 3, "font_size": 36, "cell_w": 4, "cell_h": 2, "pad": 4, "ai_depth": 9},
    "7×7":   {"size": 7,  "win": 5, "font_size": 24, "cell_w": 3, "cell_h": 1, "pad": 3, "ai_depth": 3},
    "10×10": {"size": 10, "win": 5, "font_size": 18, "cell_w": 3, "cell_h": 1, "pad": 2, "ai_depth": 3},
}

COLOR_BG         = "#F5F5F0"
COLOR_CELL       = "#FFFFFF"
COLOR_CELL_HOVER = "#EAEAEA"
COLOR_X          = "#C0392B"
COLOR_O          = "#2980B9"
COLOR_WIN        = "#F9E79F"
COLOR_BUTTON     = "#2C3E50"

DIFFICULTY_EASY   = "Lätt"
DIFFICULTY_MEDIUM = "Medel"
DIFFICULTY_HARD   = "Svår"

WIN_SCORE = 10_000_000


# ---------------------------------------------------------------------------
# Pure game logic
# ---------------------------------------------------------------------------

def generate_winning_lines(size: int, win: int) -> list[tuple[int, ...]]:
    lines = []
    for r in range(size):                          # horizontal
        for c in range(size - win + 1):
            lines.append(tuple(r * size + c + i for i in range(win)))
    for c in range(size):                          # vertical
        for r in range(size - win + 1):
            lines.append(tuple((r + i) * size + c for i in range(win)))
    for r in range(size - win + 1):               # diagonal: top-left → bottom-right
        for c in range(size - win + 1):
            lines.append(tuple((r + i) * size + (c + i) for i in range(win)))
    for r in range(size - win + 1):               # diagonal: top-right → bottom-left
        for c in range(win - 1, size):
            lines.append(tuple((r + i) * size + (c - i) for i in range(win)))
    return lines


def check_winner(board: list[str], winning_lines: list[tuple]) -> tuple[str, tuple] | tuple[None, None]:
    for line in winning_lines:
        mark = board[line[0]]
        if mark != EMPTY and all(board[i] == mark for i in line):
            return mark, line
    return None, None


def _empty_cells(board: list[str]) -> list[int]:
    return [i for i, v in enumerate(board) if v == EMPTY]


# ---------------------------------------------------------------------------
# AI helpers
# ---------------------------------------------------------------------------

def _candidate_moves(board: list[str], size: int) -> list[int]:
    """For boards larger than 3×3, restrict search to cells directly adjacent
    (radius 1) to any existing mark. Radius 1 is sufficient for win=5 since
    all relevant extensions are one step from existing marks."""
    if size == 3:
        return _empty_cells(board)

    occupied = [i for i, v in enumerate(board) if v != EMPTY]
    if not occupied:
        center = size // 2
        return [center * size + center]

    candidates: set[int] = set()
    for pos in occupied:
        r, c = divmod(pos, size)
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size:
                    idx = nr * size + nc
                    if board[idx] == EMPTY:
                        candidates.add(idx)
    return list(candidates) or _empty_cells(board)


def _winning_move(board: list[str], mark: str, winning_lines: list[tuple], win: int) -> int | None:
    """Return the index that immediately completes `win - 1` in a row for `mark`."""
    for line in winning_lines:
        vals = [board[i] for i in line]
        if vals.count(mark) == win - 1 and vals.count(EMPTY) == 1:
            return line[vals.index(EMPTY)]
    return None


def _evaluate(board: list[str], winning_lines: list[tuple], ai_mark: str, human_mark: str) -> int:
    """Heuristic: score lines by consecutive mark count (5^k per partial line)."""
    score = 0
    for line in winning_lines:
        ai_count    = sum(1 for i in line if board[i] == ai_mark)
        human_count = sum(1 for i in line if board[i] == human_mark)
        if human_count == 0 and ai_count > 0:
            score += 5 ** ai_count
        elif ai_count == 0 and human_count > 0:
            score -= 5 ** human_count
    return score


def _minimax(
    board: list[str], depth: int, is_max: bool, alpha: int, beta: int,
    ai_mark: str, human_mark: str, winning_lines: list[tuple], size: int,
) -> int:
    winner, _ = check_winner(board, winning_lines)
    if winner == ai_mark:
        return WIN_SCORE + depth
    if winner == human_mark:
        return -WIN_SCORE - depth

    moves = _candidate_moves(board, size)
    if not moves or depth == 0:
        return _evaluate(board, winning_lines, ai_mark, human_mark)

    if is_max:
        best = -WIN_SCORE * 2
        for i in moves:
            board[i] = ai_mark
            best = max(best, _minimax(board, depth - 1, False, alpha, beta, ai_mark, human_mark, winning_lines, size))
            board[i] = EMPTY
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = WIN_SCORE * 2
        for i in moves:
            board[i] = human_mark
            best = min(best, _minimax(board, depth - 1, True, alpha, beta, ai_mark, human_mark, winning_lines, size))
            board[i] = EMPTY
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def get_ai_move(
    board: list[str], difficulty: str, ai_mark: str, human_mark: str,
    winning_lines: list[tuple], win_length: int, board_size: int, ai_depth: int,
) -> int:
    available = _empty_cells(board)

    if difficulty == DIFFICULTY_EASY:
        return random.choice(available)

    if difficulty == DIFFICULTY_MEDIUM:
        move = _winning_move(board, ai_mark, winning_lines, win_length)
        if move is not None:
            return move
        move = _winning_move(board, human_mark, winning_lines, win_length)
        if move is not None:
            return move
        return random.choice(available)

    # Hard: alpha-beta minimax with candidate filtering
    candidates = _candidate_moves(board, board_size)
    best_score, best_move = -WIN_SCORE * 2, candidates[0]
    for i in candidates:
        board[i] = ai_mark
        score = _minimax(board, ai_depth - 1, False, -WIN_SCORE * 2, WIN_SCORE * 2,
                         ai_mark, human_mark, winning_lines, board_size)
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
    AI_DELAY = 500  # ms

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("3-i-rad")
        self.root.configure(bg=COLOR_BG)

        # Game state
        self.board: list[str]       = []
        self.winning_lines: list    = []
        self.board_size: int        = 3
        self.win_length: int        = 3
        self.ai_depth: int          = 9
        self.current_player         = self.HUMAN
        self.game_over              = False
        self.game_started           = False
        self.ai_thinking            = False
        self._ai_after_id           = None
        self.cells: list[tk.Label]  = []
        self._selector_buttons: list[tk.Radiobutton] = []

        self.difficulty   = tk.StringVar(value=DIFFICULTY_MEDIUM)
        self.board_choice = tk.StringVar(value="3×3")

        self._build_static_ui()
        self.board_choice.trace_add("write", self._on_board_size_change)
        self._rebuild_grid()
        self._new_game()

    # ------------------------------------------------------------------
    # UI construction (called once)
    # ------------------------------------------------------------------

    def _build_static_ui(self) -> None:
        self._build_difficulty_bar()
        self._build_board_size_bar()

        self.status_label = tk.Label(
            self.root, text="", font=("Helvetica", 16), bg=COLOR_BG, pady=6,
        )
        self.status_label.pack()

        self._cells_frame = tk.Frame(self.root, bg=COLOR_BG)
        self._cells_frame.pack(padx=8, pady=4)

        tk.Button(
            self.root,
            text="Nytt spel",
            font=("Helvetica", 13),
            bg=COLOR_BUTTON, fg="#000000",
            activebackground="#3D5166", activeforeground="#000000",
            relief="flat", padx=16, pady=8, cursor="hand2",
            command=self._new_game,
        ).pack(pady=10)

    def _build_difficulty_bar(self) -> None:
        bar = tk.Frame(self.root, bg=COLOR_BG, pady=6)
        bar.pack()
        tk.Label(bar, text="Svårighetsgrad:", font=("Helvetica", 11),
                 bg=COLOR_BG, fg="black").pack(side="left", padx=(8, 6))
        for level in [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]:
            btn = tk.Radiobutton(
                bar, text=level, variable=self.difficulty, value=level,
                font=("Helvetica", 11), fg="black",
                bg=COLOR_BG, activebackground=COLOR_BG, selectcolor=COLOR_BG,
            )
            btn.pack(side="left", padx=4)
            self._selector_buttons.append(btn)

    def _build_board_size_bar(self) -> None:
        bar = tk.Frame(self.root, bg=COLOR_BG, pady=2)
        bar.pack()
        tk.Label(bar, text="Brädstorlek:", font=("Helvetica", 11),
                 bg=COLOR_BG, fg="black").pack(side="left", padx=(8, 6))
        for size_key in BOARD_CONFIGS:
            btn = tk.Radiobutton(
                bar, text=size_key, variable=self.board_choice, value=size_key,
                font=("Helvetica", 11), fg="black",
                bg=COLOR_BG, activebackground=COLOR_BG, selectcolor=COLOR_BG,
            )
            btn.pack(side="left", padx=4)
            self._selector_buttons.append(btn)

    def _rebuild_grid(self) -> None:
        """Tear down all cell widgets and build a new grid for the current board size."""
        for widget in self._cells_frame.winfo_children():
            widget.destroy()
        self.cells.clear()

        cfg = BOARD_CONFIGS[self.board_choice.get()]
        self.board_size    = cfg["size"]
        self.win_length    = cfg["win"]
        self.ai_depth      = cfg["ai_depth"]
        self.winning_lines = generate_winning_lines(self.board_size, self.win_length)

        font = ("Helvetica", cfg["font_size"], "bold")

        for i in range(self.board_size ** 2):
            cell = tk.Label(
                self._cells_frame,
                text="",
                font=font,
                width=cfg["cell_w"], height=cfg["cell_h"],
                bg=COLOR_CELL, relief="solid", bd=1, cursor="hand2",
            )
            row, col = divmod(i, self.board_size)
            cell.grid(row=row, column=col, padx=cfg["pad"], pady=cfg["pad"])
            cell.bind("<Button-1>", lambda _, idx=i: self._on_cell_click(idx))
            cell.bind("<Enter>",    lambda _, idx=i: self._on_hover(idx, True))
            cell.bind("<Leave>",    lambda _, idx=i: self._on_hover(idx, False))
            self.cells.append(cell)

    # ------------------------------------------------------------------
    # Game flow
    # ------------------------------------------------------------------

    def _set_selectors_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for btn in self._selector_buttons:
            btn.config(state=state)

    def _on_board_size_change(self, *_) -> None:
        if self._ai_after_id is not None:
            self.root.after_cancel(self._ai_after_id)
            self._ai_after_id = None
        self._rebuild_grid()
        self._new_game()

    def _new_game(self) -> None:
        if self._ai_after_id is not None:
            self.root.after_cancel(self._ai_after_id)
            self._ai_after_id = None

        self.board          = [EMPTY] * (self.board_size ** 2)
        self.current_player = self.HUMAN
        self.game_over      = False
        self.game_started   = False
        self.ai_thinking    = False

        self._set_selectors_enabled(True)
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
            self._set_selectors_enabled(False)

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

        index = get_ai_move(
            self.board, self.difficulty.get(), self.AI, self.HUMAN,
            self.winning_lines, self.win_length, self.board_size, self.ai_depth,
        )
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

        winner, winning_line = check_winner(self.board, self.winning_lines)
        if winner is not None:
            for i in winning_line:
                self.cells[i].config(bg=COLOR_WIN)
            label = "Du vinner! 🎉" if winner == self.HUMAN else "Datorn vinner!"
            self.status_label.config(text=label, fg="black")
            self.game_over = True
            self._set_selectors_enabled(True)
            return

        if EMPTY not in self.board:
            self.status_label.config(text="Oavgjort!", fg="black")
            self.game_over = True
            self._set_selectors_enabled(True)


if __name__ == "__main__":
    root = tk.Tk()
    TreIRad(root)
    root.mainloop()
