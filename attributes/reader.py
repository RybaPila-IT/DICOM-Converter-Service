import typing
import pydicom


class AttributesReader:
    """
    Class enabling to read attributes of DICOM image provided as BinaryIO.
    """
    @staticmethod
    def read_pixel_spacing(dcm_decompressed_bytes: typing.BinaryIO) -> list[float]:
        with pydicom.dcmread(dcm_decompressed_bytes, force=True) as im:
            return im.PixelSpacing
