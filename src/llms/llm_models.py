from enum import Enum


class OpenAIModel(Enum):
    """
    The supported OpenAI models available to LLM manager.
    """
    GPT4 = "gpt-4"
    GPT3 = "gpt-3.5-turbo"
