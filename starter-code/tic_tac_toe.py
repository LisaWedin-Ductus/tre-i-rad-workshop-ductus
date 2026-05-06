"""
3-i-rad — GUI-version med tkinter
Stödjer 3×3, 7×7 och 10×10, med valfri AI-kommentator via Claude API.

Kör med: python tic_tac_toe.py
"""

import os
import random
import threading
import tkinter as tk
from typing import Any

import anthropic

EMPTY = " "

BOARD_CONFIGS: dict[str, dict[str, Any]] = {
    "3×3":   {"size": 3,  "win": 3, "font_size": 36, "cell_w": 4, "cell_h": 2, "pad": 4, "ai_depth": 9},
    "7×7":   {"size": 7,  "win": 5, "font_size": 24, "cell_w": 3, "cell_h": 1, "pad": 3, "ai_depth": 4},
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

COMMENTATOR_NONE = "Inga kommentarer"
COMMENTATOR_MODEL = "claude-haiku-4-5-20251001"

CHARACTER_PROMPTS: dict[str, str] = {
    "Donald Trump": (
        "You are Donald Trump commentating a tic-tac-toe game. "
        "Speak EXACTLY like Trump: use 'tremendous', 'bigly', 'believe me', "
        "'many people are saying', 'nobody knows tic-tac-toe better than me'. "
        "Make it about yourself and winning. Keep it to 1-2 sentences. Do not break character."
    ),
    "Hulk Hogan": (
        "You are Hulk Hogan commentating a tic-tac-toe game. "
        "Speak like Hulk Hogan: say 'brother', 'whatcha gonna do', use wrestling metaphors, "
        "reference Hulkamania, training, vitamins and prayers. "
        "Keep it to 1-2 sentences. Do not break character."
    ),
    "Dolly Parton": (
        "You are Dolly Parton commentating a tic-tac-toe game. "
        "Speak with Southern charm and wit: use country expressions, be warm and funny, "
        "occasionally reference country music, rhinestones or your Tennessee roots. "
        "Keep it to 1-2 sentences. Do not break character."
    ),
}

WIN_SCORE = 10_000_000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_api_key() -> str:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, _, val = line.partition("=")
                    if key.strip() == "ANTHROPIC_API_KEY":
                        return val.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "")


# ---------------------------------------------------------------------------
# Pure game logic
# ---------------------------------------------------------------------------

def generate_winning_lines(size: int, win: int) -> list[tuple[int, ...]]:
    lines = []
    for r in range(size):
        for c in range(size - win + 1):
            lines.append(tuple(r * size + c + i for i in range(win)))
    for c in range(size):
        for r in range(size - win + 1):
            lines.append(tuple((r + i) * size + c for i in range(win)))
    for r in range(size - win + 1):
        for c in range(size - win + 1):
            lines.append(tuple((r + i) * size + (c + i) for i in range(win)))
    for r in range(size - win + 1):
        for c in range(win - 1, size):
            lines.append(tuple((r + i) * size + (c - i) for i in range(win)))
    return lines


def build_cell_lines(winning_lines: list[tuple], n_cells: int) -> list[list[tuple]]:
    cell_lines: list[list[tuple]] = [[] for _ in range(n_cells)]
    for line in winning_lines:
        for idx in line:
            cell_lines[idx].append(line)
    return cell_lines


def check_winner(board: list[str], winning_lines: list[tuple]) -> tuple[str, tuple] | tuple[None, None]:
    for line in winning_lines:
        mark = board[line[0]]
        if mark != EMPTY and all(board[i] == mark for i in line):
            return mark, line
    return None, None


def _empty_cells(board: list[str]) -> list[int]:
    return [i for i, v in enumerate(board) if v == EMPTY]


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------

def _candidate_moves(board: list[str], size: int) -> list[int]:
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
    for line in winning_lines:
        vals = [board[i] for i in line]
        if vals.count(mark) == win - 1 and vals.count(EMPTY) == 1:
            return line[vals.index(EMPTY)]
    return None


def _evaluate(board: list[str], winning_lines: list[tuple], ai_mark: str, human_mark: str) -> int:
    score = 0
    for line in winning_lines:
        ai_count    = sum(1 for i in line if board[i] == ai_mark)
        human_count = sum(1 for i in line if board[i] == human_mark)
        if human_count == 0 and ai_count > 0:
            score += 10 ** ai_count
        elif ai_count == 0 and human_count > 0:
            score -= 10 ** human_count
    return score


def _move_priority(
    board: list[str], idx: int, mark: str, opponent: str,
    cell_lines: list[list[tuple]],
) -> int:
    board[idx] = mark
    if any(all(board[i] == mark for i in line) for line in cell_lines[idx]):
        board[idx] = EMPTY
        return 10_000_000
    board[idx] = EMPTY

    board[idx] = opponent
    if any(all(board[i] == opponent for i in line) for line in cell_lines[idx]):
        board[idx] = EMPTY
        return 1_000_000
    board[idx] = EMPTY

    board[idx] = mark
    best = 0
    for line in cell_lines[idx]:
        if not any(board[i] == opponent for i in line):
            cnt = sum(1 for i in line if board[i] == mark)
            if cnt > best:
                best = cnt
    board[idx] = EMPTY
    return 10 ** best


def _minimax(
    board: list[str], depth: int, is_max: bool, alpha: int, beta: int,
    ai_mark: str, human_mark: str, winning_lines: list[tuple],
    cell_lines: list[list[tuple]], size: int,
) -> int:
    winner, _ = check_winner(board, winning_lines)
    if winner == ai_mark:
        return WIN_SCORE + depth
    if winner == human_mark:
        return -WIN_SCORE - depth

    moves = _candidate_moves(board, size)
    if not moves or depth == 0:
        return _evaluate(board, winning_lines, ai_mark, human_mark)

    mark     = ai_mark if is_max else human_mark
    opponent = human_mark if is_max else ai_mark
    moves = sorted(moves, key=lambda i: _move_priority(board, i, mark, opponent, cell_lines), reverse=True)

    if is_max:
        best = -WIN_SCORE * 2
        for i in moves:
            board[i] = ai_mark
            best = max(best, _minimax(board, depth - 1, False, alpha, beta, ai_mark, human_mark, winning_lines, cell_lines, size))
            board[i] = EMPTY
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = WIN_SCORE * 2
        for i in moves:
            board[i] = human_mark
            best = min(best, _minimax(board, depth - 1, True, alpha, beta, ai_mark, human_mark, winning_lines, cell_lines, size))
            board[i] = EMPTY
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def get_ai_move(
    board: list[str], difficulty: str, ai_mark: str, human_mark: str,
    winning_lines: list[tuple], cell_lines: list[list[tuple]],
    win_length: int, board_size: int, ai_depth: int,
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

    candidates = _candidate_moves(board, board_size)
    candidates = sorted(candidates, key=lambda i: _move_priority(board, i, ai_mark, human_mark, cell_lines), reverse=True)
    best_score, best_move = -WIN_SCORE * 2, candidates[0]
    alpha = -WIN_SCORE * 2
    for i in candidates:
        board[i] = ai_mark
        score = _minimax(board, ai_depth - 1, False, alpha, WIN_SCORE * 2,
                         ai_mark, human_mark, winning_lines, cell_lines, board_size)
        board[i] = EMPTY
        if score > best_score:
            best_score, best_move = score, i
            alpha = best_score
        if best_score >= WIN_SCORE:
            break
    return best_move


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class TreIRad:
    HUMAN    = "X"
    AI       = "O"
    AI_DELAY = 500

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("3-i-rad")
        self.root.configure(bg=COLOR_BG)

        self._api_key = _load_api_key()

        # Game state
        self.board: list[str]       = []
        self.winning_lines: list    = []
        self.cell_lines: list       = []
        self.board_size: int        = 3
        self.win_length: int        = 3
        self.ai_depth: int          = 9
        self.current_player         = self.HUMAN
        self.game_over              = False
        self.game_started           = False
        self.ai_thinking            = False
        self.commentary_pending     = False
        self._pending_ai_move       = False
        self._session_id            = 0
        self._ai_after_id           = None
        self.cells: list[tk.Label]  = []
        self._selector_buttons: list[tk.Radiobutton] = []

        self.difficulty   = tk.StringVar(value=DIFFICULTY_MEDIUM)
        self.board_choice = tk.StringVar(value="3×3")
        self.commentator  = tk.StringVar(value=COMMENTATOR_NONE)

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
        self._build_commentator_bar()

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

        self._build_chat_window()

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

    def _build_commentator_bar(self) -> None:
        bar = tk.Frame(self.root, bg=COLOR_BG, pady=2)
        bar.pack()
        tk.Label(bar, text="Kommentator:", font=("Helvetica", 11),
                 bg=COLOR_BG, fg="black").pack(side="left", padx=(8, 6))
        for name in [COMMENTATOR_NONE, "Donald Trump", "Hulk Hogan", "Dolly Parton"]:
            tk.Radiobutton(
                bar, text=name, variable=self.commentator, value=name,
                font=("Helvetica", 11), fg="black",
                bg=COLOR_BG, activebackground=COLOR_BG, selectcolor=COLOR_BG,
            ).pack(side="left", padx=4)

    def _build_chat_window(self) -> None:
        outer = tk.Frame(self.root, bg=COLOR_BG)
        outer.pack(fill="x", padx=12, pady=(0, 10))

        tk.Label(outer, text="Kommentatorsbåset", font=("Helvetica", 10),
                 bg=COLOR_BG, fg="black").pack(anchor="w")

        inner = tk.Frame(outer, bg=COLOR_BG)
        inner.pack(fill="x")

        scrollbar = tk.Scrollbar(inner)
        scrollbar.pack(side="right", fill="y")

        self.chat_box = tk.Text(
            inner,
            height=5,
            wrap="word",
            state="disabled",
            yscrollcommand=scrollbar.set,
            bg="#FFFFFF",
            fg="black",
            font=("Helvetica", 11),
            relief="solid",
            bd=1,
        )
        self.chat_box.pack(side="left", fill="x", expand=True)
        scrollbar.config(command=self.chat_box.yview)

        self.chat_box.tag_config("name", font=("Helvetica", 11, "bold"))

    def _rebuild_grid(self) -> None:
        for widget in self._cells_frame.winfo_children():
            widget.destroy()
        self.cells.clear()

        cfg = BOARD_CONFIGS[self.board_choice.get()]
        self.board_size    = cfg["size"]
        self.win_length    = cfg["win"]
        self.ai_depth      = cfg["ai_depth"]
        self.winning_lines = generate_winning_lines(self.board_size, self.win_length)
        self.cell_lines    = build_cell_lines(self.winning_lines, self.board_size ** 2)

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

        self._session_id       += 1
        self.board              = [EMPTY] * (self.board_size ** 2)
        self.current_player     = self.HUMAN
        self.game_over          = False
        self.game_started       = False
        self.ai_thinking        = False
        self.commentary_pending = False
        self._pending_ai_move   = False

        self._set_selectors_enabled(True)
        for cell in self.cells:
            cell.config(text="", bg=COLOR_CELL, fg="black", cursor="hand2")
        self._update_status()

    def _update_status(self) -> None:
        if self.commentary_pending:
            self.status_label.config(text="Kommenterar...", fg="black")
        elif self.current_player == self.HUMAN:
            self.status_label.config(text="Din tur (X)", fg="black")
        else:
            self.status_label.config(text="Datorns tur (O)…", fg="black")

    # ------------------------------------------------------------------
    # Human interaction
    # ------------------------------------------------------------------

    def _on_hover(self, index: int, entering: bool) -> None:
        if self.game_over or self.ai_thinking or self.commentary_pending or self.board[index] != EMPTY:
            return
        self.cells[index].config(bg=COLOR_CELL_HOVER if entering else COLOR_CELL)

    def _on_cell_click(self, index: int) -> None:
        if self.game_over or self.ai_thinking or self.commentary_pending or self.board[index] != EMPTY:
            return

        if not self.game_started:
            self.game_started = True
            self._set_selectors_enabled(False)

        event = self._place_mark(index, self.HUMAN)

        if self.commentator.get() != COMMENTATOR_NONE:
            self._pending_ai_move = not self.game_over
            self._request_commentary(self.HUMAN, index, event)
        elif not self.game_over:
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
            self.winning_lines, self.cell_lines, self.win_length, self.board_size, self.ai_depth,
        )
        self.ai_thinking = False
        event = self._place_mark(index, self.AI)

        if self.commentator.get() != COMMENTATOR_NONE:
            self._pending_ai_move = False
            self._request_commentary(self.AI, index, event)
        elif not self.game_over:
            self.current_player = self.HUMAN
            self._update_status()

    # ------------------------------------------------------------------
    # Move logic — returns the event type for commentary
    # ------------------------------------------------------------------

    def _place_mark(self, index: int, player: str) -> str:
        opponent = self.HUMAN if player == self.AI else self.AI

        # Detect missed-win and block BEFORE changing the board
        winning_opp  = _winning_move(self.board, player, self.winning_lines, self.win_length)
        missed_win   = winning_opp is not None and winning_opp != index
        opp_near_win = _winning_move(self.board, opponent, self.winning_lines, self.win_length)
        blocks       = opp_near_win == index

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
            return "win"

        if EMPTY not in self.board:
            self.status_label.config(text="Oavgjort!", fg="black")
            self.game_over = True
            self._set_selectors_enabled(True)
            return "draw"

        if missed_win:
            return "missed_win"

        if _winning_move(self.board, player, self.winning_lines, self.win_length) is not None:
            return "created_threat"

        if blocks:
            return "blocked_threat"

        return "normal"

    # ------------------------------------------------------------------
    # Commentary
    # ------------------------------------------------------------------

    def _build_commentary_prompt(self, player: str, index: int, event: str) -> str:
        is_human    = player == self.HUMAN
        player_desc = "The human player (X)" if is_human else "The computer AI (O)"
        move_num    = self.board_size ** 2 - self.board.count(EMPTY)

        context = (
            f"Game: {self.board_size}×{self.board_size} tic-tac-toe, "
            f"{self.win_length} in a row to win. Move #{move_num}. "
        )
        descriptions = {
            "win":            f"{player_desc} just WON the game by getting {self.win_length} in a row!",
            "draw":           "The game ended in a DRAW — the board is full and nobody won!",
            "missed_win":     f"{player_desc} had a GUARANTEED winning move but played elsewhere — what a blunder!",
            "created_threat": f"{player_desc} just created a dangerous threat with {self.win_length - 1} in a row!",
            "blocked_threat": f"{player_desc} just blocked the opponent's winning threat just in time!",
            "normal":         f"{player_desc} made a move. The game continues.",
        }
        return context + descriptions.get(event, descriptions["normal"])

    def _request_commentary(self, player: str, index: int, event: str) -> None:
        character = self.commentator.get()
        if character == COMMENTATOR_NONE:
            return

        self.commentary_pending = True
        self._update_status()

        if not self._api_key:
            self.root.after(0, self._display_commentary,
                            character, "[API-nyckel saknas — kontrollera .env-filen]", self._session_id)
            return

        prompt = self._build_commentary_prompt(player, index, event)
        sid    = self._session_id
        threading.Thread(
            target=self._fetch_commentary,
            args=(character, prompt, sid),
            daemon=True,
        ).start()

    def _fetch_commentary(self, character: str, prompt: str, sid: int) -> None:
        try:
            client   = anthropic.Anthropic(api_key=self._api_key)
            response = client.messages.create(
                model=COMMENTATOR_MODEL,
                max_tokens=120,
                system=CHARACTER_PROMPTS[character],
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
        except Exception as exc:
            text = f"[Fel: {exc}]"
        self.root.after(0, self._display_commentary, character, text, sid)

    def _display_commentary(self, character: str, text: str, sid: int) -> None:
        if sid != self._session_id:
            return  # stale response from a previous game — discard

        self.commentary_pending = False

        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"{character}: ", "name")
        self.chat_box.insert("end", f"{text}\n\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

        self._continue_after_commentary()

    def _continue_after_commentary(self) -> None:
        if self.game_over:
            return
        if self._pending_ai_move:
            self._pending_ai_move = False
            self.current_player   = self.AI
            self.ai_thinking      = True
            self._update_status()
            self._ai_after_id = self.root.after(self.AI_DELAY, self._do_ai_move)
        else:
            self.current_player = self.HUMAN
            self._update_status()


if __name__ == "__main__":
    root = tk.Tk()
    TreIRad(root)
    root.mainloop()
