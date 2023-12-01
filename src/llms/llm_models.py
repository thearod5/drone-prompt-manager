from enum import Enum


class OpenAIModel(Enum):
    """
    The supported OpenAI models available to LLM manager.
    """
    GPT4 = "gpt-4"
    GPT3 = "gpt-3.5-turbo-1106"
    _token_map = {
        GPT3: 4096,
        GPT4: 8192
    }

    def get_max_tokens(self) -> int:
        """
        Returns the max number of tokens for given model.
        :param model: The model to return max tokens for.
        :return: Number of max tokens.
        """
        return self._token_map.value[self.value]
