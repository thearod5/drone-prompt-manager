import ast
from typing import Dict, List, Tuple

from core.drone_constants import CELLS_KEY, DRONE_ID_KEY, DRONE_KEY, DronePromptArgs, NEW_LINE
from core.drone_plan import DronePlan
from core.drone_variables import DroneVariables
from prompts.multi_dict_prompt import MultiDictPrompt
from prompts.prompt import Prompt
from prompts.prompt_builder import PromptBuilder
from prompts.prompt_response_manager import PromptResponseManager
from prompts.questionnaire_prompt import QuestionnairePrompt
from utils.drone_util import parse_coordinates

from src.core.drone_constants import STARTING_FLIGHT_PLAN_NUM, START_KEY, SEARCH_KEY, END_KEY
from src.prompts.prompt_util import PromptUtil


class PromptFactory:
    RESPONSE_FORMAT_EXAMPLE = {DRONE_ID_KEY: "[Drone ID e.g., Purple]",
                               START_KEY: "[Starting Cell]",
                               SEARCH_KEY: "[List of adjacent cells to search separated by commas]",
                               END_KEY: "[Ending Cell (nearest charging station)]"}
    ORDINAL_NUMBERS = ["first", "second", "third", "fourth", "fifth"]

    def __init__(self, variables: DroneVariables):
        """
        Builds the prompt for creating a drone plan.
        :param variables: The variables to include in the prompt.
        """
        self.variables = variables
        self.builder = None
        self.task_prompt = None
        self.response_manager = PromptResponseManager({
            DRONE_KEY: list(self.RESPONSE_FORMAT_EXAMPLE.keys())
        }, include_response_instructions=False)

    def build(self, flight_plan_num: int) -> str:
        """
        Builds the prompt for the whichever flight plan is being generated.
        :param flight_plan_num: Which flight plan is being generated.
        :return: The prompt to provide to generate the flight plan.
        """

        if flight_plan_num == STARTING_FLIGHT_PLAN_NUM:
            if self.variables.plan_adaptation:
                self.task_prompt = self._build_adaption_prompt()
                objective_prompt = None
            else:
                self.task_prompt = self._build_task_prompt(flight_plan_num=flight_plan_num)
                objective_prompt = self._build_objectives(self.variables.search_priorities)
            tasks = [
                self._build_mission_description(), self._build_flight_stages_description(), self._build_search_rules(),
                self._build_search_area(), self._build_drones(), QuestionnairePrompt([self._build_reasoning(), self.task_prompt],
                                                                                     instructions=PromptUtil.as_markdown_header(
                                                                                         "TASKS"))
            ]
            if objective_prompt:
                tasks.insert(3, objective_prompt)
        else:
            tasks = [self.task_prompt]
        self.builder = PromptBuilder(tasks, title="Task")
        prompt = self.builder.build(DronePromptArgs,
                                    **vars(self.variables),
                                    delimiter=NEW_LINE + NEW_LINE)
        prompt_text = prompt["prompt"]
        return prompt_text

    def parse(self, res: str) -> List[DronePlan]:
        """
        Parses the response from the model to create a flight plan.
        :param res: The response from the model.
        :return: A list of plans for each drone.
        """
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

    def entry_formatter(self, v) -> Dict:
        """
        Formats the entry for each drone.
        :param v: The parsed response for the drone.
        :return: Dictionary containing plan info for the Drone.
        """
        cells = self._get_response_values(v, [START_KEY, SEARCH_KEY, END_KEY])
        drone_id = v[DRONE_ID_KEY][0]
        parsed_cells = []
        for cell in cells:
            parsed_cells.extend(
                [c for c in parse_coordinates(cell, alpha_format=self.variables.use_alphabetical)])
        return {
            DRONE_ID_KEY: drone_id,
            CELLS_KEY: parsed_cells
        }

    @staticmethod
    def _get_response_values(res: Dict, keys: List[str]) -> Tuple:
        """
        Retrieves the value of the given keys from the response.
        :param res: The model's response.
        :param keys: The list of keys to get values for.
        :return: Values for each of the keys.
        """
        values = []
        for k in keys:
            values.append(res[k][0])
        return tuple(values)

    @staticmethod
    def parse_block_coordinates(input_str: str) -> List:
        """
        Parses the coordinates from the input.
        :param input_str: String containing the coordinates.
        :return: A list of the coordinates parsed
        """
        parsed_data = ast.literal_eval(input_str)
        coordinate_list = [coord for coord in parsed_data]
        return coordinate_list

    @staticmethod
    def _build_search_rules() -> Prompt:
        """
        Builds the prompt containing the search rules
        :return: The prompt containing the search rules
        """
        search_strategies = ["IF a cell has already been searched it MUST NOT be searched again in this plan."]
        return QuestionnairePrompt(question_prompts=[Prompt(stage) for stage in search_strategies],
                                   instructions="Search RULES are")

    def _build_mission_description(self) -> Prompt:
        """
       Builds the prompt containing the mission description
       :return: The prompt containing the mission description
       """
        top_right_coordinate = self.variables.translate_coordinate((1, 1))
        bottom_right_coordinate = self.variables.translate_coordinate((self.variables.n_width_blocks, self.variables.n_height_blocks))
        mission_description = Prompt(
            "A critical search and rescue mission is underway to locate a missing person in a designated area. "
            "The search zone has been organized into a grid format {n_width_blocks} cells wide and {n_height_blocks} cells high. "
            f"Coordinate {top_right_coordinate} is the top-left corner and {bottom_right_coordinate} is bottom-right corner. "
            f"A cell in the top row is not adjacent to a cell in the bottom row.  There is no wrapping.  "
            "This is also true of the leftmost and rightmost columns.  They are not adjacent to each other. \n\n"
            "Each drone can fly for {battery_time} minutes before needing to recharge batteries. "
            "All drones start their first flight at the launch pad, and end at the nearest charging station.  "
            "All subsequent flights start at the nearest recharging stations. ",
            title="Mission Description"
        )
        if self.variables.plan_adaptation:
            mission_description.value += "\n*UPDATE*: {plan_adaptation} " \
                                         f"Your goal will be to adapt the current plan with this new information."
        return mission_description

    @staticmethod
    def _build_flight_stages_description() -> Prompt:
        """
       Builds the prompt containing the flight stages
       :return: The prompt containing the flight stages
       """
        stages = ["Flying from its current cell to the starting cell of its search.",
                  "A series of adjacent cells representing its search. It can search {cells_in_single_battery} cells.",
                  "A flight from the final cell searched to a charging station "
                  "or back to the launch point which is also a charging station."]
        return QuestionnairePrompt(question_prompts=[Prompt(stage) for stage in stages],
                                   instructions="Each flight consists of three stages:")

    def _build_drones(self) -> Prompt:
        """
       Builds the prompt containing the drone info
       :return: The prompt containing the drone info
       """
        instructions = "All drones start at the launch point. The launch point is an additional battery charging station.\n " \
            if not self.variables.plan_adaptation else ""
        return MultiDictPrompt(DRONE_KEY, title="Drones", instructions=f"{instructions}Here are the available drones:")

    @staticmethod
    def _build_search_area() -> Prompt:
        """
       Builds the prompt containing the search area info
       :return: The prompt containing the search area info
       """
        return MultiDictPrompt("terrain", title="Search Area",
                               instructions="The location of woods, water bodies, the launch pad, "
                                            "and charging stations is provided in this xml file:")

    @staticmethod
    def _build_objectives(search_priorities_list: List[str]) -> Prompt:
        """
       Builds the prompt containing the search objectives
       :return: The prompt containing the search objectives
       """
        mission_constraints = QuestionnairePrompt([
            Prompt("Minimize the distance from the last searched cell to its charging station.")
        ], title="Search strategies")
        if len(search_priorities_list) > 0:
            item_indices = ["i.", "ii.", "iii.", "iv.", "v."][:len(search_priorities_list)]
            search_priorities = QuestionnairePrompt([
                Prompt(p) for p in search_priorities_list
            ], enumeration_chars=item_indices,
                instructions=f"Order of Search Priorities")
            mission_constraints.question_prompts.append(search_priorities)
        return mission_constraints

    def _build_reasoning(self) -> Prompt:
        """
       Builds the prompt containing reasoning questions for the model
       :return: The prompt containing reasoning questions for the model
       """
        if self.variables.plan_adaptation:
            questions = ["How will adjust the plan based on the new information?"]
        else:
            questions = ["Can drones search cells that have already been searched?",
                         "How could battery usage be optimized?", "What area should each drone search first and why? "
                                                                  "Note: it may be different for each drone."]
        return QuestionnairePrompt(
            [Prompt(q) for q in questions],
            instructions=f"First, please explain what you understand about the mission by answering {len(questions)} questions:",
            response_manager=PromptResponseManager(response_tag="reasoning")
        )

    def _build_task_prompt(self, flight_plan_num: int) -> Prompt:
        """
       Builds the prompt containing the main task (build a flight plan) for the model
       :param flight_plan_num: The number of the current flight plan to generate.
       :return: The prompt containing the main task (build a flight plan) for the model
       """
        instructions = f"Next, please plan the {self.ORDINAL_NUMBERS[flight_plan_num]} " \
                       f"flight for each of the {len(self.variables.drones)} drones.  " \
                       f"Each drone should have a unique plan. If the drone has special equipment, " \
                       f"consider optimizing the plan to where it is best suited. "
        return self._get_task_prompt(instructions=instructions, flight_plan_num=flight_plan_num)

    def _build_adaption_prompt(self) -> Prompt:
        """
       Builds the prompt containing the adaption task  for the model
       :return: The prompt containing adaption task for the model
       """
        instructions = "Remember: {plan_adaptation}\n" \
                       f"With this new information, create a flight for each of the {len(self.variables.drones)} drones.  " \
                       f"Each drone should have a unique plan. If the drone has special equipment, " \
                       f"consider optimizing the plan to where it is best suited. " \
                       f"Each drone must start at its current location. "
        return self._get_task_prompt(instructions=instructions)

    def _get_task_prompt(self, instructions: str, flight_plan_num: int = STARTING_FLIGHT_PLAN_NUM) -> Prompt:
        """
        Gets that task prompt for the model using the given instructions.
         :param flight_plan_num: The number of the current flight plan to generate.
        :param instructions: The instructions to include in the prompt.
        :return: The task prompt
        """
        if flight_plan_num == STARTING_FLIGHT_PLAN_NUM:
            instructions += "Each drone must cover approximately {cells_in_single_battery} cells, " \
                            "and then return to a charging cell. Drones can only move to adjacent cells. " \
                            "Structure output as follows:\n"
            instructions += MultiDictPrompt(DRONE_KEY).build(drones=[self.RESPONSE_FORMAT_EXAMPLE])
        else:
            instructions += f"Each drone should start at the Ending Cell ({END_KEY}) of its last flight."
        flight_plan_questionnaire = Prompt(instructions, response_manager=self.response_manager)
        return flight_plan_questionnaire
