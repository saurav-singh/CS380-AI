import math
import random
import sys
import time


CONNECT = 3
COLS = 4
ROWS = 3
EMPTY = ' '
TIE = 'TIE'
PLAYER1 = 'X'
PLAYER2 = 'O'


class Connect3Board:

    def __init__(self, string=None):
        if string is not None:
            self.b = [list(line) for line in string.split('|')]
        else:
            self.b = [list(EMPTY * ROWS) for i in range(COLS)]

    def compact_string(self):
        return '|'.join([''.join(row) for row in self.b])

    def clone(self):
        return Connect3Board(self.compact_string())

    def get(self, i, j):
        return self.b[i][j] if i >= 0 and i < COLS and j >= 0 and j < ROWS else None

    def row(self, j):
        return [self.get(i, j) for i in range(COLS)]

    def put(self, i, j, val):
        self.b[i][j] = val
        return self

    def empties(self):
        return self.compact_string().count(EMPTY)

    def first_empty(self, i):
        j = ROWS - 1
        if self.get(i, j) != EMPTY:
            return None
        while j >= 0 and self.get(i, j) == EMPTY:
            j -= 1
        return j+1

    def place(self, i, label):
        j = self.first_empty(i)
        if j is not None:
            self.put(i, j, label)
        return self

    def equals(self, board):
        return self.compact_string() == board.compact_string()

    def next(self, label):
        boards = []
        for i in range(COLS):
            j = self.first_empty(i)
            if j is not None:
                board = self.clone()
                board.put(i, j, label)
                boards.append(board)
        return boards

    def _winner_test(self, label, i, j, di, dj):
        for _ in range(CONNECT-1):
            i += di
            j += dj
            if self.get(i, j) != label:
                return False
        return True

    def winner(self):
        for i in range(COLS):
            for j in range(ROWS):
                label = self.get(i, j)
                if label != EMPTY:
                    if self._winner_test(label, i, j, +1, 0) \
                            or self._winner_test(label, i, j, 0, +1) \
                            or self._winner_test(label, i, j, +1, +1) \
                            or self._winner_test(label, i, j, -1, +1):
                        return label
        return TIE if self.empties() == 0 else None

    def __str__(self):
        return stringify_boards([self])


def stringify_boards(boards):
    if len(boards) > 6:
        return stringify_boards(boards[0:6]) + '\n' + stringify_boards(boards[6:])
    else:
        s = ' '.join([' ' + ('-' * COLS) + ' '] * len(boards)) + '\n'
        for j in range(ROWS):
            rows = []
            for board in boards:
                rows.append('|' + ''.join(board.row(ROWS-1-j)) + '|')
            s += ' '.join(rows) + '\n'
        s += ' '.join([' ' + ('-' * COLS) + ' '] * len(boards))
        return s

# -----------------------------------------------------------------------------------
# AI Players Implementation
# -----------------------------------------------------------------------------------

# Player Class
class Player:
    def __init__(self, label):
        self.label = label

# Random Player
class RandomPlayer(Player):
    def __init__(self, label):
        super().__init__(label)

    def play(self, board):
        moves = board.next(self.label)
        pick = random.randint(0, len(moves)-1)
        return moves[pick]

# Minimax player
class MinimaxPlayer(Player):
    def __init__(self, label):
        super().__init__(label)
        # Define Opponent
        self.opponent = PLAYER1
        if self.label == PLAYER1:
            self.opponent = PLAYER2
        # Tree depth reducer
        self.reducer = 0.7

    def maximize(self,board):
        # Check end state
        endState = board.winner()
        if self.terminal_test(endState):
            return None, self.utility(endState) * self.reducer

        # Create possible actions to maximize
        move, value = None, -99999
        actions = board.next(self.label)

        # Compute minimax for each action
        for action in actions:
            _, checkValue = self.minimize(action)
            if checkValue > value:
                move, value = action, checkValue * self.reducer

        return move, value

    def minimize(self, board):
        # Check end state
        endState = board.winner()
        if self.terminal_test(endState):
            return None, self.utility(endState) * self.reducer

        # Create possible actions to minimize
        move, value = None, 99999
        actions = board.next(self.opponent)
        
        # Compute minimax for each action
        for action in actions:
            _, checkValue = self.maximize(action)
            if checkValue < value:
                move, value = action, checkValue * self.reducer

        return move, value

    def terminal_test(self, endState):
        if endState != None:
            return True
        return False

    def utility(self, endState):
        if endState == self.label:
            return 1000
        elif endState == TIE:
            return 1
        else:
            return -1000

    def play(self, board):
        move, _ = self.maximize(board)
        return move

#Alpha Beta Player
class MinimaxAlphaBetaPlayer(MinimaxPlayer):
    def __init__(self, label):
        super().__init__(label)
    
    def maximize(self,board, alpha, beta):
        # Check end state
        endState = board.winner()
        if self.terminal_test(endState):
            return None, self.utility(endState) * self.reducer

        # Create possible actions to maximize
        move, value = None, -99999
        actions = board.next(self.label)

        # Compute minimax for each action
        for action in actions:
            _, checkValue = self.minimize(action, alpha, beta)
            if checkValue > value:
                move, value = action, checkValue * self.reducer
                alpha = max(alpha, value)
            # Break for beta
            if beta <= alpha:
                break

        return move, value
    
    def minimize(self, board, alpha, beta):
        # Check end state
        endState = board.winner()
        if self.terminal_test(endState):
            return None, self.utility(endState) * self.reducer

        # Create possible actions to minimize
        move, value = None, 99999
        actions = board.next(self.opponent)
        
        # Compute minimax for each action
        for action in actions:
            _, checkValue = self.maximize(action, alpha, beta)
            if checkValue < value:
                move, value = action, checkValue * self.reducer
                beta = min(beta, value)
            # Break for alpha
            if beta <= alpha:
                break

        return move, value
    
    def play(self, board):
        move, _ = self.maximize(board,-99999, 99999)
        return move  


# Game AI Class
class GameAI:
    def __init__(self, board, mode):
        self.board = board
        self.player1 = None
        self.player2 = None
        self.timer = False
        self.AIname = ""
        if mode == 'random':
            self.player1 = RandomPlayer(PLAYER1)
            self.player2 = RandomPlayer(PLAYER2)
        if mode == 'minimax':
            self.player1 = RandomPlayer(PLAYER1)
            self.player2 = MinimaxPlayer(PLAYER2)
            self.timer = True
            self.AIname = "Minimax Player"
        if mode == 'alphabeta':
            self.player1 = RandomPlayer(PLAYER1)
            self.player2 = MinimaxAlphaBetaPlayer(PLAYER2)
            self.timer = True
            self.AIname = "AlphaBeta Player"
    
    # Gameplay simulation
    def gameplay(self):
        gamePlay = [self.board]
        winner = None
        timer = []

        # Game simulation
        while True:

            # Playe 1 makes a move
            self.board = self.player1.play(self.board)
            if self.board.winner() != None:
                break
            gamePlay.append(self.board)

            # Player 2 makes a move
            if self.timer:
                start = time.time()

            self.board = self.player2.play(self.board)

            if self.timer:
                end = time.time()
                timer.append(round(end-start, 3))     

            if self.board.winner() != None:
                break
            gamePlay.append(self.board)

        # Game end result
        gamePlay.append(self.board)
        winner = self.board.winner()
        if winner != TIE:
            winner += " wins!"

        # Display result
        print(stringify_boards(gamePlay))
        print("Result =", winner)
        if self.timer:
            print("Time by",self.AIname,"in seconds:")
            for _time in timer:
                print(str(_time) + "secs", end=" | ")
        print("\n")

# Main function
if __name__ == "__main__":        

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        board = Connect3Board(sys.argv[2] if len(sys.argv) > 2 else None)

        if cmd == 'print':
            print(board)

        if cmd == 'next':
            boards = board.next('o')
            print(stringify_boards(boards))

        if cmd == 'random':
            gameAI = GameAI(board, "random")
            gameAI.gameplay()

        if cmd == 'minimax':
            gameAI = GameAI(board, "minimax")
            gameAI.gameplay()

        if cmd == 'alphabeta':
            gameAI =  GameAI(board, "alphabeta")
            gameAI.gameplay()
    