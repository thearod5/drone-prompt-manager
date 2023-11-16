from typing import List


class ListUtil:
    @staticmethod
    def flatten(list_: List[List]) -> List:
        """
        Flattens list of lists into single list.
        :param list_: List containing lists as elements.
        :return: List containing all sub-elements.
        """
        return [item for sublist in list_ for item in sublist]

    @staticmethod
    def batch(iterable: List, n: int = 1):
        """
        Creates batches of constant size except for possible the last batch.
        :param iterable: The iterable containing items to batch.
        :param n: The batch size.
        :return: List of batches
        """
        iterable_len = len(iterable)
        batches = []
        for ndx in range(0, iterable_len, n):
            batches.append(iterable[ndx:min(ndx + n, iterable_len)])
        return batches
