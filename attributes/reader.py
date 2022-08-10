import typing
import pydicom


class AttributesReader:
    """
    Class enabling to read attributes of DICOM image provided as BinaryIO.
    """
    @staticmethod
    def read_attributes(dcm_decompressed_bytes: typing.BinaryIO) -> dict:
        with pydicom.dcmread(dcm_decompressed_bytes, force=True) as im:
            return {
                'pixel_spacing': im.PixelSpacing[0],
                'image_size': [im.Columns, im.Rows]
            }
