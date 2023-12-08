from copy import deepcopy
from typing import List, Dict

from src.core.drone_constants import N_DRONE_FLIGHTS, STARTING_FLIGHT_PLAN_NUM
from src.core.drone_plan import DronePlanManager, DronePlan
from src.core.drone_variables import DroneVariables
from src.llms.llm_manager import LLMManager
from src.prompts.prompt_factory import PromptFactory
import logging


class PlanGenerator:

    def __init__(self, drone_variables: DroneVariables, ):
        """
        Uses the model to generate a flight plan for the scenario provided in the variables.
        :param drone_variables: The variables to include in the prompt.
        """
        self.initial_configuration = drone_variables
        self.current_configuration = drone_variables
        self.conversation_history = []

    def generate_adaption(self, plan_adaptation: str, current_location_of_drones: Dict, **params) -> List[DronePlan]:
        """
        Uses the model to generate an adapted flight plan with the new information.
        :param plan_adaptation: Contains the updated information for adapting the plan.
        :param current_location_of_drones: Maps the id of the drone to its current cell location.
          :return: A plan for each drone.
        """
        self.current_configuration = deepcopy(self.current_configuration)
        self.current_configuration.plan_adaptation = plan_adaptation
        self.current_configuration.add_current_location_to_drones(current_location_of_drones)
        return self._generate(**params)

    def generate_initial(self, **params) -> List[DronePlan]:
        """
        Uses the model to generate a flight plan for the scenario provided in the variables.
        :return: A plan for each drone.
        """
        self.current_configuration = self.initial_configuration
        return self._generate(**params)

    def _generate(self, mock_response: str = None) -> List[DronePlan]:
        """
        Uses the model to generate a flight plan for the scenario provided in the variables.
        :param mock_response: If provided, uses the mock response in place of an actual generation from the model.
        :return: A plan for each drone.
        """
        self.conversation_history.clear()
        prompt_factory = PromptFactory(self.current_configuration)
        drone_plan_manager = DronePlanManager()
        last_flight_plan_num = N_DRONE_FLIGHTS + STARTING_FLIGHT_PLAN_NUM
        for i in range(STARTING_FLIGHT_PLAN_NUM, last_flight_plan_num):
            prompt = prompt_factory.build(flight_plan_num=i)

            logging.info(f"Completing flight plan {i}")
            if mock_response:
                res_text = mock_response
            else:
                self.conversation_history = LLMManager.make_completion(prompt, conversation_history=self.conversation_history)
                res_text = self.conversation_history[-1]["content"]

            drones = prompt_factory.parse(res_text)
            drone_plan_manager.add_plans(drones)
            logging.info(res_text)

        return drone_plan_manager.get_plans()