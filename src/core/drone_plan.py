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

    def add_to_plan(self, coordinates: List[BlockCoordinate]) -> None:
        """
        Adds the new coordinates to the plan.
        :param coordinates: List of coordinates to add.
        :return: None
        """
        if self.coordinates and self.coordinates[-1] == coordinates[0]:
            coordinates.pop(0)
        self.coordinates.extend(self.coordinates)

    def __add__(self, other: "DronePlan") -> "DronePlan":
        """
        Adds to drone plans together.
        :param other: Another plan.
        :return: The combined plan.
        """
        assert other.id == self.id, "Cannot add plans from different drones"
        self.add_to_plan(other.coordinates)
        return self

    def __repr__(self) -> str:
        """
        Pretty-prints the drone plan (ID: cells)
        """
        return f"{self.id}:{self.coordinates}"


class DronePlanManager:

    def __init__(self):
        """
        manages all drone plans
        """
        self.drone_id_to_plan = {}

    def add_plans(self, plans: List[DronePlan]) -> None:
        """
        Adds a new set of plans for the drones
        :param plans: List of drone plans
        :return: None
        """
        for plan in plans:
            if plan.id not in self.drone_id_to_plan:
                self.drone_id_to_plan[plan.id] = plan
            else:
                self.drone_id_to_plan[plan.id] += plan

    def get_plans(self) -> List[DronePlan]:
        """
        Gets a list of all drone plans
        :return: A list of all drone plans
        """
        return list(self.drone_id_to_plan.values())
