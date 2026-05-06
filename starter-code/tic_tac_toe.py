"""
3-i-rad — tkinter MVC-version

Model:      GameModel  — spelstatus och domänlogik, ingen UI-kod
View:       GameView   — tkinter-widgets, render(model) synkar UI mot modellen
Controller: GameController — tar emot händelser från vyn, uppdaterar modellen,
                             anropar render

Kör med: python tic_tac_toe.py
"""

import tkinter as tk
from dataclasses import dataclass, field

EMPTY = " "

WINNING_LINES: list[tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

COLOR_BG        = "#F5F5F0"
COLOR_CELL      = "#FFFFFF"
COLOR_CELL_HOVER = "#EAEAEA"
COLOR_X         = "#C0392B"
COLOR_O         = "#2980B9"
COLOR_WIN       = "#F9E79F"
COLOR_BUTTON    = "#2C3E50"
COLOR_SUBTEXT   = "#555555"


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

@dataclass
class GameModel:
    board: list[str]              = field(default_factory=lambda: [EMPTY] * 9)
    current_player: str           = "X"
    game_over: bool               = False
    winner: str | None            = None
    winning_line: tuple | None    = None

    def reset(self) -> None:
        self.board          = [EMPTY] * 9
        self.current_player = "X"
        self.game_over      = False
        self.winner         = None
        self.winning_line   = None

    def is_valid_move(self, index: int) -> bool:
        return not self.game_over and self.board[index] == EMPTY

    def make_move(self, index: int) -> bool:
        """Places the current player's mark. Returns True if the move changed state."""
        if not self.is_valid_move(index):
            return False

        self.board[index] = self.current_player

        winner, line = self._check_winner()
        if winner:
            self.winner       = winner
            self.winning_line = line
            self.game_over    = True
        elif EMPTY not in self.board:
            self.game_over = True
        else:
            self.current_player = "O" if self.current_player == "X" else "X"

        return True

    def _check_winner(self) -> tuple[str, tuple] | tuple[None, None]:
        for line in WINNING_LINES:
            a, b, c = line
            if self.board[a] != EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a], line
        return None, None


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------

class GameView:
    def __init__(self, root: tk.Tk, controller: "GameController") -> None:
        self.root       = root
        self.controller = controller
        self.cells: list[tk.Label] = []

        root.title("3-i-rad")
        root.resizable(False, False)
        root.configure(bg=COLOR_BG)

        self._build_ui()

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
            cell.bind("<Button-1>", lambda e, idx=i: self.controller.on_cell_click(idx))
            cell.bind("<Enter>",    lambda e, idx=i: self.controller.on_hover(idx, entering=True))
            cell.bind("<Leave>",    lambda e, idx=i: self.controller.on_hover(idx, entering=False))
            self.cells.append(cell)

        tk.Button(
            self.root,
            text="Nytt spel",
            font=("Helvetica", 13),
            bg=COLOR_BUTTON,
            fg="#000000",
            activebackground="#3D5166",
            activeforeground="#000000",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.controller.on_new_game,
        ).grid(row=4, column=0, columnspan=3, pady=12)

    def render(self, model: GameModel) -> None:
        """Syncs all UI elements to the current model state."""
        self._render_cells(model)
        self._render_status(model)

    def _render_cells(self, model: GameModel) -> None:
        for i, mark in enumerate(model.board):
            cell = self.cells[i]
            if mark == EMPTY:
                cell.config(text="", bg=COLOR_CELL, fg="black", cursor="hand2")
            else:
                color = COLOR_X if mark == "X" else COLOR_O
                cell.config(text=mark, fg=color, cursor="arrow")

        if model.winning_line:
            for i in model.winning_line:
                self.cells[i].config(bg=COLOR_WIN)

    def _render_status(self, model: GameModel) -> None:
        if model.winner:
            color = COLOR_X if model.winner == "X" else COLOR_O
            text  = f"Spelare {model.winner} vinner! 🎉"
        elif model.game_over:
            color, text = COLOR_SUBTEXT, "Oavgjort!"
        else:
            color = COLOR_X if model.current_player == "X" else COLOR_O
            text  = f"Spelare {model.current_player}:s tur"

        self.status_label.config(text=text, fg=color)

    def update_hover(self, index: int, entering: bool, model: GameModel) -> None:
        """Visual-only hover highlight — no state change, reads model to decide."""
        if model.game_over or model.board[index] != EMPTY:
            return
        self.cells[index].config(bg=COLOR_CELL_HOVER if entering else COLOR_CELL)


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------

class GameController:
    def __init__(self, root: tk.Tk) -> None:
        self.model = GameModel()
        self.view  = GameView(root, self)
        self.view.render(self.model)

    def on_cell_click(self, index: int) -> None:
        if self.model.make_move(index):
            self.view.render(self.model)

    def on_hover(self, index: int, entering: bool) -> None:
        self.view.update_hover(index, entering, self.model)

    def on_new_game(self) -> None:
        self.model.reset()
        self.view.render(self.model)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    GameController(root)
    root.mainloop()
