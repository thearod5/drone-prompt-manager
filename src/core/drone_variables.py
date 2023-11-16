from dataclasses import dataclass
from typing import List

from core.drone_struct import DroneStruct
from core.terrain_struct import TerrainStruct


@dataclass
class DroneVariables:
    """
    :param drones: List of drones available for the mission.
    :param terrains: List of terrains that are identified in the search area.
    :param n_width_blocks: The width of the search area in blocks.
    :param n_height_blocks: The height of the search area in blocks.
    :param launch_point: The launch point of the drones / mission control.
    :param battery_time: The length of a single battery run in minutes.
    :param cells_in_single_battery: The number of cells that can be searched in a single battery life.
    :param search_priorities: Human made list of terrains to prioritize.
    """
    drones: List[DroneStruct]
    terrains: List[TerrainStruct]
    battery_changing_stations: str
    drone_max_distance: int
    n_width_blocks: int
    n_height_blocks: int
    launch_point: str
    battery_time: int
    cells_in_single_battery: int
    search_priorities: List[str]
