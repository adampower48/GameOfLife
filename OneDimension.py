from Main import my_hash

START_FILE = "start_1d.txt"

DEFAULT_NEIGHBOURHOOD = (
    -1, 1
)

DEFAULT_RULES = {
    0: -1,
    1: 1,
    2: -1,
}

LEFT_NEIGHOURHOOD = {
    -2, -1
}


def print_state(state):
    print(*["X" if c else "-" for c in state], sep="")


def read_start_state(filename=START_FILE):
    with open(filename) as f:
        line = f.readline()[:-1]
        return [0 if c == "-" else 1 for c in line]


def calc_survive(state, i, mutation_prob=0, rules=DEFAULT_RULES, neighbourhood=DEFAULT_NEIGHBOURHOOD):
    num_living = 0

    # Counting
    for offset in neighbourhood:
        adj = (i + offset) % len(state)
        num_living += state[adj]

    # TODO: Random stuff

    return rules[num_living]


def advance(state):
    changes = 0
    new_state = state[:]

    for i in range(len(state)):
        survive = calc_survive(state, i)

        if survive == -1:
            new_state[i] = 0
        elif survive == 1:
            new_state[i] = 1

        if new_state[i] != state[i]:
            changes += 1

    return new_state, changes


def run_complete(state):
    state_hashes = {my_hash(state): True}
    print_state(state)

    steps = 0
    total_changes = 0

    while True:
        state, changes = advance(state)
        state_hash = my_hash(state)
        if state_hash in state_hashes:
            break
        else:
            state_hashes[state_hash] = True

        steps += 1
        total_changes += changes
        print_state(state)

    print("Steps: {}, Changes: {}".format(steps, total_changes))

    return state


if __name__ == '__main__':
    s = read_start_state()
    run_complete(s)
