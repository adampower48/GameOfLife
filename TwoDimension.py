from Enums import Neighbourhoods2D, Rules2D


START_FILE = "start_2d.txt"


class Cell:
    # Base class for cell
    def __init__(self, **kwargs):
        self.display_chr = chr(1)
        self.debug_chr = "1"
        self.neighbourhood = Neighbourhoods2D.DEFAULT
        self.rules = Rules2D.DEFAULT
        self.alive = False

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.type = hash((self.neighbourhood, tuple(self.rules.items())))

    def __eq__(self, other):
        return self.neighbourhood == other.neighbourhood and self.rules == other.rules and self.alive == other.alive

    def __hash__(self):
        return hash((self.debug_chr, self.alive))


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