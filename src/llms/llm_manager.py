from typing import TypeVar

import openai

from llms.llm_models import OpenAIModel

AIObject = TypeVar("AIObject")


class LLMManager:
    """
    Interface for all AI utility classes.
    """

    @staticmethod
    def make_completion(prompt: str, temperature: float = 0, model: OpenAIModel = OpenAIModel.GPT4) -> AIObject:
        """
        Makes a request to completion a model
        :param prompt: The prompt to make completion for.
        :param temperature: The temperature to run the model at.
        :param model: The OpenAI model to use.
        :return: The response from open AI.
        """
        assert isinstance(model, OpenAIModel), f"Expected OpenAIModel to be passed in but got {model}."
        params = {
            "temperature": temperature,
            "model": model.value,
            "messages": [{"role": "user", "content": prompt}]}
        res = openai.ChatCompletion.create(**params)
        res_text = res.choices[0]["message"]["content"]
        return res_text
