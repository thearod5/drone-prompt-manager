from typing import List, Optional, TypedDict


class DroneStruct(TypedDict):
    """
    :param id: Any unique identifier for the drone. Colors are nice to use.
    :param camera: The cameras available on the drones.
    :param equipment: Any additional equipment available on the drone.
    """
    id: str
    camera: Optional[List[str]]
    equipment: Optional[List[str]]
