from copy import deepcopy
from typing import List, Dict

from core.drone_constants import N_DRONE_FLIGHTS, STARTING_FLIGHT_PLAN_NUM
from core.drone_plan import DronePlanManager, DronePlan
from core.drone_variables import DroneVariables
from llms.llm_manager import LLMManager
from prompts.prompt_factory import PromptFactory
import logging
import os
from xml.etree.ElementTree import Element, ElementTree
from datetime import datetime
import copy 
import time 

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


    def save_xml_to_file(self,folder_path,xml_data_initial,xml_adaptation=None):
        """Saves the XML data to a file with the current date and time in its name."""
        # Format the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"drone_flights_{current_time}.xml"
        file_path = os.path.join(folder_path, file_name)

        if xml_adaptation:
            file_name_adapted = f"drone_flights_adapted_{current_time}.xml"
            file_path_adapted = os.path.join(folder_path,file_name_adapted)

        # Write the XML data to the file
        tree = ElementTree(xml_data_initial)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        
        tree = ElementTree(xml_adaptation)
        tree.write(file_path_adapted, encoding='utf-8', xml_declaration=True)
        print(f"Drone Flights saved to {file_path}")
        #print(f"Drone FLights Adapted saved to {file_path_adapted}")

    def _generate(self, mock_response: str = None) -> List[DronePlan]:
        """
        Uses the model to generate a flight plan for the scenario provided in the variables.
        :param mock_response: If provided, uses the mock response in place of an actual generation from the model.
        :return: A plan for each drone.
        """
        self.conversation_history.clear()
        prompt_factory = PromptFactory(self.current_configuration)
        drone_plan_manager = DronePlanManager()
        for i in range(10):
            prompt = prompt_factory.build(flight_plan_num=i)
            logging.info(f"Recieving flight plan {i+1}")
            print()
            print("################################")
            print(prompt)
            print("#################################")
            print()
            if mock_response:
                res_text = mock_response
            else:
                #time.sleep(3)
                self.conversation_history = LLMManager.make_completion(prompt, conversation_history=self.conversation_history)
                res_text = self.conversation_history[-1]["content"]
            end_mission = prompt_factory.parse(res_text)
            print('end mission',end_mission)
            if end_mission:
                print('ending mission')
                break
            #drone_plan_manager.add_plans(drones)

        #new code to enable adaptation 
        xml_front_end = prompt_factory.response_manager.get_front_end_xml()
        print("XML STRING")
        self.save_xml_to_file("/Users/theochambers/drone-prompt-manager/src/front_end",xml_front_end)
        '''
        xml_front_end = prompt_factory.response_manager.get_front_end_xml()
        prompt_factory.response_manager.adapted_xml_front_end = copy.deepcopy(xml_front_end)
        prompt_factory.adaptation = True
        prompt_factory.variables.plan_adaptation = "The missing person has been found at location K10."
        prompt = prompt_factory.build(1)
        logging.info(f"Adaptation Inbound")
        print()
        print("Adapted Prompt")
        print("################################")
        print(prompt)
        print("#################################")
        print()
        self.conversation_history = LLMManager.make_completion(prompt, conversation_history=self.conversation_history)
        res_text = self.conversation_history[-1]["content"]
        prompt_factory.parse(res_text,1)

        #generate next flight adaptation
        prompt = prompt_factory.build(5)
        print()
        print("################################")
        print(prompt)
        print("#################################")
        print()
        self.conversation_history = LLMManager.make_completion(prompt, conversation_history=self.conversation_history)
        res_text = self.conversation_history[-1]["content"]
        prompt_factory.parse(res_text,5)
        xml_front_end_adapted = prompt_factory.response_manager.get_front_end_xml_adapted()
        self.save_xml_to_file("/Users/theochambers/drone-prompt-manager/src/front_end",xml_front_end,xml_front_end_adapted)
        return drone_plan_manager.get_plans()
        '''
        return 

     