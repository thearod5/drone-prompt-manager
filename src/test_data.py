from typing import List

from core.drone_struct import DroneStruct
from utils.drone_util import to_numeric

test_terrains = [
    {
        "type": "Waterway",
        "blocks": to_numeric(["B2", "C1", "C2", "C3", "D1", "D2", "D3", "E1", "E2", "E3", "F1", "G1", "H1", "H2",
                             "H3", "H4", "H5", "H6", "H7", "H8", "H9", "G9", "F9"])
    },
    {
        "type": "Woodland",
        "blocks": to_numeric(["A5", "B3", "B4", "B5", "B6", "C4", "C5", "C6", "D4", "D5", "D6", "E8", "F8", "G5", "G6", "G7"])
    },
    {
        "type": "Waterway",
        "blocks": to_numeric(["A13", "A14", "B12", "B13", "B14", "C12", "C13", "C14", "D12"])
    },
    {
        "type": "Woodland",
        "blocks": to_numeric(["D13", "D14", "E12", "E13", "E14", "F12", "F13", "F14", "G12", "G13", "G14", "H11"])
    }
]
test_drones: List[DroneStruct] = [
    {
        "id": "Red",
        "camera": ["RBG"]
    }, {
        "id": "Blue",
        "camera": ["RBG", "Thermal"]
    }, {
        "id": "Purple",
        "camera": ["RBG"],
        "equipment": ["Flotation Device"]
    }, {
        "id": "Yellow",
        "camera": ["RBG"]
    }, {
        "id": "Green",
        "camera": ["RBG"]
    }
]
