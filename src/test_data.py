from typing import List

from core.drone_struct import DroneStruct
from utils.drone_util import to_numeric

test_terrains = [
    {
        "type": "Waterway",
        "blocks": to_numeric(
            ["B22", "B23", "B24", "C22", "C23", "C24", "D21", 'D22', "D23", "D24", "E21", "E22", "E23", "E24", "F21", "F22", "F23",
             "G21", "G22", "G23", "G24"])
    },
    {
        "type": "Woodland",
        "blocks": to_numeric(
            ["B3", "B4", "B5", "B6", "C3", "C4", "C5", "C6", "D3", "D4", "D5", "D6", "E3", "E4", "E5", "E6", "F5", "F6", "G5", "G6"])
    },
    {
        "type": "Waterway",
        "blocks": to_numeric(
            ["J2", "J3", "J4", "K2", "K3", "K4", "L2", "L3", "L4", "M2", "M3", "N2", "O2", "P10", "P11", "P12", "P2", "P3", "P4", "P5",
             "P6", "P7", "P8", "P9"])
    },
    {
        "type": "Woodland",
        "blocks": to_numeric(
            ["E15", "E16", "E17", "F15", "F16", "F17", "G13", "G14", "G15", "G16", "H13", "H14", "H15", "I13", "I14", "J14"])
    },
    {
        "type": "LaunchPad",
        "blocks": to_numeric(["I8"])
    },
    {
        "type": "BatteryCharging",
        "blocks": to_numeric(["N16"])
    },
    {
        "type": "BatteryCharging",
        "blocks": to_numeric(["E20"])
    },
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
