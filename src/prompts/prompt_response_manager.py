import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Set, Tuple, Type, Union

import bs4

from core.drone_constants import EMPTY_STRING
from prompts.prompt_util import PromptUtil
from utils.drone_llm_response_util import LLMResponseUtil
from utils.drone_util import format_selective

RESPONSE_FORMAT = "Enclose your answer inside of {}"
REQUIRE_ALL_TAGS = str(uuid.uuid4())


@dataclass
class PromptResponseManager:
    """
    :param response_tag: The tag that the model uses to enclose its answer
    """
    response_tag: Union[str, dict, list] = EMPTY_STRING
    """
    :param response_instructions_format: The format of the instructions included in prompt to tell the model how to respond
    """
    response_instructions_format: str = RESPONSE_FORMAT
    """
    :param id2tag: A dictionary mapping the id of the tag to the tag name in order to fill in the response instructions with the 
                   appropriate tags
    """
    id2tag: Dict = field(default_factory=dict)
    """
    :param include_expected_response: If True, the response instructions will be automatically added to the prompt
    """
    include_response_instructions: bool = True
    """
    :param expected_response_type: A dictionary mapping the tag id to the expected response type for that tag
    """
    expected_response_type: Union[Type, Dict[str, Type]] = field(default_factory=dict)
    """
    :param expected_responses: A dictionary mapping the tag id to the expected responses for that tag
    """
    expected_responses: Union[List, Dict[str, Set]] = field(default_factory=dict)
    """
    :param formatter: A method that takes in the tag id and returns the correct format for the associated response
    """
    value_formatter: Callable = None
    """
    :param default_factory: A method that takes in the tag id and returns a default failure for it if the response parsing fails
    """
    default_factory: Callable = None
    """
    :param required_tag_ids: A set of the tag ids that will throw an exception if not include
    """
    required_tag_ids: Union[Set, str] = field(default_factory=set)
    """
    Formats an entry given its tag and values.
    """
    entry_formatter: Callable[[str, Dict], Any] = None
    """
    Create reverse lookup for tags to their ids after init
    """
    _tag2id: Dict[str, str] = field(init=False, default_factory=dict)
    """
    A list of all response tags in the order they are provided . 
     If parent, children, they are returned in the order:
     p1, c1.1, .. c1.n, p2, c2.1, .. c2.n,... pn, cn.1, .. cn.n
    """
    _all_tag_ids: List[str] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        """
        Converts input to the correct format after init
        :return: None
        """
        if self.response_tag:
            self._init_tag_attrs()
        self.expected_response_type = self._convert2dict(self.expected_response_type)
        self.expected_responses = self._convert2dict(self.expected_responses)
        if self.required_tag_ids == REQUIRE_ALL_TAGS:
            self.required_tag_ids = set(self._all_tag_ids)
        elif not isinstance(self.required_tag_ids, set):
            self.required_tag_ids = {self.required_tag_ids}

    def _convert2dict(self, initial_val: Any) -> Dict:
        """
        Converts a non-dict value to a dictionary mapping tag id to the given value to standardize a param
        :param initial_val: The original value which may not be a dictionary
        :return: A dictionary mapping tag id to a value
        """
        if not isinstance(initial_val, dict):
            return {id_: initial_val for id_ in self._all_tag_ids}
        return initial_val

    def _init_tag_attrs(self) -> None:
        """
        Initializes tag2id and all_tag_ids from the provided response tag and id2tag
        :return: None
        """
        all_tags = []
        if isinstance(self.response_tag, str):
            all_tags.append(self.response_tag)
        elif isinstance(self.response_tag, list):
            all_tags.extend(self.response_tag)
        else:
            for tag, children in self.response_tag.items():
                all_tags.append(tag)
                all_tags.extend(children)
        if not self.id2tag:
            self.id2tag = {tag: tag for tag in all_tags}
        self._tag2id = {tag: id_ for id_, tag in self.id2tag.items()}
        self._all_tag_ids = [self._tag2id[tag] for tag in all_tags]

    def get_all_tag_ids(self) -> List[str]:
        """
        Gets all the response tag ids in the order they are provided .
        If parent, children, they are returned in the order:
        p1, c1.1, .. c1.n, p2, c2.1, .. c2.n,... pn, cn.1, .. cn.n
        :return: All the response tag ids in the order they are provided
        """
        return self._all_tag_ids

    def format_response_instructions(self) -> str:
        """
        Formats the response instructions with the appropriate tags
        :return: The formatted response instructions
        """
        if not self.include_response_instructions:
            return EMPTY_STRING
        args = [PromptUtil.create_xml(tag_name=tag) for tag in self.get_all_tag_ids()]
        kwargs = {id_: PromptUtil.create_xml(tag_name=tag) for id_, tag in self.id2tag.items()}
        return format_selective(self.response_instructions_format, *args, **kwargs)

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parses the response from the model in the expected format for the prompt
        :param response: The model response
        :return: The formatted response
        """
        if not self.response_tag:
            return {}
        output = {}
        if isinstance(self.response_tag, dict):
            for parent, child_tags in self.response_tag.items():
                values = LLMResponseUtil.parse(response, parent, is_nested=True, raise_exception=parent in self.required_tag_ids)
                tags = child_tags + [parent]
                values = [{self._tag2id[c_tag]: val.get(c_tag, None) for c_tag in tags if c_tag in val or c_tag != parent}
                          for val in values]
                output[self._tag2id[parent]] = values
        else:
            tags, _ = self._convert2list(self.response_tag)
            for tag in tags:
                tag_id = self._tag2id[tag]
                parsed = LLMResponseUtil.parse(response, tag, is_nested=False, raise_exception=tag in self.required_tag_ids)
                output[tag_id] = parsed if len(parsed) > 0 else [None]
        formatted_output = self._format_response(output)
        return formatted_output

    def _format_response(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies the appropriate formatting to the response values for each tag
        :param output: Maps tag id to the parsed output from the model
        :return: A mapping of tag id to the formatted output value
        """
        formatted_tags = {}
        for tag, values in output.items():
            values, _ = self._convert2list(values)
            formatted_values = []
            for val in values:
                formatted_val = val
                if isinstance(val, dict):
                    formatted_val = self._format_response(val)
                    if self.entry_formatter:
                        formatted_val = self.entry_formatter(tag, formatted_val)
                    formatted_values.append(formatted_val)
                else:
                    try:
                        formatted_val = self._format_value(tag, formatted_val)
                    except (TypeError, AssertionError, ValueError) as e:
                        print(e)
                        formatted_val = self._format_on_failure(tag, formatted_val, e)
                    if formatted_val is not None:
                        formatted_values.append(formatted_val)
            formatted_tags[tag] = formatted_values
        return formatted_tags

    def _format_value(self, tag: str, orig_val: Any) -> Any:
        """
        Formats a value for a tag
        :param tag: The tag to format the value for
        :param orig_val: The original value
        :return: The formatted value
        """
        assert orig_val is not None, f"{orig_val} is missing {tag}"
        vals2format, orig_vals_is_list = self._convert2list(orig_val)
        formatted = []
        for val in vals2format:
            if isinstance(val, bs4.NavigableString):
                val = str(val)
            if self.value_formatter:
                val = self.value_formatter(tag, val)
            inner_vals, inner_vals_is_list = self._convert2list(val)
            if tag in self.expected_response_type:
                inner_vals = self._convert_to_expected_type(inner_vals, tag, inner_vals_is_list)
            if tag in self.expected_responses:
                inner_vals = self._assert_expected_response(inner_vals, tag, inner_vals_is_list)
            val = inner_vals if inner_vals_is_list else inner_vals.pop()
            if val is not None:
                formatted.append(val)
        formatted_val = formatted if orig_vals_is_list else formatted.pop()
        return formatted_val

    def _assert_expected_response(self, vals2check: List[Any], tag: str, is_list: bool) -> List[Any]:
        """
        Asserts that all values are expected
        :param vals2check: The values to check
        :param tag: The tag used to output values
        :param is_list: True if the response is a list
        :return: The checked values
        """
        checked_values = []
        for v in vals2check:
            val = v
            success = False
            if isinstance(self.expected_responses[tag], range):
                expected_range = sorted(list(self.expected_responses[tag]))
                if expected_range[0] <= v <= expected_range[-1]:
                    success = True
            elif v in self.expected_responses[tag]:
                success = True
            if not success:
                val = self._format_on_failure(tag, v, AssertionError(f"Unexpected value for {tag}"),
                                              no_exception=is_list, return_none_on_fail=is_list)
            if val is not None:
                checked_values.append(val)
        return checked_values

    def _convert_to_expected_type(self, vals2convert: List[Any], tag: str, is_list: bool) -> List[Any]:
        """
        Returns the list of values converted to the expected type
        :param vals2convert: The list of values to convert
        :param tag: The tag used to output values
        :param is_list: If true no exception is thrown if formatting error occurs.
        :return: The list of converted values
        """
        converted = []
        for v in vals2convert:
            try:
                val = self.expected_response_type[tag](v)
            except (ValueError, TypeError) as e:
                val = self._format_on_failure(tag, v, e, no_exception=is_list, return_none_on_fail=is_list)
            if val is not None:
                converted.append(val)
        return converted

    def _format_on_failure(self, tag_id: str, val: Any, e: Union[Exception, str], no_exception: bool = False,
                           return_none_on_fail: bool = False) -> Any:
        """
        Parses the response if it fails in some way, may be overridden in child classes
        :param tag_id: The id of the tag that failed
        :param val: The value of the prompt.
        :param e: The exception causing the failure
        :param no_exception: If True, no exception will be thrown
        :param return_none_on_fail: If True, returns None instead of the origin value
        :return: Default value
        """
        assert no_exception or tag_id not in self.required_tag_ids, f"Missing expected tag {tag_id}"
        print(f"Unexpected response for {tag_id}: {val} - {e}.")
        if self.default_factory:
            return self.default_factory(tag_id, val)
        return val if not return_none_on_fail else None

    @staticmethod
    def _convert2list(orig_val: Any) -> Tuple[List, bool]:
        """
        Converts val to list if not already
        :param orig_val: The original value
        :return: The values as a list and whether it was already a list
        """
        is_list = isinstance(orig_val, list)
        return [orig_val] if not is_list else orig_val, is_list
