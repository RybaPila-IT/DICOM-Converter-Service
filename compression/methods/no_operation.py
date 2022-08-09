from compression.method import Method


class NoCompression(Method):
    @staticmethod
    def decompress(compressed: str) -> str:
        """
        Implementation of the no decompression algorithm.

        :param compressed: string of compressed bytes.
        :return: string containing the uncompressed bytes (same as the input).
        """
        return compressed
