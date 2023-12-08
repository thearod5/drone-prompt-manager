import logging
import random
from typing import Any, List

from core.drone_constants import EMPTY_STRING
from core.drone_variables import DroneVariables
from src.core.drone_plan import DronePlan
from src.core.plan_generator import PlanGenerator
from test_data import test_drones, test_terrains

MOCK_DEFAULT = False
ALPHA_DEFAULT = True
test_responses = {
    False: "../examples/numeric_response.txt",
    True: "../examples/alpha_response.txt"
}
drone_variables = DroneVariables(
    drone_max_distance=8,
    drones=test_drones,
    terrains=test_terrains,
    battery_changing_stations=[(1, 1), (1, 14), (8, 14), (8, 1)],
    n_width_blocks=28,
    n_height_blocks=16,
    launch_point=(1, 1),
    battery_time=30,
    cells_in_single_battery=8,
    weather_status="sunny",
    search_priorities=["Search bodies of water first.", "Search woods next.", "Search areas immediately adjacent to woods."],
    use_alphabetical=ALPHA_DEFAULT,
)


def run_initial_plan_generation(should_mock: bool = MOCK_DEFAULT):
    logging.info("Running initial plan generation")
    mock_response = test_responses[ALPHA_DEFAULT] if should_mock else None
    plan_generator = PlanGenerator(drone_variables)
    initial_plan = plan_generator.generate_initial(mock_response=mock_response)
    return initial_plan


def run_adaption_plan_generation(adapted_plan: List[DronePlan], current_index_of_drones: int, plan_adaptation: str,
                                 should_mock: bool = MOCK_DEFAULT):
    logging.info("Running plan adaption")
    mock_response = test_responses[ALPHA_DEFAULT] if should_mock else None
    plan_generator = PlanGenerator(drone_variables)
    drone_locations = {drone_plan.id: drone_plan.coordinates[current_index_of_drones] for drone_plan in adapted_plan}
    adapted_plan = plan_generator.generate_adaption(plan_adaptation=plan_adaptation,
                                                    current_location_of_drones=drone_locations,
                                                    mock_response=mock_response)
    return adapted_plan


def prompt_tf(prompt: str, default_value: Any = None) -> bool:
    if default_value is not None:
        prompt = f"{prompt}({default_value})"
    pos_responses = ["t", "y"]
    user_response = input(prompt).lower()
    if user_response.strip() == EMPTY_STRING:
        return default_value
    return any([p in user_response for p in pos_responses])


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.info("Starting prompt runner...")
    initial = run_initial_plan_generation(should_mock=MOCK_DEFAULT)
    adaption = run_adaption_plan_generation(plan_adaptation="The missing person has been found at location K10.",
                                            adapted_plan=initial,
                                            current_index_of_drones=random.randint(0, len(initial[0].coordinates))-1,
                                            should_mock=MOCK_DEFAULT)
    for drone in initial:
        print(drone.id, ":", drone.coordinates)
