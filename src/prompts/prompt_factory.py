import ast
from typing import Dict, List

from core.drone_constants import CELLS_KEY, DRONE_ID_KEY, DRONE_KEY, DronePromptArgs, NEW_LINE
from core.drone_plan import DronePlan
from core.drone_variables import DroneVariables
from prompts.prompt import Prompt
from prompts.prompt_builder import PromptBuilder
from prompts.prompt_response_manager import PromptResponseManager
from prompts.questionnaire_prompt import QuestionnairePrompt
from prompts.multi_dict_prompt import MultiDictPrompt
from utils.drone_util import parse_coordinates


class PromptFactory:
    def __init__(self, variables: DroneVariables):
        self.variables = variables
        self.response_manager = PromptResponseManager({
            DRONE_KEY: [DRONE_ID_KEY, CELLS_KEY]
        }, include_response_instructions=False)
        self.builder = None
        self.task_prompt = None

    def build(self) -> str:
        self.task_prompt = self._build_task_prompt(self.response_manager)
        self.builder = PromptBuilder([
            self._build_mission_description(),
            self._build_drones(),
            self._build_search_area(),
            self._build_objectives(self.variables.search_priorities),
            self._build_reasoning(),
            self.task_prompt
        ], title="Task")
        prompt = self.builder.build(DronePromptArgs,
                                    drone_max_distance=self.variables.drone_max_distance,
                                    n_width_blocks=self.variables.n_width_blocks,
                                    n_height_blocks=self.variables.n_height_blocks,
                                    launch_point=self.variables.launch_point,
                                    drones=self.variables.drones,
                                    terrains=self.variables.terrains,
                                    battery_time=self.variables.battery_time,
                                    cells_in_single_battery=self.variables.cells_in_single_battery,
                                    battery_changing_stations=self.variables.battery_changing_stations,
                                    delimiter=NEW_LINE + NEW_LINE)
        prompt_text = prompt["prompt"]
        return prompt_text

    def parse(self, res: str) -> List[DronePlan]:
        parsed_response = self.response_manager.parse_response(res)
        id2struct = {}
        for drone_plan in parsed_response[DRONE_KEY]:
            drone = self.entry_formatter(drone_plan)
            drone_id = drone[DRONE_ID_KEY]
            if drone_id not in id2struct:
                id2struct[drone_id] = []
            id2struct[drone_id].extend(drone[CELLS_KEY])

        drone_plans = [DronePlan(d_id, blocks) for d_id, blocks in id2struct.items()]
        return drone_plans

    @classmethod
    def entry_formatter(cls, v) -> Dict:
        drone_id = v[DRONE_ID_KEY][0]
        cells = [c for c_text in v[CELLS_KEY] for c in parse_coordinates(c_text)]
        return {
            DRONE_ID_KEY: drone_id,
            CELLS_KEY: cells
        }

    @staticmethod
    def parse_block_coordinates(input_str):
        parsed_data = ast.literal_eval(input_str)
        coordinate_list = [coord for coord in parsed_data]
        return coordinate_list

    @staticmethod
    def _build_mission_description():
        return Prompt(
            "A critical search and rescue mission is underway to locate a missing person in a designated area. "
            "The search zone has been organized into a grid format {n_width_blocks} cells wide and {n_height_blocks} cells high. "
            "Coordinate (1,1) is the top-left corner and ({n_width_blocks},{n_height_blocks}) is bottom-right corner.\n\n"
            "Drones will start from the origin point at {launch_point}. "
            "Each drone can fly for 30 minutes before needing to recharge batteries. "
            "Battery changing stations are located at coordinates {battery_changing_stations}. "
            "A drone can search up to {cells_in_single_battery} cells during a {battery_time} minute flight."
            "Drones can travel a maximum of {drone_max_distance} cells horizontally or vertically in one flight in one flight.\n\n"
            "Your task is to formulate a comprehensive plan using these drones to locate the missing person in the shortest time possible. ",
            title="Mission Description"
        )

    @staticmethod
    def _build_drones():
        return MultiDictPrompt(DRONE_KEY, title="Drone Statuses")

    @staticmethod
    def _build_search_area():
        return MultiDictPrompt("terrain", title="Search Area")

    @staticmethod
    def _build_objectives(search_priorities_list: List[str]):
        mission_constraints = QuestionnairePrompt([
            Prompt("Maximize search efficiency by prioritizing high probability areas."),
            Prompt("Create flight plans that maximize its battery life."),
            Prompt("Select the closest charging station to the drone's last search area."),
            Prompt("Ensure at least one drone is always searching."),
            Prompt("During dusk or nighttime conditions use thermal camera."),
        ], title="Objectives")
        if len(search_priorities_list) > 0:
            item_indices = ["i.", "ii.", "iii.", "iv.", "v."][:len(search_priorities_list)]
            search_priorities = QuestionnairePrompt([
                Prompt(p) for p in search_priorities_list
            ], enumeration_chars=item_indices,
                instructions=f"Order of Search Priorities")
            mission_constraints.question_prompts.append(search_priorities)
        return mission_constraints

    @staticmethod
    def _build_reasoning():
        return Prompt(
            "First, consider all the constraints placed on the mission. "
            "Describe any obstacles present in the current constraints."
            "Then, describe how you plan to construct the flight plans. "
            "Use this to make a draft of your plans.",
            title="Mission Reasoning", response_manager=PromptResponseManager(response_tag="reasoning")
        )

    @staticmethod
    def _build_task_prompt(response_manager: PromptResponseManager):
        instructions = "Then, create a flight route for each drones to cover the entire search area. " \
                       f"Each flight plan should be enclosed in <{DRONE_KEY}></{DRONE_KEY}> and include:\n"
        flight_plan_questionnaire = QuestionnairePrompt([
            Prompt(f"The drone ID enclosed within <{DRONE_ID_KEY}></{DRONE_ID_KEY}>"),
            Prompt(f"List of cells coordinates (x,y) determining the drone's flight route within <{CELLS_KEY}></{CELLS_KEY}>."),
            Prompt("The flight route should begin with the drone current cell, "
            "followed by {cells_in_single_battery} cells to search and the cell of the closest charging station."
            "Continue the pattern of {cells_in_single_battery} search cells and a charging station until the plan is complete. "
            f"List search cells and charging stations in the same <{CELLS_KEY}></{CELLS_KEY}>."
            "This section should be formatted as strict XML and include complete flight plans.")
        ], response_manager=response_manager, instructions=instructions, enumeration_chars=["-"])
        return flight_plan_questionnaire
