import ast
import logging
import re
import string
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from core.drone_constants import COMMA, EMPTY_STRING, L_BRACKET, R_BRACKET


def read_file(file_path: str, raise_exception: bool = True) -> Optional[str]:
    """
    Reads file at given path if exists.
    :param file_path: Path of the file to read.
    :param raise_exception: If True, raises an exception if reading fails
    :return: The content of the file.
    """
    try:
        with open(file_path) as file:
            file_content = file.read()
            return file_content
    except Exception as e:
        logging.exception(f"Failed reading file: {file_path}")
        if raise_exception:
            raise e
        return None


def parse_coordinates(r: str, as_list: bool = True, alpha_format: bool = False) -> Union[List, Tuple]:
    """
    Parses a list of coordinates in string form (e.g. := (1,1), (2,1) or [(1,1), (2,1)]
    :param r: The text to convert.
    :param as_list: Whether the result should be converted into a list or left as is.
    :return: The parsed data.
    """
    if not alpha_format:
        parsed_data = ast.literal_eval(r)
        if as_list:
            parsed_data = [d for d in parsed_data]
    else:
        r = r.replace(L_BRACKET, EMPTY_STRING).replace(R_BRACKET, EMPTY_STRING)
        coordinates = r.split(COMMA)
        parsed_data = to_numeric(coordinates)
    return parsed_data


def to_numeric(cells: List[str], starting_index: int = 1) -> List[Tuple]:
    """
    Translates alphabetical coordinates (A1) to numeric ones (1,1).
    :param cells: The cells to convert.
    :param starting_index: The starting index of the grid.
    :return: List of coordinates.
    """
    block_coordinates = []
    for b in cells:
        b = b.strip()
        block_x = int(b[1:])
        block_y = string.ascii_uppercase.index(b[0]) + starting_index
        block_coordinate = (block_x, block_y)
        block_coordinates.append(block_coordinate)
    return block_coordinates


def format_selective(string, *args: object, **kwargs: object) -> str:
    """
    A replacement for the string format to allow the formatting of only selective fields
    :param string: The string to format
    :param args: Ordered params to format the prompt with
    :param kwargs: Key, value pairs to format the prompt with
    :return: The formatted str
    """
    if not args and not kwargs:
        return string
    formatting_fields = re.findall(r'\{(\w*)\}', string)
    if not formatting_fields:
        return string
    updated_args = [arg for arg in args]
    updated_kwargs = {}
    for i, field in enumerate(formatting_fields):
        replacement = '{%s}' % field
        if field:
            if field in kwargs:
                updated_kwargs[field] = kwargs[field]
            else:
                updated_kwargs[field] = replacement
        if not field and i >= len(updated_args):
            updated_args.append(replacement)
    try:
        string = string.format(*updated_args, **updated_kwargs)
    except Exception as e:
        print(str(e))
        print(f"Unable to format {string} with args={updated_args} and kwargs={updated_kwargs}")
    return string


def get_kwarg_values(kwargs: Dict, pop: bool = False, **keys) -> Any:
    """
    Gets all kwargs values for the given keys
    :param kwargs: The kwargs to get values from
    :param pop: If True, removes the values from the kwargs
    :param keys: The keys to retrieve from the kwargs along with a default value
    :return: Return the value for each key
    """
    if not keys:
        return
    values = []
    for key, default in keys.items():
        value = kwargs.get(key, default)
        values.append(value)
        if pop and key in kwargs:
            kwargs.pop(key)
    return values[0] if len(values) == 1 else values


def convert_to_dict(dataclass_: dataclass, **val2replace) -> Dict:
    """
    Converts the dataclass to a dictionary
    :param dataclass_: The dataclass to convert
    :param val2replace: Dictionary mapping attr to the new value for it
    :return: the dataclass as a dictionary
    """
    args = {k: v for k, v in vars(dataclass_).items() if k not in val2replace.keys()
            and not is_function(v) and not k.startswith("__")}
    args.update(val2replace)
    return args


def is_function(unknown_obj) -> bool:
    """
    Returns true if the object is a function else false
    :param unknown_obj: The obj to test if its a function
    :return: True if it is a function else False
    """
    return type(unknown_obj).__name__ in ["function", "builtin_function_or_method", "method", "classmethod",
                                          "staticmethod", "abstractmethod"]
