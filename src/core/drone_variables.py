import string
from dataclasses import dataclass
from typing import List, Tuple, Union

from core.drone_constants import COMMA
from core.drone_struct import DroneStruct
from core.terrain_struct import TerrainStruct

CoordinateType = Tuple[int, int]


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
    battery_changing_stations: Union[List[CoordinateType], str]
    drone_max_distance: int
    n_width_blocks: int
    n_height_blocks: int
    launch_point: Union[CoordinateType, str]
    battery_time: int
    cells_in_single_battery: int
    search_priorities: List[str]
    weather_status: str
    use_alphabetical: bool = True

    def __post_init__(self):
        """
        Translates
        :return:
        """
        self.translate_coordinates()

    def translate_coordinates(self) -> None:
        """
        Translates the coordinates in the state to the right format (e.g. alphabetical / numeric).
        :return: None
        """
        if isinstance(self.battery_changing_stations, list):
            translated_coordinates = [self.translate_coordinate(c) for c in self.battery_changing_stations]
            self.battery_changing_stations = COMMA.join(translated_coordinates)
        if isinstance(self.launch_point, tuple):
            self.launch_point = self.translate_coordinate(self.launch_point)

        for i in range(len(self.terrains)):
            t_blocks = self.terrains[i]["blocks"]
            self.terrains[i]["blocks"] = [self.translate_coordinate(c) for c in t_blocks]

    def translate_coordinate(self, coordinate: CoordinateType) -> str:
        """
        Translates the coordinate to the set type (e.g. alphabetical or numeric)
        :param coordinate: The coordinate to translate.
        :return: The translated coordinate.
        """
        x = coordinate[0]
        y = coordinate[1]
        if self.use_alphabetical:
            x = string.ascii_uppercase[x - 1]
            return f"{x}{y}"
        return f"({x}, {y})"
 