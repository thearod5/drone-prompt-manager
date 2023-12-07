from typing import List

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
        self.drone_variables = drone_variables
        self.conversation_history = []

    def generate_initial(self, mock_response: str = None) -> List[DronePlan]:
        """
        Uses the model to generate a flight plan for the scenario provided in the variables.
        :param mock_response: If provided, uses the mock response in place of an actual generation from the model.
        """
        prompt_factory = PromptFactory(self.drone_variables)
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
