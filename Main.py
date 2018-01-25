# Implementation of
# https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

from numpy.random import rand, random

cell_width = 20
cell_height = 20
START_FILE = "start.txt"
DEFAULT_RULES = {
    0: -1,
    1: -1,
    2: 0,
    3: 1,
    4: -1,
    5: -1,
    6: -1,
    7: -1,
    8: -1,
    9: -1,
}

MOORES_NEIGHBOURHOOD = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)

VON_NEUMANN_NEIGHBOURHOOD = (
    (-2, 0),
    (-1, 0),
    (1, 0),
    (2, 0),
    (0, -2),
    (0, -1),
    (0, 1),
    (0, 2),
)


def my_hash(o):
    # Used to hash states to keep track of seen states
    try:
        return hash(o)
    except TypeError:
        if type(o) == list:
            return hash(tuple(my_hash(e) for e in o))


def print_grid(grid):
    for row in grid:
        # print(*row)
        print(*["X" if c else "-" for c in row])
    print()


def read_start_state(filename=START_FILE):
    # Reads seed state from given file
    # "-" represent dead cells, anything else represents live cells
    grid = []
    with open(START_FILE) as f:
        for line in f.readlines():
            row = [0 if c == "-" else 1 for c in line[:-1]]
            grid.append(row)

    return grid


def gen_random_state(density=0.5, height=cell_height, width=cell_width):
    # Generates random seed state
    grid: list = rand(height, width).tolist()

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            grid[i][j] = 1 if grid[i][j] < density else 0

    return grid


def calc_survive_toroidal(grid, i, j):
    # Check cell neighbours to get next cell state
    # Toroidal field
    # -1: Dead
    #  0: Same
    #  1: Live

    num_living = 0

    for yOff in range(-1, 2):
        for xOff in range(-1, 2):
            adj_i = (i + yOff) % len(grid)  # Wrapping at edges
            adj_j = (j + xOff) % len(grid[0])  #

            # Valid index & not middle cell
            if 0 <= adj_i < len(grid) and 0 <= adj_j < len(grid[0]) and not (adj_i == i and adj_j == j):
                num_living += grid[adj_i][adj_j]

    if num_living < 2 or num_living > 3:
        return -1
    if num_living == 3:
        return 1
    return 0


def calc_survive(grid, i, j, mutation_prob=0, rules=DEFAULT_RULES, neighbourhood=VON_NEUMANN_NEIGHBOURHOOD):
    # Check cell neighbours to get next cell state
    # Toroidal field
    # Mutation by adding/subtracting num of neighbours at random
    # Optional ruleset, neighbourhood
    # -1: Dead
    #  0: Same
    #  1: Live

    # Counting
    num_living = 0
    for offset in neighbourhood:
        adj_i = (i + offset[0]) % len(grid)  # Wrapping at edges
        adj_j = (j + offset[1]) % len(grid[0])  #

        # Valid index
        if 0 <= adj_i < len(grid) and 0 <= adj_j < len(grid[0]):
            num_living += grid[adj_i][adj_j]

    # Random stuff
    num_change = 0
    while random() < mutation_prob:
        num_change += 1

    if random() < 0.5:
        num_change *= -1

    num_living += num_change
    num_living = max(0, min(9, num_living))
    # End random stuff

    # Rules
    return rules[num_living]


def advance(grid):
    # Calculates next future state given current state
    # Creates full new array representing new state

    changes = 0
    new_grid = [g[:] for g in grid]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            # survive = calc_survive(grid, i, j)
            survive = calc_survive_toroidal(grid, i, j)

            if survive == -1:
                new_grid[i][j] = 0
            elif survive == 1:
                new_grid[i][j] = 1

            if new_grid[i][j] != grid[i][j]:
                changes += 1

    return new_grid, changes


def advance_buffer_toroidal(grid):
    # Calculates next future state given current state
    # In-place using 3 buffer arrays
    # Toroidal field
    survival_func = calc_survive

    changes = 0
    buffer_first = grid[0]

    buffer1 = []
    for j in range(len(grid[0])):
        survive = survival_func(grid, 0, j)
        if survive == 0:
            buffer1.append(grid[0][j])
        else:
            buffer1.append(1 if survive == 1 else 0)

            if buffer1[-1] != grid[0][j]:
                changes += 1

    for i in range(1, len(grid) - 1):
        buffer2 = []
        for j in range(len(grid[i])):
            survive = survival_func(grid, i, j)
            if survive == 0:
                buffer2.append(grid[i][j])
            else:
                buffer2.append(1 if survive == 1 else 0)

                if buffer2[-1] != grid[i][j]:
                    changes += 1

        grid[i - 1] = buffer1
        buffer1 = buffer2

    # Last line
    last_grid = [buffer_first, grid[-2], grid[-1]]
    buffer2 = []
    for j in range(len(grid[-1])):
        survive = survival_func(last_grid, 2, j)

        if survive == 0:
            buffer2.append(last_grid[2][j])
        else:
            buffer2.append(1 if survive == 1 else 0)

            if buffer2[-1] != last_grid[2][j]:
                changes += 1

    grid[-2] = buffer1
    grid[-1] = buffer2

    return grid, changes


def advance_buffer(grid):
    # Calculates next future state given current state
    # In-place using 2 buffer arrays
    changes = 0

    buffer1 = []
    for j in range(len(grid[0])):
        survive = calc_survive(grid, 0, j)
        if survive == 0:
            buffer1.append(grid[0][j])
        else:
            buffer1.append(1 if survive == 1 else 0)

            if buffer1[-1] != grid[0][j]:
                changes += 1

    for i in range(1, len(grid)):
        buffer2 = []
        for j in range(len(grid[i])):
            survive = calc_survive(grid, i, j)
            if survive == 0:
                buffer2.append(grid[i][j])
            else:
                buffer2.append(1 if survive == 1 else 0)

                if buffer2[-1] != grid[i][j]:
                    changes += 1

        grid[i - 1] = buffer1
        buffer1 = buffer2

    grid[-1] = buffer1

    return grid, changes


def advance_by(grid, n):
    # Advances by n generations
    changes = 0
    for _ in range(n):
        grid, c = advance(grid)
        changes += c

    return grid, changes


def run_complete(grid):
    states = {my_hash(grid): True}
    print_grid(grid)

    steps = 0
    total_changes = 0
    changes = 1

    while changes:
        grid, changes = advance_buffer_toroidal(grid)
        state = my_hash(grid)
        if state in states:
            break
        else:
            states[state] = True

        steps += 1
        total_changes += changes
        print_grid(grid)

    print("Steps: {}, Changes: {}".format(steps, total_changes))

    return grid


if __name__ == '__main__':
    # grid = read_start_state()
    grid = gen_random_state()
    grid = run_complete(grid)
