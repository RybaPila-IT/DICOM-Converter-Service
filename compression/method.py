from abc import ABC, abstractmethod


class Method(ABC):
    @staticmethod
    @abstractmethod
    def decompress(compressed: str) -> str:
        """
        Abstract method allowing to decompress the string.

        It is the base method for all the implementations
        of decompression algorithms.

        :param compressed: string containing compressed data.
        :return: string being the result of decompression.
        """
        pass
