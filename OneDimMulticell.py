from copy import copy
from random import choice, random, choices

import Enums
from Enums import Rules1D, Neighbourhoods1D, Rulesets
from Helpers import my_hash

DEFAULT_WIDTH = 75
CSV_CHUNK_SIZE = 25
START_FILE = "start_multi.txt"
CSV_FILE = "out_multi.txt"

# Cell attributes
CELL_TYPES = {
    # (display_chr, debug_chr, neighbourhood, rules)
    "Default": (chr(1), "1", Neighbourhoods1D.DEFAULT, Rules1D.DEFAULT),
    "Far2": (chr(1132), "2", (-2, 2), Rules1D.DEFAULT),
    "Far3": (chr(1421), "3", (-3, 3), Rules1D.DEFAULT),
    "Left3": ("X", "4", (-3, -2, -1), {0: -1, 1: 0, 2: 1, 3: -1}),
    "Abacus": ("O", "5", Neighbourhoods1D.ABACUS, Rules1D.ABACUS),
    "Class4A": ("A", "6", Neighbourhoods1D.CLASS_4A, Rules1D.CLASS_4A),
    "DatePalm": ("P", "7", Neighbourhoods1D.DATE_PALM, Rules1D.DATE_PALM),
    "Roots": ("R", "8", *Enums.from_ruleset(Rulesets.ROOTS))
}


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

        self.type = hash((self.neighbourhood, tuple(self.rules.items())))

    def __eq__(self, other):
        return self.neighbourhood == other.neighbourhood and self.rules == other.rules and self.alive == other.alive

    def __hash__(self):
        return hash((self.debug_chr, self.alive))


def build_cell(attr_tuple):
    # Builds constructor of Cell given its attributes
    return lambda: Cell(display_chr=attr_tuple[0],
                        debug_chr=attr_tuple[1],
                        neighbourhood=attr_tuple[2],
                        rules=attr_tuple[3])


# Constructors for Cell types
possible_types = tuple(build_cell(CELL_TYPES[t]) for t in CELL_TYPES)
possible_types_inst = tuple(map(lambda c: c(), possible_types))
possible_weights = (1, 1, 1, 1, 1, 1, 1, 1)


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


def write_to_csv(states, clear=False):
    with open(CSV_FILE, "w" if clear else "a") as f:
        f.writelines([",".join([c.debug_chr if c.alive else "-" for c in state]) + "\n" for state in states])


def calc_survive(state, i):
    # Calculates future state of 1 cell

    neighbourhood = state[i].neighbourhood
    rules = state[i].rules

    num_living = 0
    neighbour_counts = {state[i].type: 0}

    # Counting
    len_state = len(state)
    for offset in neighbourhood:
        adj = (i + offset) % len_state

        if state[adj].alive:
            num_living += 1

            # Neighbour types
            cell_type = state[adj].type
            if cell_type in neighbour_counts:
                neighbour_counts[cell_type] += 1
            else:
                neighbour_counts[cell_type] = 1

    # Class of new cell, highest number priority
    max_count = max(neighbour_counts.values())
    max_type = choice([t for t in neighbour_counts if neighbour_counts[t] == max_count])
    max_type = next(c for i, c in enumerate(possible_types) if possible_types_inst[i].type == max_type)

    # Class of new cell, no weights
    # max_type = choice(tuple(neighbour_counts.keys()))

    return rules[num_living], max_type


def calc_survive2(state, i):
    # Calculates future state of 1 cell
    # This was an attempted optimisation of calc_survive
    # Results:
    #   calc_survive : 124000 cells per second
    #   calc_survive2:  73000 cells per second
    # Listed optimisations can be found here:
    # https://pastebin.com/tXiKVEfX

    neighbourhood = state[i].neighbourhood
    rules = state[i].rules

    num_living = 0
    neighbour_counts = {c.type: 0 for c in possible_types_inst}

    # Counting
    for adj_cell in map(lambda offset: state[(i + offset) % DEFAULT_WIDTH], neighbourhood):
        num_living += adj_cell.alive
        neighbour_counts[adj_cell.type] += adj_cell.alive

    # Class of new cell, highest number priority
    max_count = max(neighbour_counts.values())
    max_type = choice([t for t in neighbour_counts if neighbour_counts[t] == max_count])
    max_type = next(c for i, c in enumerate(possible_types) if possible_types_inst[i].type == max_type)

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
    print_state(state, True)
    write_to_csv([state], True)

    steps = 0
    total_changes = 0

    state_buffer = []
    while True:
        state, changes = advance(state)
        state_buffer.append(state)

        state_hash = my_hash(state)
        if state_hash in state_hashes:
            write_to_csv(state_buffer)
            break
        else:
            state_hashes[state_hash] = True

        steps += 1
        total_changes += changes

        print_state(state, True)
        if steps % CSV_CHUNK_SIZE == 0:
            write_to_csv(state_buffer)
            state_buffer = []

    print("Steps: {}, Changes: {}".format(steps, total_changes))

    return state


def prof():
    # Profile entire program
    import cProfile

    s = gen_random_state(7500)

    pr = cProfile.Profile()
    pr.enable()
    advance(s)
    pr.disable()
    pr.print_stats(sort="tottime")


if __name__ == '__main__':
    state = gen_random_state()
    # state = read_start_state()
    state = run_complete(state)

    # prof()
