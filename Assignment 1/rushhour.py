import sys
import copy


class Board:
    def __init__(self, board_state, cars=[]):
        self.board_state = []
        self.cars = cars

        if (isinstance(board_state, str)):
            self.parse_state(board_state)

        if (isinstance(board_state, list)):
            self.board_state = board_state.copy()

    def parse_state(self, board_state):
        board_state = board_state.split('|')
        for i in range(6):
            self.board_state.append(list(board_state[i]))
            for c in list(board_state[i]):
                self.cars.append(c)
        self.cars = list(set(self.cars))
        self.cars.remove(" ")

    def done(self):
        if (self.board_state[2][4] + self.board_state[2][5] == "xx"):
            return True
        return False

    def car_position(self, car):
        position = []
        for i in range(len(self.board_state)):
            for j in range(len(self.board_state[i])):
                if self.board_state[i][j] == car:
                    position.append((i, j))
        return position

    def move_horizontal(self, car):
        position = self.car_position(car)
        car_head = position[0]
        for pos in position:
            if (pos[0] != car_head[0]):
                return False
        return True

    def possible_moves(self, pos, horizontal):
        possible_moves = []

        if (horizontal):
            direction = pos[0][0]
            car_head = max(pos)[1] + 1
            car_tail = min(pos)[1] - 1

            while (car_tail > -1) and (self.board_state[direction][car_tail] == " "):
                possible_moves.append((direction, car_tail))
                car_tail -= 1

            while (car_head < 6) and (self.board_state[direction][car_head] == " "):
                possible_moves.append((direction, car_head))
                car_head += 1

        else:
            direction = pos[0][1]
            car_head = max(pos)[0] + 1
            car_tail = min(pos)[0] - 1

            while (car_tail > -1) and (self.board_state[car_tail][direction] == " "):
                possible_moves.append((car_tail, direction))
                car_tail -= 1

            while (car_head < 6) and (self.board_state[car_head][direction] == " "):
                possible_moves.append((car_head, direction))
                car_head += 1

        return possible_moves

    def next_for_car(self, car):
        next_moves = []
        pos = self.car_position(car)
        hr = self.move_horizontal(car)
        moves = self.possible_moves(pos, hr)

        for move in moves:
            B = self.clone()
            B.move(car, move)
            next_moves.append(B)

        return next_moves

    def next(self):
        possible_boards = []
        for car in self.cars:
            next_moves = self.next_for_car(car)
            for next_move in next_moves:
                possible_boards.append(next_move)
        if (len(possible_boards) > 0):
            self.print(possible_boards)

    def distance(self, p1, p2):
        P = (p2[0] - p1[0], p2[1] - p1[1])
        P = (P[0]) + (P[1])
        return P

    def move(self, car, move_to):
        new_pos = []
        current_pos = self.car_position(car)
        move_horizontal = self.move_horizontal(car)

        car_head = max(current_pos)
        car_tail = min(current_pos)

        L = self.distance(car_head, move_to)
        U = self.distance(car_tail, move_to)

        move_distance = U if (abs(U) < abs(L)) else L

        if (move_horizontal):
            for p in current_pos:
                new_pos.append((p[0], p[1]+move_distance))
                self.board_state[p[0]][p[1]] = " "
        else:
            for p in current_pos:
                new_pos.append((p[0] + move_distance, p[1]))
                self.board_state[p[0]][p[1]] = " "

        for p in new_pos:
            self.board_state[p[0]][p[1]] = car

    def clone(self):
        state = copy.deepcopy(self.board_state)
        clone = Board(state, self.cars)
        return clone

    def print(self, boards=[]):
        # SETUP
        if len(boards) == 0:
            boards.append(self)
        width = len(boards)
        height = 6
        # PRINT
        print(" ------ " * width)
        for i in range(height):
            for board in boards:
                bar = " " if (i == 2) else "|"
                print("|"+"".join(board.board_state[i]), end=bar)
            print("")
        print(" ------ " * width)


# -------------------------------------------
# Main Function
# -------------------------------------------
if __name__ == "__main__":

    arguments_length = len(sys.argv)

    if(arguments_length < 2):
        print("\nInvalid Command.\nPlease enter atleast 1 argument.\n")
        sys.exit()

    if(arguments_length > 2):
        board_state = sys.argv[2]
    else:
        board_state = "  o aa|  o   |xxo   |ppp  q|     q|     q"

    command = sys.argv[1]
    board = Board(board_state)

    if (command == "print"):
        board.print()

    elif (command == "done"):
        print(board.done())

    elif (command == "next"):
        board.next()

    else:
        print("\nInvalid command.")
        print("Valid commands: print | done | next\n")
