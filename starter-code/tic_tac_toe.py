"""
3-i-rad — terminal-version

Två spelare turas om att placera X och O på ett 3x3-bräde.
Spelet avslutas när någon får tre i rad eller brädet är fullt.

Kör med: python tic_tac_toe.py
"""

EMPTY = " "

# De 8 vinstkombinationerna: 3 rader, 3 kolumner, 2 diagonaler
WINNING_LINES: list[tuple[int, int, int]] = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rader
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # kolumner
    (0, 4, 8), (2, 4, 6),             # diagonaler
]


def create_board() -> list[str]:
    """Skapar ett tomt bräde med 9 tomma rutor."""
    return [EMPTY] * 9


def print_board(board: list[str]) -> None:
    """Skriver ut brädet. Tomma rutor visas som siffran 1-9."""
    def cell(i: int) -> str:
        return board[i] if board[i] != EMPTY else str(i + 1)

    print()
    print(f" {cell(0)} | {cell(1)} | {cell(2)} ")
    print("---+---+---")
    print(f" {cell(3)} | {cell(4)} | {cell(5)} ")
    print("---+---+---")
    print(f" {cell(6)} | {cell(7)} | {cell(8)} ")
    print()


def check_winner(board: list[str]) -> str | None:
    """Returnerar 'X' eller 'O' om någon har vunnit, annars None."""
    for a, b, c in WINNING_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_board_full(board: list[str]) -> bool:
    """Returnerar True om brädet är fullt."""
    return EMPTY not in board


def get_player_move(board: list[str], player: str) -> int:
    """Frågar spelaren efter ett drag (1-9) och validerar."""
    while True:
        raw = input(f"Spelare {player}, välj ruta (1-9): ").strip()

        if not raw.isdigit():
            print("  Skriv en siffra mellan 1 och 9.")
            continue

        position = int(raw)
        if not 1 <= position <= 9:
            print("  Siffran måste vara mellan 1 och 9.")
            continue

        index = position - 1

        if board[index] != EMPTY:
            print("  Den rutan är redan tagen, välj en annan.")
            continue

        return index


def play_game() -> None:
    """Huvudloop för ett spel."""
    board = create_board()
    current_player = "X"

    print("Välkommen till 3-i-rad!")
    print("Skriv en siffra 1-9 för att placera ditt märke.")

    while True:
        print_board(board)

        index = get_player_move(board, current_player)
        board[index] = current_player

        winner = check_winner(board)
        if winner is not None:
            print_board(board)
            print(f"Spelare {winner} vinner!")
            return

        if is_board_full(board):
            print_board(board)
            print("Oavgjort!")
            return

        current_player = "O" if current_player == "X" else "X"


if __name__ == "__main__":
    play_game()