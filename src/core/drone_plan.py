from typing import List

from core.drone_constants import BlockCoordinate


class DronePlan:

    def __init__(self, drone_id: str, cells: List[BlockCoordinate]):
        """
        Creates a plan for a drone.
        :param drone_id: Id of drone.
        :param cells: The blocks that
        """
        self.id = drone_id
        self.coordinates = cells

    def __repr__(self) -> str:
        """
        Pretty-prints the drone plan (ID: cells)
        """
        return f"{self.id}:{self.coordinates}"
