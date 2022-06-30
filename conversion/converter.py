import io
import typing
import numpy as np
import pydicom
from PIL import Image


class Converter:
    @staticmethod
    def convert(dcm_decompressed_bytes: typing.BinaryIO) -> bytes:
        im = pydicom.dcmread(dcm_decompressed_bytes, force=True)
        # Convert type to float and reduce it values into [0, 255] size range.
        im = im.pixel_array.astype(float)
        im = (np.maximum(im, 0) / np.amax(im)) * 255
        im = np.uint8(im)
        im = Image.fromarray(im)
        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, 'PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr
