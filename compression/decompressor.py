import base64

from compression.methods.lz_string import LZString


class Decompressor:

    allowed_compression_methods = {
        'lz': lambda: Decompressor.lz_decompress
    }

    @staticmethod
    def decompress(compressed_bytes: str, method: str, is_encoded: bool = True):
        if (decompress_method := Decompressor.allowed_compression_methods.get(method)) is None:
            raise NotImplementedError
        # Decompress the data accordingly to allowed compression method.
        decompressed_data = decompress_method()(compressed_bytes)
        # Perform optional final base64 decoding.
        return decompressed_data \
            if not is_encoded \
            else base64.b64decode(decompressed_data)

    @staticmethod
    def lz_decompress(compressed: str) -> str:
        return LZString.decompressFromBase64(compressed)
