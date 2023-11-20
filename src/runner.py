import logging
from typing import Any

from core.drone_constants import EMPTY_STRING
from core.drone_variables import DroneVariables
from llms.llm_manager import LLMManager
from prompts.prompt_factory import PromptFactory
from test_data import test_drones, test_terrains
from utils.drone_util import read_file

test_responses = {
    False: "../examples/numeric_response.txt",
    True: "../examples/alpha_response.txt"
}


def run(mock_response: bool = True, alpha_format: bool = True):
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.info("Starting prompt runner...")

    drone_variables = DroneVariables(
        drone_max_distance=8,
        drones=test_drones,
        terrains=test_terrains,
        battery_changing_stations=[(1, 1), (1, 14), (8, 14), (8, 1)],
        n_width_blocks=8,
        n_height_blocks=14,
        launch_point=(1, 1),
        battery_time=30,
        cells_in_single_battery=3,
        weather_status="sunny",
        search_priorities=["Waterways"],
        use_alphabetical=alpha_format
    )
    prompt_factory = PromptFactory(drone_variables)
    prompt = prompt_factory.build()

    logging.info(prompt)
    test_file = test_responses[alpha_format]
    res_text = read_file(test_file) if mock_response else LLMManager.make_completion(prompt)
    logging.info(res_text)

    drones = prompt_factory.parse(res_text)
    return drones


def prompt_tf(prompt: str, default_value: Any = None) -> bool:
    if default_value is not None:
        prompt = f"{prompt}({default_value})"
    pos_responses = ["t", "y"]
    user_response = input(prompt).lower()
    if user_response.strip() == EMPTY_STRING:
        return default_value
    return any([p in user_response for p in pos_responses])


if __name__ == "__main__":
    use_prompt = False
    kwargs = {}
    if use_prompt:
        kwargs["mock_response"] = prompt_tf("Mock OpenAI responses? (t/f)", True)
        kwargs["alpha_format"] = prompt_tf("Use alphabetical format (t/f)?", True)
    output = run(**kwargs)
    for drone in output:
        print(drone.id, ":", drone.coordinates)
