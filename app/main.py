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


def is_moves_left(board: list[list[int]]):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return True
    return False


def evaluate(board: list[list[int]], player: int, opponent: int):
    # Checking for rows if x or o is the winner
    for row in range(3):
        if board[row][0] == board[row][1] and board[row][1] == board[row][2]:
            if board[row][0] == player:
                return 1
            elif board[row][0] == opponent:
                return -1

    # Checking for columns if x or o is the winner
    for col in range(3):

        if board[0][col] == board[1][col] and board[1][col] == board[2][col]:

            if board[0][col] == player:
                return 1
            elif board[0][col] == opponent:
                return -1

    # Checking for diagonals if x or o is the winner
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

    # If none of them have won then return 0
    return 0


def minimax(board: list[list[int]], depth, is_max: bool, player: int, opponent: int):
    score = evaluate(board, player, opponent)

    # If Maximizer has won
    # return evaluated score
    if score == 1:
        return score

    # If Minimizer has won
    # return evaluated score
    if score == -1:
        return score

    # If there are no more moves and no winner then
    # It is a draw
    if not is_moves_left(board):
        return 0

    # If this maximizer's move
    if is_max:
        best = -9999

        # Traverse all cells
        for i in range(3):
            for j in range(3):

                # Check if cell is empty
                if board[i][j] == 0:
                    # Make the move
                    board[i][j] = player

                    # Call minimax recursively and choose
                    # the maximum value
                    best = max(best, minimax(board, depth + 1, not is_max, player, opponent))

                    # Undo the move
                    board[i][j] = 0
        return best

    # If this minimizer's move
    else:
        best = 9999

        # Traverse all cells
        for i in range(3):
            for j in range(3):

                # Check if cell is empty
                if board[i][j] == 0:
                    # Make the move
                    board[i][j] = opponent

                    # Call minimax recursively and choose
                    # the minimum value
                    best = min(best, minimax(board, depth + 1, not is_max, player, opponent))

                    # Undo the move
                    board[i][j] = 0
        return best


# This will return the best possible move for the player
def find_best_move(board: list[list[int]], player: int, opponent: int):
    best_val = -9999
    best_move = Point(-1, -1)

    # Traverse all cells, evaluate minimax function for
    # all empty cells. And return the cell with optimal
    # value
    for i in range(3):
        for j in range(3):

            # Check if cell is empty
            if board[i][j] == 0:

                # Make the move
                board[i][j] = player

                # compute evaluation function for this
                # move
                move_val = minimax(board, 0, False, player, opponent)

                # Undo the move
                board[i][j] = 0

                # If the value of the current move is
                # more than the best value, then update
                # best
                if move_val > best_val:
                    best_move = Point(i, j)
                    best_val = move_val

    return best_move


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

    return find_best_move(board, player, opponent)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
