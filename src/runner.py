import logging
from typing import Any

from core.drone_constants import EMPTY_STRING
from core.drone_variables import DroneVariables
from src.core.plan_generator import PlanGenerator
from test_data import test_drones, test_terrains

MOCK_DEFAULT = False
ALPHA_DEFAULT = True
test_responses = {
    False: "../examples/numeric_response.txt",
    True: "../examples/alpha_response.txt"
}


def run(should_mock: bool = MOCK_DEFAULT, alpha_format: bool = ALPHA_DEFAULT):
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.info("Starting prompt runner...")

    drone_variables = DroneVariables(
        drone_max_distance=8,
        drones=test_drones,
        terrains=test_terrains,
        battery_changing_stations=[(1, 1), (1, 14), (8, 14), (8, 1)],
        n_width_blocks=28,
        n_height_blocks=16,
        launch_point=(1, 1),
        battery_time=30,
        cells_in_single_battery=3,
        weather_status="sunny",
        search_priorities=["Search bodies of water first.", "Search woods next.", "Search areas immediately adjacent to woods."],
        use_alphabetical=alpha_format
    )

    mock_response = test_responses[alpha_format] if should_mock else None
    plan_generator = PlanGenerator(drone_variables)
    initial_plan = plan_generator.generate_initial(mock_response=mock_response)
    return initial_plan


def prompt_tf(prompt: str, default_value: Any = None) -> bool:
    if default_value is not None:
        prompt = f"{prompt}({default_value})"
    pos_responses = ["t", "y"]
    user_response = input(prompt).lower()
    if user_response.strip() == EMPTY_STRING:
        return default_value
    return any([p in user_response for p in pos_responses])


if __name__ == "__main__":
    use_interactive = False
    kwargs = {}
    if use_interactive:
        kwargs["mock_response"] = prompt_tf("Mock OpenAI responses? (t/f)", MOCK_DEFAULT)
        kwargs["alpha_format"] = prompt_tf("Use alphabetical format (t/f)?", ALPHA_DEFAULT)
    output = run(**kwargs)
    for drone in output:
        print(drone.id, ":", drone.coordinates)
