"""
3-i-rad — pygame-version

Två spelare turas om att placera X och O på ett 3x3-bräde.
Spelet avslutas när någon får tre i rad eller brädet är fullt.

Kör med: python tic_tac_toe.py
"""

import sys
import pygame

EMPTY = " "

WINNING_LINES: list[tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

C_BG         = (15,  23,  42)
C_GRID       = (51,  65,  85)
C_CELL_HOVER = (30,  41,  59)
C_X          = (239, 68,  68)
C_O          = (59,  130, 246)
C_WIN_LINE   = (251, 191, 36)
C_TEXT       = (241, 245, 249)
C_SUBTEXT    = (148, 163, 184)
C_BTN        = (30,  41,  59)
C_BTN_HOVER  = (51,  65,  85)

WIN_W, WIN_H = 480, 600
CELL         = 130
GRID_SIZE    = CELL * 3
GRID_X       = (WIN_W - GRID_SIZE) // 2
GRID_Y       = 100
MARK_PAD     = 28
MARK_W       = 9
GRID_LINE_W  = 4


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


def cell_rect(index: int) -> pygame.Rect:
    row, col = divmod(index, 3)
    return pygame.Rect(GRID_X + col * CELL, GRID_Y + row * CELL, CELL, CELL)


def draw_x(surface: pygame.Surface, rect: pygame.Rect, color: tuple) -> None:
    p = MARK_PAD
    pygame.draw.line(surface, color, (rect.left + p, rect.top + p), (rect.right - p, rect.bottom - p), MARK_W)
    pygame.draw.line(surface, color, (rect.right - p, rect.top + p), (rect.left + p, rect.bottom - p), MARK_W)


def draw_o(surface: pygame.Surface, rect: pygame.Rect, color: tuple) -> None:
    radius = (CELL - 2 * MARK_PAD) // 2
    pygame.draw.circle(surface, color, rect.center, radius, MARK_W)


def draw_win_line(surface: pygame.Surface, line: tuple[int, int, int]) -> None:
    start = cell_rect(line[0]).center
    end   = cell_rect(line[2]).center
    pygame.draw.line(surface, C_WIN_LINE, start, end, 7)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("3-i-rad")
        self.clock = pygame.time.Clock()

        self.font_title  = pygame.font.SysFont("helvetica", 34, bold=True)
        self.font_status = pygame.font.SysFont("helvetica", 22)
        self.font_btn    = pygame.font.SysFont("helvetica", 18, bold=True)

        self.btn_rect = pygame.Rect(WIN_W // 2 - 85, WIN_H - 68, 170, 46)
        self._new_game()

    def _new_game(self) -> None:
        self.board        = create_board()
        self.current_player = "X"
        self.game_over    = False
        self.winner: str | None = None
        self.winning_line: tuple[int, int, int] | None = None

    def run(self) -> None:
        while True:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            self._draw(mouse)
            pygame.display.flip()
            self.clock.tick(60)

    def _handle_click(self, pos: tuple[int, int]) -> None:
        if self.btn_rect.collidepoint(pos):
            self._new_game()
            return
        if self.game_over:
            return
        for i in range(9):
            if cell_rect(i).collidepoint(pos) and self.board[i] == EMPTY:
                self.board[i] = self.current_player
                winner, line = check_winner(self.board)
                if winner:
                    self.winner, self.winning_line, self.game_over = winner, line, True
                elif is_board_full(self.board):
                    self.game_over = True
                else:
                    self.current_player = "O" if self.current_player == "X" else "X"
                break

    def _draw(self, mouse: tuple[int, int]) -> None:
        self.screen.fill(C_BG)
        self._draw_title()
        self._draw_grid(mouse)
        self._draw_marks()
        if self.winning_line:
            draw_win_line(self.screen, self.winning_line)
        self._draw_status()
        self._draw_button(mouse)

    def _draw_title(self) -> None:
        surf = self.font_title.render("3-i-rad", True, C_TEXT)
        self.screen.blit(surf, (WIN_W // 2 - surf.get_width() // 2, 32))

    def _draw_grid(self, mouse: tuple[int, int]) -> None:
        if not self.game_over:
            for i in range(9):
                r = cell_rect(i)
                if r.collidepoint(mouse) and self.board[i] == EMPTY:
                    pygame.draw.rect(self.screen, C_CELL_HOVER, r)

        for k in range(1, 3):
            x = GRID_X + k * CELL
            pygame.draw.line(self.screen, C_GRID, (x, GRID_Y), (x, GRID_Y + GRID_SIZE), GRID_LINE_W)
            y = GRID_Y + k * CELL
            pygame.draw.line(self.screen, C_GRID, (GRID_X, y), (GRID_X + GRID_SIZE, y), GRID_LINE_W)

    def _draw_marks(self) -> None:
        for i, mark in enumerate(self.board):
            if mark == EMPTY:
                continue
            r = cell_rect(i)
            if mark == "X":
                draw_x(self.screen, r, C_X)
            else:
                draw_o(self.screen, r, C_O)

    def _draw_status(self) -> None:
        grid_bottom = GRID_Y + GRID_SIZE
        if self.winner:
            color = C_X if self.winner == "X" else C_O
            text  = f"Spelare {self.winner} vinner!"
        elif self.game_over:
            color, text = C_SUBTEXT, "Oavgjort!"
        else:
            color = C_X if self.current_player == "X" else C_O
            text  = f"Spelare {self.current_player}:s tur"

        surf = self.font_status.render(text, True, color)
        self.screen.blit(surf, (WIN_W // 2 - surf.get_width() // 2, grid_bottom + 18))

    def _draw_button(self, mouse: tuple[int, int]) -> None:
        color = C_BTN_HOVER if self.btn_rect.collidepoint(mouse) else C_BTN
        pygame.draw.rect(self.screen, color, self.btn_rect, border_radius=10)
        surf = self.font_btn.render("Nytt spel", True, C_TEXT)
        self.screen.blit(surf, (
            self.btn_rect.centerx - surf.get_width() // 2,
            self.btn_rect.centery - surf.get_height() // 2,
        ))


if __name__ == "__main__":
    Game().run()
