import os
from typing import TypeVar

import openai
from dotenv import load_dotenv

from llms.llm_models import OpenAIModel

AIObject = TypeVar("AIObject")

load_dotenv()
OPEN_AI_ORG = os.environ["OPEN_AI_ORG"]
OPEN_AI_KEY = os.environ["OPEN_AI_KEY"]

assert OPEN_AI_ORG and OPEN_AI_KEY, f"Must supply value for {f'{OPEN_AI_ORG=}'.split('=')[0]} " \
                                    f"and {f'{OPEN_AI_KEY=}'.split('=')[0]} in .env"
openai.organization = OPEN_AI_ORG
openai.api_key = OPEN_AI_KEY


class LLMManager:
    """
    Interface for all AI utility classes.
    """

    @staticmethod
    def make_completion(prompt: str, temperature: float = 0, model: OpenAIModel = OpenAIModel.GPT3) -> AIObject:
        """
        Makes a request to completion a model
        :param prompt: The prompt to make completion for.
        :param temperature: The temperature to run the model at.
        :param model: The OpenAI model to use.
        :return: The response from open AI.
        """

        assert isinstance(model, OpenAIModel), f"Expected OpenAIModel to be passed in but got {model}."
        max_tokens = model.get_max_tokens()
        params = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "model": model.value,
            "messages": [{"role": "user", "content": prompt}]}
        res = openai.ChatCompletion.create(**params)
        res_text = res.choices[0]["message"]["content"]
        return res_text
