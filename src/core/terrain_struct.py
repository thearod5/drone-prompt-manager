from typing import List, TypedDict


class TerrainStruct(TypedDict):
    """
    :param type: The type of terrain the blocks represent.
    :param blocks: The blocks this terrain encompasses.
    """
    type: str
    blocks: List[str]
