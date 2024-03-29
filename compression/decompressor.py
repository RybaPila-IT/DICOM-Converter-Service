import base64

from compression.methods.lzw import LZWDecompress
from compression.methods.no_operation import NoCompression


class Decompressor:
    """
    Class responsible for decompressing the submitted image bytes.

    Since DICOM data is compressed in order to reduce it size (from MB to KB magnitude)
    the decompression of the submitted data must be performed prior to
    conversion method.

    Decompressor performs also base64 decoding if the submitted data was originally
    encoded in base64 (DICOM data encoded in base64 before compression).

    IMPORTANT:  Data after compression must be encoded in base64 and decompression methods
                should take this into account.
    """
    allowed_compression_methods = {
        'none': NoCompression,
        'lz': LZWDecompress
    }

    @staticmethod
    def decompress(compressed: str, method: str, is_encoded: bool = True):
        if (decompress_method := Decompressor.allowed_compression_methods.get(method)) is None:
            raise NotImplementedError
        # Decompress the data accordingly to allowed compression method.
        decompressed_data = decompress_method.decompress(compressed)
        # Perform optional final base64 decoding.
        return decompressed_data.encode() \
            if not is_encoded \
            else base64.b64decode(decompressed_data)
