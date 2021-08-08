from abc import ABC
from typing import List, Dict, Tuple

from boundary import WrapBoundaryHandler, ClipBoundaryHandler
from cell import Grid1D, Cell, Grid, Grid2D, Grid1DFactory


class Ruleset(ABC):
    def process_grid(self, grid: Grid) -> Grid:
        """Generates the next state for a grid of cells."""

    def process_cell(self, neighbourhood: List[Cell], old_cell: Cell) -> Cell:
        """Generates the next state for a single cell."""


class BoundaryModeFactory:
    @classmethod
    def get_boundary_handler(cls, name: str):
        if name == "wrap":
            return WrapBoundaryHandler()
        elif name == "clip":
            return ClipBoundaryHandler()
        else:
            raise ValueError(f"Unknown boundary handler: {name}")


class Mapping1DRuleset(Ruleset):
    def __init__(self, mappings: Dict[Tuple[bool], bool], offsets: List[int], boundary="wrap"):
        self.mappings = mappings
        self.offsets = offsets
        self.boundary_handler = BoundaryModeFactory.get_boundary_handler(boundary)

    def process_grid(self, grid: Grid1D) -> Grid1D:
        new_cells = []
        for cell_idx in range(len(grid)):
            # Collect neighbouring cells
            neighbourhood = [grid[self.boundary_handler.get_idx(cell_idx + o, len(grid))] for o in self.offsets]
            new_cells.append(self.process_cell(neighbourhood, grid[cell_idx]))

        return Grid1D(new_cells)

    def process_cell(self, neighbourhood: List[Cell], old_cell: Cell) -> Cell:
        key = tuple(c.state for c in neighbourhood)
        return Cell(self.mappings.get(key, False))

    def __repr__(self):
        return "\n".join([
            f"Neighbourhood: {self.offsets}",
            "True states:",
            *[f"{k}" for k in self.mappings.keys()]
        ])


class Mapping2DRuleset(Ruleset):
    def __init__(self, mappings: Dict[Tuple[Tuple[bool]], bool], offsets: List[List[Tuple[int, int]]], boundary="wrap"):
        self.mappings = mappings
        self.offsets = offsets
        self.boundary_handler = BoundaryModeFactory.get_boundary_handler(boundary)

    def process_grid(self, grid: Grid2D) -> Grid2D:
        new_cells = [[] for _ in range(grid.height)]

        for i in range(grid.height):
            for j in range(grid.width):

                # Collect neighbourhood of cells
                neighbourhood = [[] for _ in range(len(self.offsets))]
                for off_i in range(len(self.offsets)):
                    for off_j in range(len(self.offsets[off_i])):
                        y, x = self.offsets[off_i][off_j]
                        y = self.boundary_handler.get_idx(i + y, grid.height)
                        x = self.boundary_handler.get_idx(j + x, grid.width)

                        neighbourhood[off_i].append(grid[(y, x)])

                new_cells[i].append(self.process_cell(neighbourhood, grid[i, j]))

        return Grid2D(new_cells)

    def process_cell(self, neighbourhood: List[List[Cell]], old_cell: Cell) -> Cell:
        key = tuple(tuple(c.state for c in row) for row in neighbourhood)
        return Cell(self.mappings.get(key, False))


class Sum1DRuleset(Ruleset):
    """Cell state is updated based on the number of alive cells surrounding it."""

    def __init__(self, outcomes: Dict[int, bool], offsets: List[int], boundary="wrap"):
        self.outcomes = outcomes
        self.offsets = offsets
        self.boundary_handler = BoundaryModeFactory.get_boundary_handler(boundary)

    def process_grid(self, grid: Grid1D) -> Grid1D:
        new_cells = []
        for cell_idx in range(len(grid)):
            # Collect neighbouring cells
            neighbourhood = [grid[self.boundary_handler.get_idx(cell_idx + o, len(grid))] for o in self.offsets]
            new_cells.append(self.process_cell(neighbourhood, grid[cell_idx]))

        return Grid1D(new_cells)

    def process_cell(self, neighbourhood: List[Cell], old_cell: Cell) -> Cell:
        key = sum(c.state for c in neighbourhood)

        outcome = self.outcomes.get(key, False)
        if outcome == "same":
            return Cell(old_cell.state)
        else:
            assert type(outcome) == bool
            return Cell(outcome)

    def __repr__(self):
        return "\n".join([
            f"Neighbourhood: {self.offsets}",
            f"True sums: {[state for state, outcome in self.outcomes.items() if outcome == True]}",
            f"Survive sums: {[state for state, outcome in self.outcomes.items() if outcome == 'same']}",
        ])


class Ruleset1DFactory:
    """Responsible for creating specific instances of 1D Rulesets."""

    @staticmethod
    def wolfram(code: int, rule_class=3) -> Mapping1DRuleset:
        assert 0 <= code <= 2 ** (2 ** rule_class) - 1
        assert rule_class % 2 == 1

        states = bin(code)[2:][::-1]
        mappings = {}
        for i in range(2 ** rule_class):
            if i >= len(states):
                break

            if states[i] == "0":
                # Only store True outcomes
                continue

            # Determine the initial state (key)
            key = f"{bin(i)[2:]:0>{rule_class}}"  # As binary string
            key = tuple(k == "1" for k in key)  # As tuple of bools

            mappings[key] = True

        offsets = list(range(- (rule_class // 2), rule_class // 2 + 1))
        return Mapping1DRuleset(mappings, offsets)

    @staticmethod
    def from_ruleset_string(ruleset_string: str) -> Sum1DRuleset:
        """Generates a ruleset from a string."""

        tokens = ruleset_string.split(",")

        # First 3 tokens are fixed: Radius, C, Middle
        radius = int(tokens[0][1:])
        c = int(tokens[1][1:])  # todo: find out what C is and incorporate it in the rules.
        middle = bool(int(tokens[2][1:]))

        # Remaining tokens are either Survive or Born, all other outcomes are assumed dead.
        outcomes = {}
        for token in tokens[3:]:
            if token.startswith("S"):
                outcomes[int(token[1:])] = "same"
            elif token.startswith("B"):
                outcomes[int(token[1:])] = True
            else:
                raise ValueError(f"Error parsing token: {token}")

        # Offsets
        offsets = list(range(-radius, radius + 1))
        if not middle:
            offsets.pop(radius)

        return Sum1DRuleset(outcomes, offsets)

    @staticmethod
    def tulips() -> Sum1DRuleset:
        return Ruleset1DFactory.from_ruleset_string(
            "R10,C0,M1,S0,S3,S6,S10,S11,S14,S15,S16,S17,S18,S19,S20,S21,B1,B11,B12,B17,B18,B19,B20,B21")

    @staticmethod
    def city() -> Sum1DRuleset:
        return Ruleset1DFactory.from_ruleset_string("R3,C0,M0,S0,S3,B0,B4")

    @staticmethod
    def roots() -> Sum1DRuleset:
        return Ruleset1DFactory.from_ruleset_string("R4,C0,M1,S1,S2,S5,S6,S9,B3,B4,B6")

    @staticmethod
    def abacus() -> Sum1DRuleset:
        return Ruleset1DFactory.from_ruleset_string("R2,C0,M1,S1,B3")

    @staticmethod
    def class_4a() -> Sum1DRuleset:
        return Ruleset1DFactory.from_ruleset_string("R2,C0,M1,S1,B2,B3,B4")

    @staticmethod
    def date_palm() -> Sum1DRuleset:
        return Ruleset1DFactory.from_ruleset_string("R5,C0,M1,S7,S8,S9,S10,S11,B0")


class Ruleset2DFactory:
    """Responsible for creating specific instances of 2D Rulesets."""

    @staticmethod
    def game_of_life():
        """Conway's Game of Life"""
        # 3x3 neighbourhood
        offsets = [[(y, x) for y in range(-1, 2)] for x in range(-1, 2)]

        # Create mappings
        mappings = {}
        for i in range(2 ** 9):

            # Determine the initial state (key)
            key = f"{bin(i)[2:]:0>9}"  # As binary string
            key = tuple(k == "1" for k in key)  # As tuple of bools
            key = tuple(key[i * 3:i * 3 + 3] for i in range(3))  # Reshape into 2D grid

            # Alive counts
            centre = key[1][1]
            others = sum(sum(row) for row in key) - centre

            # Skip if state does not evaluate to True
            if centre:
                if others not in (2, 3):
                    continue

            else:
                if others != 3:
                    continue

            mappings[key] = True

        return Mapping2DRuleset(mappings, offsets)


if __name__ == '__main__':
    # r = Ruleset1DFactory.tulips()
    # r = Ruleset1DFactory.city()
    # r = Ruleset1DFactory.roots()
    # r = Ruleset1DFactory.abacus()
    # r = Ruleset1DFactory.class_4a()
    r = Ruleset1DFactory.date_palm()
    print(r)

    g = Grid1DFactory.random(200)
    # g = Grid1DFactory.point(200)
    print(g)

    for _ in range(100):
        # print("=" * 100)
        g = r.process_grid(g)
        print(g)
