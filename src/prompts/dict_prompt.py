from typing import Dict, List, Union

from core.drone_constants import COMMA, EMPTY_STRING, NEW_LINE, TAB
from prompts.prompt import Prompt
from prompts.prompt_util import PromptUtil


class DictPrompt(Prompt):
    """
    Responsible for formatting and parsing of presenting a single dictionary in a prompt.
    """

    def __init__(self, tag_name: str, title: str = EMPTY_STRING):
        """
        Constructor for making a prompt from an dictionary
        :param tag_name: The name of tag to enclose content within.
        :param title: The prefix to the prompt.
        """
        self.tag_name = tag_name
        super().__init__(value=EMPTY_STRING, title=title, allow_formatting=False)

    def _build(self, obj: Dict, **kwargs) -> str:
        """
        Builds the artifact prompt using the given build method
        :param obj: The dictionary containing the attributes representing a drone
        :param kwargs: Ignored
        :return: The formatted prompt
        """
        prompt = f"{NEW_LINE}{self.value}{NEW_LINE}" if self.value else EMPTY_STRING
        obj = self._build_as_xml(obj=obj, tag=self.tag_name, **kwargs)
        return f"{prompt}{obj}"

    @classmethod
    def _build_as_xml(cls, obj: Dict, tag: str, **kwargs) -> str:
        """
        Formats the obj information using xml
        :param obj: The object to format as XML.
        :param tag: The tag to enclose content within.
        :return: The formatted prompt
        """
        inner_tags = [PromptUtil.create_xml(k, cls.get_value(v), prefix=TAB) for k, v in obj.items()]
        content = NEW_LINE.join(inner_tags)
        outer_tag = PromptUtil.create_xml(tag, f"{NEW_LINE}{content}{NEW_LINE}")
        return outer_tag

    @classmethod
    def get_value(cls, v: Union[List, str, int, float]) -> str:
        """
        Returns the formatted value of the dictionary property.
        :param v: The value to unwind into a primitive value.
        :return: The unwinded value.
        """
        if isinstance(v, list):
            return COMMA.join([cls.get_value(v_inner) for v_inner in v])
        return str(v)
