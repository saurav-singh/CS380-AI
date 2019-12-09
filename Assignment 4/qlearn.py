import random
import sys


DEFAULT_STATE = '       | ###  -| # #  +| # ####|       '


class Action:

    def __init__(self, name, dx, dy):
        self.name = name
        self.dx = dx
        self.dy = dy


ACTIONS = [
    Action('UP', 0, -1),
    Action('RIGHT', +1, 0),
    Action('DOWN', 0, +1),
    Action('LEFT', -1, 0)
]


class State:

    def __init__(self, env, x, y):
        self.env = env
        self.x = x
        self.y = y

    def clone(self):
        return State(self.env, self.x, self.y)

    def is_legal(self, action):
        cell = self.env.get(self.x + action.dx, self.y + action.dy)
        return cell is not None and cell in ' +-'

    def legal_actions(self, actions):
        legal = []
        for action in actions:
            if self.is_legal(action):
                legal.append(action)
        return legal

    def reward(self):
        cell = self.env.get(self.x, self.y)
        if cell is None:
            return None
        elif cell == '+':
            return +10
        elif cell == '-':
            return -10
        else:
            return 0

    def at_end(self):
        return self.reward() != 0

    def execute(self, action):
        self.x += action.dx
        self.y += action.dy
        return self

    def __str__(self):
        tmp = self.env.get(self.x, self.y)
        self.env.put(self.x, self.y, 'A')
        s = ' ' + ('-' * self.env.x_size) + '\n'
        for y in range(self.env.y_size):
            s += '|' + ''.join(self.env.row(y)) + '|\n'
        s += ' ' + ('-' * self.env.x_size)
        self.env.put(self.x, self.y, tmp)
        return s


class Env:

    def __init__(self, string):
        self.grid = [list(line) for line in string.split('|')]
        self.x_size = len(self.grid[0])
        self.y_size = len(self.grid)

    def get(self, x, y):
        if x >= 0 and x < self.x_size and y >= 0 and y < self.y_size:
            return self.grid[y][x]
        else:
            return None

    def put(self, x, y, val):
        if x >= 0 and x < self.x_size and y >= 0 and y < self.y_size:
            self.grid[y][x] = val

    def row(self, y):
        return self.grid[y]

    def random_state(self):
        x = random.randrange(0, self.x_size)
        y = random.randrange(0, self.y_size)
        while self.get(x, y) != ' ':
            x = random.randrange(0, self.x_size)
            y = random.randrange(0, self.y_size)
        return State(self, x, y)


class QTable:

    def __init__(self, env, actions):
        self.env = env
        self.actions = actions
        self.actionMap = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}
        self.Qtable = [[[0] * len(actions) for _ in range(env.x_size)]
                       for _ in range(env.y_size)]

    def get_q(self, state, action):
        return self.Qtable[state.y][state.x][action]

    def get_q_row(self, state):
        return self.Qtable[state.y][state.x]

    def set_q(self, state, action, val):
        self.Qtable[state.y][state.x][action] = val

    def learn_episode(self, alpha=.10, gamma=.90):
        state = self.env.random_state()
        print(state)

        while not state.at_end():
            # Simulate
            possibleActions = state.legal_actions(self.actions)
            action = possibleActions[random.randint(0, len(possibleActions)-1)]
            preState = state.clone()
            state = state.execute(action)
            reward = state.reward()
            # Calculate Q-value
            _action = self.actionMap[action.name]
            eqnLeft = (1-alpha) * self.get_q(preState, _action)
            eqnRight = alpha * (reward + gamma * max(self.get_q_row(state)))
            Qvalue = eqnLeft + eqnRight
            # Update Q-table
            self.set_q(preState, _action, Qvalue)
            print(state)

    def learn(self, episodes, alpha=.10, gamma=.90):
        for _ in range(episodes):
            self.learn_episode(alpha, gamma)

    def __str__(self):
        _str = "\n"
        for action in self.actionMap:
            z = self.actionMap[action]
            _str += action + "\n"
            for y in range(self.env.y_size):
                for x in range(self.env.x_size):
                    Qvalue = self.Qtable[y][x][z]
                    _str += "----" if Qvalue is 0 else "{0:.2f}".format(Qvalue)
                    _str += "\t"
                _str += "\n"
            _str += "\n"

        return _str


if __name__ == "__main__":

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        env = Env(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STATE)

        if cmd == 'learn':
            qt = QTable(env, ACTIONS)
            qt.learn(100)
            print(qt)
