from abc import ABC


class BoundaryHandler(ABC):
    def get_idx(self, index: int, grid_size: int) -> int:
        """Handles how indices are mapped at grid boundaries"""


class WrapBoundaryHandler(BoundaryHandler):
    def get_idx(self, index: int, grid_size: int) -> int:
        """Loops around on the other side of the grid."""
        return index % grid_size


class ClipBoundaryHandler(BoundaryHandler):
    def get_idx(self, index: int, grid_size: int) -> int:
        if index >= grid_size:
            return grid_size

        return index
