"""
3-i-rad — GUI-version med tkinter

Två spelare turas om att placera X och O på ett 3x3-bräde.
Spelet avslutas när någon får tre i rad eller brädet är fullt.

Kör med: python tic_tac_toe.py
"""

import tkinter as tk

EMPTY = " "

WINNING_LINES: list[tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rader
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # kolumner
    (0, 4, 8), (2, 4, 6),             # diagonaler
]

COLOR_BG = "#F5F5F0"
COLOR_CELL = "#FFFFFF"
COLOR_CELL_HOVER = "#EAEAEA"
COLOR_X = "#C0392B"
COLOR_O = "#2980B9"
COLOR_WIN = "#F9E79F"
COLOR_BUTTON = "#2C3E50"
COLOR_BUTTON_TEXT = "#000000"


def create_board() -> list[str]:
    return [EMPTY] * 9


def check_winner(board: list[str]) -> tuple[str, tuple[int, int, int]] | tuple[None, None]:
    for line in WINNING_LINES:
        a, b, c = line
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], line
    return None, None


def is_board_full(board: list[str]) -> bool:
    return EMPTY not in board


class TreIRad:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("3-i-rad")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        self.board: list[str] = []
        self.current_player: str = "X"
        self.game_over: bool = False
        self.cells: list[tk.Label] = []

        self._build_ui()
        self._new_game()

    def _build_ui(self) -> None:
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 16),
            bg=COLOR_BG,
            pady=12,
        )
        self.status_label.grid(row=0, column=0, columnspan=3, sticky="ew")

        for i in range(9):
            cell = tk.Label(
                self.root,
                text="",
                font=("Helvetica", 36, "bold"),
                width=4,
                height=2,
                bg=COLOR_CELL,
                relief="solid",
                bd=1,
                cursor="hand2",
            )
            cell.grid(row=i // 3 + 1, column=i % 3, padx=4, pady=4)
            cell.bind("<Button-1>", lambda e, idx=i: self._on_cell_click(idx))
            cell.bind("<Enter>", lambda e, idx=i: self._on_hover(idx, True))
            cell.bind("<Leave>", lambda e, idx=i: self._on_hover(idx, False))
            self.cells.append(cell)

        self.restart_btn = tk.Button(
            self.root,
            text="Nytt spel",
            font=("Helvetica", 13),
            bg=COLOR_BUTTON,
            fg=COLOR_BUTTON_TEXT,
            activebackground="#3D5166",
            activeforeground=COLOR_BUTTON_TEXT,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._new_game,
        )
        self.restart_btn.grid(row=4, column=0, columnspan=3, pady=12)

    def _new_game(self) -> None:
        self.board = create_board()
        self.current_player = "X"
        self.game_over = False
        for cell in self.cells:
            cell.config(text="", bg=COLOR_CELL, fg="black", cursor="hand2")
        self._update_status()

    def _update_status(self) -> None:
        color = COLOR_X if self.current_player == "X" else COLOR_O
        self.status_label.config(
            text=f"Spelare {self.current_player}:s tur",
            fg=color,
        )

    def _on_hover(self, index: int, entering: bool) -> None:
        if self.game_over or self.board[index] != EMPTY:
            return
        self.cells[index].config(bg=COLOR_CELL_HOVER if entering else COLOR_CELL)

    def _on_cell_click(self, index: int) -> None:
        if self.game_over or self.board[index] != EMPTY:
            return

        self.board[index] = self.current_player
        color = COLOR_X if self.current_player == "X" else COLOR_O
        self.cells[index].config(text=self.current_player, fg=color, cursor="arrow")

        winner, winning_line = check_winner(self.board)
        if winner is not None:
            for i in winning_line:
                self.cells[i].config(bg=COLOR_WIN)
            self.status_label.config(text=f"Spelare {winner} vinner! 🎉", fg=color)
            self.game_over = True
            return

        if is_board_full(self.board):
            self.status_label.config(text="Oavgjort!", fg="#555555")
            self.game_over = True
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self._update_status()


if __name__ == "__main__":
    root = tk.Tk()
    TreIRad(root)
    root.mainloop()
