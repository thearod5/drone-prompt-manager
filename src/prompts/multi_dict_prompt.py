from typing import Dict, List

from core.drone_constants import EMPTY_STRING, NEW_LINE
from prompts.dict_prompt import DictPrompt
from prompts.prompt import Prompt


class MultiDictPrompt(Prompt):
    """
    Responsible for formatting and parsing of presenting many drones in a prompt
    """

    def __init__(self, tag_name: str, title: str = EMPTY_STRING):
        """
        Constructor for making a prompt containing many artifacts.
        :param tag_name: Name of tag used to enclose individual content.
        :param title: The prefix to attach to prompt.
        """
        self.tag_name = tag_name
        super().__init__(value=EMPTY_STRING, title=title)

    def _build(self, drones: List[Dict] = None, terrains: List[Dict] = None, **kwargs) -> str:
        """
        Builds the artifacts prompt using the given build method
        :param content: The list of dictionaries containing the attributes representing each drone
        :param kwargs: Ignored
        :return: The formatted prompt
        """
        prompt = f"{NEW_LINE}{self.value}{NEW_LINE}" if self.value else EMPTY_STRING
        content = self._build_as_xml(drones=drones, terrains=terrains)
        return f"{prompt}{content}"

    def _build_as_xml(self, drones: List[Dict], terrains: List[Dict] = None, **kwargs):
        """
        Formats the drone information in xml
        :param drones: The list of dictionaries containing the attributes representing each drone
        :return: The formatted prompt
        """
        objs = drones if self.tag_name == "drone" else terrains
        drone_prompt = DictPrompt(self.tag_name)
        formatted_drones = [drone_prompt.build(obj=obj, **kwargs) for obj in objs]
        content = NEW_LINE.join(formatted_drones)
        return content
