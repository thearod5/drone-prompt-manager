import logging
import os

from llms.llm_manager import LLMManager
from core.drone_variables import DroneVariables
from prompts.prompt_factory import PromptFactory
from test_data import test_drones, test_terrains
from utils.drone_util import read_file


def run(use_mock: bool = True):
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.info("Starting prompt runner...")

    drone_variables = DroneVariables(
        drone_max_distance=8,
        drones=test_drones,
        terrains=test_terrains,
        battery_changing_stations="(1,1), (1, 14), (8, 14), (8,1)",
        n_width_blocks=8,
        n_height_blocks=14,
        launch_point="(1,1)",
        battery_time=30,
        cells_in_single_battery=3,
        search_priorities=["Waterways"]
    )
    prompt_factory = PromptFactory(drone_variables)
    prompt = prompt_factory.build()

    logging.info(prompt)
    res_text = read_file("../output/response.txt") if use_mock else LLMManager.make_completion(prompt)
    logging.info(res_text)

    drones = prompt_factory.parse(res_text)
    return drones


if __name__ == "__main__":
    output = run()
    for drone in output:
        print(drone.id, ":", drone.coordinates)
