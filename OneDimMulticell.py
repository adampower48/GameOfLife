from copy import copy
from random import choice, random, choices

from Enums import Rules1D, Neighbourhoods1D
from Main import my_hash

DEFAULT_WIDTH = 100
START_FILE = "start_multi.txt"


class Cell:
    # Base class for cell
    def __init__(self, **kwargs):
        self.display_chr = chr(1)
        self.debug_chr = "1"
        self.neighbourhood = Neighbourhoods1D.DEFAULT
        self.rules = Rules1D.DEFAULT
        self.alive = False

        for k, v in kwargs.items():
            setattr(self, k, v)

    def type_of(self):
        return self.neighbourhood, self.rules

    def __eq__(self, other):
        return self.neighbourhood == other.neighbourhood and self.rules == other.rules and self.alive == other.alive

    def __hash__(self):
        return hash((self.debug_chr, self.alive))


class CellFar2(Cell):
    def __init__(self):
        super().__init__()
        self.display_chr = chr(1132)
        self.debug_chr = "2"
        self.neighbourhood = (-2, 2)


class CellFar3(Cell):
    def __init__(self):
        super().__init__()
        self.display_chr = chr(1421)
        self.debug_chr = "3"
        self.neighbourhood = (-3, 3)


class CellLeft(Cell):
    def __init__(self):
        super().__init__()
        self.display_chr = "X"
        self.debug_chr = "4"
        self.neighbourhood = (-3, -2, -1)
        self.rules = {
            0: -1,
            1: 0,
            2: 1,
            3: -1
        }


class CellAbacus(Cell):
    def __init__(self):
        super().__init__()
        self.display_chr = "O"
        self.debug_chr = "5"
        self.neighbourhood = Neighbourhoods1D.ABACUS
        self.rules = Rules1D.ABACUS


possible_types = (Cell, CellFar2, CellFar3, CellLeft, CellAbacus)
possible_types_inst = tuple(map(lambda c: c(), possible_types))
possible_weights = (1, 0, 0, 0, 0)


def read_start_state(filename=START_FILE):
    state = []

    with open(filename) as f:
        line = f.readline()[:-1]

        for c in line:
            if c == "-":
                state.append(Cell())
            else:
                for cell_type in possible_types_inst:
                    if cell_type.debug_chr == c:
                        state.append(type(cell_type)())
                        state[-1].alive = True

        return state


def gen_random_state(width=DEFAULT_WIDTH, density=0.5):
    # Generates single state with randomised cells
    state = [c() for c in choices(possible_types, weights=possible_weights, k=width)]
    for c in state:
        c.alive = random() < density

    return state


def print_state(state, debug=False):
    if debug:
        print(*[c.debug_chr if c.alive else "-" for c in state], sep="")
    else:
        print(*[c.display_chr if c.alive else " " for c in state], sep="")


def calc_survive(state, i):
    # Calculates future state of 1 cell

    neighbourhood = state[i].neighbourhood
    rules = state[i].rules

    num_living = 0
    neighbour_counts = {type(state[i]): 0}

    # Counting
    for offset in neighbourhood:
        adj = (i + offset) % len(state)

        if state[adj].alive:
            num_living += 1

            # Neighbour types
            if type(state[adj]) in neighbour_counts:
                neighbour_counts[type(state[adj])] += 1
            else:
                neighbour_counts[type(state[adj])] = 1

    # Class of new cell, weighted per number of cells
    max_count = max(neighbour_counts.values())
    max_type = choice([t for t in neighbour_counts if neighbour_counts[t] == max_count])

    # Class of new cell, no weights
    # max_type = choice(tuple(neighbour_counts.keys()))

    return rules[num_living], max_type


def advance(state):
    # Calculates next future state
    changes = 0
    new_state = [copy(c) for c in state]

    for i in range(len(state)):
        survive, new_type = calc_survive(state, i)

        # Sets cell type/aliveness
        if survive == -1:
            new_state[i].alive = False
        elif survive == 1:
            new_state[i] = new_type()
            new_state[i].alive = True
        elif survive == 0:
            new_state[i] = new_type()
            new_state[i].alive = state[i].alive

        if new_state[i] != state[i]:
            changes += 1

    return new_state, changes


def run_complete(state):
    # Generates future states until repeated state is found

    state_hashes = {my_hash(state): True}
    print_state(state)

    steps = 0
    total_changes = 0

    while True:
        state, changes = advance(state)
        state_hash = my_hash(state)
        if state_hash in state_hashes:
            break
            # pass
        else:
            state_hashes[state_hash] = True

        steps += 1
        total_changes += changes
        print_state(state)

    print("Steps: {}, Changes: {}".format(steps, total_changes))

    return state


if __name__ == '__main__':
    # state = gen_random_state()
    state = read_start_state()
    state = run_complete(state)
