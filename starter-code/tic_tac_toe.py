"""
3-i-rad — grafisk version (tkinter)

Två spelare turas om att klicka på rutor i ett 3x3-bräde.
Spelet är helt musdrivet; ingen terminalinmatning krävs under spelet.

Kör med: python tic_tac_toe.py
"""

import tkinter as tk
from tkinter import font as tkfont

EMPTY = " "
PLAYERS = ("X", "O")

WINNING_LINES: list[tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

CELL_BG = "#f5f5f5"
CELL_BG_HOVER = "#eaeaea"
WIN_BG = "#ffd54a"
X_COLOR = "#1565c0"
O_COLOR = "#c62828"


def find_winning_line(board: list[str]) -> tuple[int, int, int] | None:
    for a, b, c in WINNING_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return (a, b, c)
    return None


class TicTacToeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("3-i-rad")
        self.root.resizable(False, False)

        self.board: list[str] = [EMPTY] * 9
        self.current_player: str = PLAYERS[0]
        self.game_over: bool = False

        self.cell_font = tkfont.Font(family="Helvetica", size=48, weight="bold")
        self.status_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.button_font = tkfont.Font(family="Helvetica", size=12)

        self.status = tk.Label(
            root,
            text="",
            font=self.status_font,
            pady=12,
        )
        self.status.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.cells: list[tk.Label] = []
        for i in range(9):
            r, c = divmod(i, 3)
            cell = tk.Label(
                root,
                text="",
                font=self.cell_font,
                width=2,
                height=1,
                bg=CELL_BG,
                relief="ridge",
                borderwidth=2,
                cursor="hand2",
            )
            cell.grid(row=1 + r, column=c, padx=4, pady=4, ipadx=8, ipady=8)
            cell.bind("<Button-1>", lambda _e, idx=i: self.on_cell_click(idx))
            cell.bind("<Enter>", lambda _e, idx=i: self.on_cell_enter(idx))
            cell.bind("<Leave>", lambda _e, idx=i: self.on_cell_leave(idx))
            self.cells.append(cell)

        self.new_game_button = tk.Button(
            root,
            text="Nytt spel",
            font=self.button_font,
            command=self.reset,
            cursor="hand2",
        )
        self.new_game_button.grid(row=4, column=0, columnspan=3, sticky="ew", padx=4, pady=(8, 12))

        self.reset()

    def on_cell_click(self, idx: int) -> None:
        if self.game_over or self.board[idx] != EMPTY:
            return

        self.board[idx] = self.current_player
        self.render_cell(idx)

        line = find_winning_line(self.board)
        if line is not None:
            self.finish_with_win(self.current_player, line)
            return

        if EMPTY not in self.board:
            self.finish_with_draw()
            return

        self.current_player = PLAYERS[1] if self.current_player == PLAYERS[0] else PLAYERS[0]
        self.update_status()

    def on_cell_enter(self, idx: int) -> None:
        if self.game_over or self.board[idx] != EMPTY:
            return
        self.cells[idx].configure(bg=CELL_BG_HOVER)

    def on_cell_leave(self, idx: int) -> None:
        if self.game_over or self.board[idx] != EMPTY:
            return
        self.cells[idx].configure(bg=CELL_BG)

    def render_cell(self, idx: int) -> None:
        mark = self.board[idx]
        color = X_COLOR if mark == "X" else O_COLOR if mark == "O" else "black"
        self.cells[idx].configure(text=mark if mark != EMPTY else "", fg=color, bg=CELL_BG)

    def update_status(self) -> None:
        color = X_COLOR if self.current_player == "X" else O_COLOR
        self.status.configure(text=f"{self.current_player}s tur", fg=color)

    def finish_with_win(self, winner: str, line: tuple[int, int, int]) -> None:
        self.game_over = True
        for idx in line:
            self.cells[idx].configure(bg=WIN_BG)
        color = X_COLOR if winner == "X" else O_COLOR
        self.status.configure(text=f"{winner} vinner!", fg=color)

    def finish_with_draw(self) -> None:
        self.game_over = True
        self.status.configure(text="Oavgjort!", fg="black")

    def reset(self) -> None:
        self.board = [EMPTY] * 9
        self.current_player = PLAYERS[0]
        self.game_over = False
        for i in range(9):
            self.cells[i].configure(text="", bg=CELL_BG, fg="black")
        self.update_status()


def main() -> None:
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
