from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import getrandbits
from typing import List, Tuple


@dataclass
class Cell:
    """Represents the state of a single cell."""
    state: bool

    def __repr__(self):
        return "#" if self.state else " "


@dataclass
class Grid(ABC):
    @abstractmethod
    def __getitem__(self, item) -> Cell:
        """Returns a cell at a given position."""

    @abstractmethod
    def __repr__(self) -> str:
        """String representation of the grid"""


@dataclass
class Grid1D(Grid):
    """Represents a grid of cells."""
    cells: List[Cell]

    def __len__(self):
        return len(self.cells)

    def __getitem__(self, i):
        return self.cells[i]

    def __repr__(self):
        return "".join(list(map(str, self.cells)))


@dataclass
class Grid2D(Grid):
    """Represents a 2D grid."""
    cells: List[List[Cell]]

    @property
    def height(self) -> int:
        return len(self.cells)

    @property
    def width(self) -> int:
        return len(self.cells[0])

    def size(self) -> Tuple[int, int]:
        """Retuns (height, width)"""
        return self.height, self.width

    def __getitem__(self, idx_tuple: Tuple[int, int]):
        y, x = idx_tuple
        return self.cells[y][x]

    def __setitem__(self, idx_tuple: Tuple[int, int], state: bool):
        y, x = idx_tuple
        self.cells[y][x].state = state

    def __repr__(self):
        return "\n".join([
            "".join(list(map(str, row))) for row in self.cells
        ])


class Grid1DFactory:
    @staticmethod
    def random(n: int) -> Grid1D:
        """Generates a random grid."""
        states = f"{bin(getrandbits(n))[2:]:0>{n}}"
        return Grid1D([Cell(s == "1") for s in states])

    @staticmethod
    def empty(n: int) -> Grid1D:
        return Grid1D([Cell(False) for _ in range(n)])

    @staticmethod
    def point(n: int) -> Grid1D:
        g = Grid1DFactory.empty(n)

        # Set central cell to true
        g[n // 2].state = True

        return g


class Grid2DFactory:
    @staticmethod
    def glider_demo() -> Grid2D:
        g = Grid2DFactory.empty(10, 10)

        # Create glider
        g[(1, 1)] = True
        g[(1, 3)] = True
        g[(2, 2)] = True
        g[(2, 3)] = True
        g[(3, 2)] = True

        return g

    @staticmethod
    def random(height: int, width: int) -> Grid2D:
        rows = []
        for row in range(height):
            states = f"{bin(getrandbits(width))[2:]:0>{width}}"
            rows.append([Cell(s == "1") for s in states])

        return Grid2D(rows)

    @staticmethod
    def empty(height: int, width: int) -> Grid2D:
        return Grid2D([[Cell(False) for j in range(width)]
                       for i in range(height)])


if __name__ == '__main__':
    # g = Grid1D.random_grid(25)
    # print(g)
    # print()
    # print()
    #
    # g = Grid2D.random_grid(25, 25)
    # print(g)

    g = Grid2DFactory.glider_demo()
    print(g)
