import random

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class DataSource(BaseModel):
    board: list[list[int]]
    type: int


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


def is_first_turn(board: list[list[int]]):
    if board == [[0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 0]]:
        return True
    return False


def is_moves_left(board: list[list[int]]):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return True
    return False


def evaluate(board: list[list[int]], player: int, opponent: int):
    # Checking for rows if player or opponent is the winner
    for row in range(3):
        if board[row][0] == board[row][1] and board[row][1] == board[row][2]:
            if board[row][0] == player:
                return 1
            elif board[row][0] == opponent:
                return -1

    # Checking for columns if player or opponent is the winner
    for col in range(3):

        if board[0][col] == board[1][col] and board[1][col] == board[2][col]:

            if board[0][col] == player:
                return 1
            elif board[0][col] == opponent:
                return -1

    # Checking for diagonals if player or opponent is the winner
    if board[0][0] == board[1][1] and board[1][1] == board[2][2]:

        if board[0][0] == player:
            return 1
        elif board[0][0] == opponent:
            return -1

    if board[0][2] == board[1][1] and board[1][1] == board[2][0]:

        if board[0][2] == player:
            return 1
        elif board[0][2] == opponent:
            return -1

    # If none of them have won the match then return 0
    return 0


def minimax(board: list[list[int]], depth, is_max: bool, player: int, opponent: int):
    score = evaluate(board, player, opponent)

    # If maximizer has won return evaluated score
    if score == 1:
        return score

    # If minimizer has won return evaluated score
    if score == -1:
        return score

    # If there are no moves left and no winner
    # It is a draw
    if not is_moves_left(board):
        return 0

    # If maximizer moves
    if is_max:
        optimal = -100

        # Traverse all cells
        for i in range(3):
            for j in range(3):

                # Check if cell is empty
                if board[i][j] == 0:
                    # Move
                    board[i][j] = player

                    # Call minimax recursively and take max value
                    optimal = max(optimal, minimax(board, depth + 1, not is_max, player, opponent))

                    # Undo the move
                    board[i][j] = 0
        return optimal

    # If minimizer moves
    else:
        optimal = 100

        # Traverse all cells
        for i in range(3):
            for j in range(3):

                # Check if cell is empty
                if board[i][j] == 0:
                    # move
                    board[i][j] = opponent

                    # Call minimax recursively and take min value
                    optimal = min(optimal, minimax(board, depth + 1, not is_max, player, opponent))

                    # Undo the move
                    board[i][j] = 0
        return optimal


# This will return the optimal move for the player
def find_optimal_move(board: list[list[int]], player: int, opponent: int):
    if is_first_turn(board):
        return Point(random.randint(0, 2), random.randint(0, 2))

    optimal_val = -100
    optimal_move = None

    # Traverse all cells, find the optimal
    for i in range(3):
        for j in range(3):

            # Check if cell is empty
            if board[i][j] == 0:

                # Move
                board[i][j] = player

                # Evaluate this move
                move_val = minimax(board, 0, False, player, opponent)

                # Undo the move
                board[i][j] = 0

                # Update the best value
                if move_val > optimal_val:
                    optimal_move = Point(i, j)
                    optimal_val = move_val
                elif move_val == optimal_val and random.random() < .5:
                    optimal_move = Point(i, j)
                    optimal_val = move_val

    return optimal_move


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/nextTurn")
def next_turn(data_source: DataSource):
    board: list[list[int]] = data_source.board
    player = 1
    opponent = 2
    data_source_type = data_source.type
    if data_source_type == 2:
        player = 2
        opponent = 1

    return find_optimal_move(board, player, opponent)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
