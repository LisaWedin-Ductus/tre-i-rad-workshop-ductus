# Three-in-a-Row (Tic-Tac-Toe)

## Goal

Build a **graphical, mouse-driven** three-in-a-row game. The game runs in a desktop window and replaces any prior terminal-based version — all interaction during play happens through the GUI using mouse clicks.

## Requirements

### Functional

1. **GUI gameplay**
   The game runs in a windowed GUI displaying a 3×3 board. Players make moves by clicking cells with the mouse. No terminal input is required during a game.

2. **Hot-seat two-player mode**
   Two human players play on the same computer, alternating turns as X and O. No AI opponent and no network play.

3. **Current turn indicator**
   The GUI clearly shows whose turn it is at all times (e.g., a status label such as "X's turn" or a highlighted player marker). The indicator updates immediately after every valid move.

4. **Winning line visualization**
   When a player wins, the three cells forming the winning line are visually highlighted (color, outline, or strike-through) so the result is unambiguous. The board is locked from further input until the game is restarted.

5. **Restart**
   A restart control (e.g., a "New Game" button) is always visible and resets the board to an empty state, clears any winning highlight, and resets the turn indicator to the starting player. Restart works both mid-game and after a game ends.

6. **End-of-game handling**
   The game detects and visibly communicates:
   - **Win** — winning line highlighted, status shows the winner.
   - **Draw** — board full with no winner, status shows draw.

### Non-functional

- Mouse-only interaction during gameplay; no keyboard input required to make a move.
- Clicks on already-occupied cells, or any clicks after a game has ended, must not change game state.
- Board state, turn indicator, and end-of-game status must always be consistent with each other (single source of truth for game state).

## Out of Scope

- AI / single-player mode
- Network or online multiplayer
- Persistent score tracking across sessions
- Custom board sizes (fixed at 3×3)

## Acceptance Criteria

- [ ] Two players can complete a full game using only the mouse.
- [ ] The current player is visible on screen at every point in the game.
- [ ] A win highlights the three winning cells and announces the winner.
- [ ] A draw is detected and announced when the board fills with no winner.
- [ ] "New Game" returns the application to a clean starting state from any game state.
- [ ] Clicking an occupied cell, or interacting after game end, has no effect on game state.