import base64
import io
import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from conversion.converter import Converter
from compression.decompressor import Decompressor
from attributes.reader import AttributesReader

# Setting up the logger.
logging.basicConfig(level=logging.INFO)


class Request(BaseModel):
    compression: str
    data: str
    encoded: bool


ACCESS_TOKEN_ENV_KEY = 'ACCESS_TOKEN'

# Preparing the environment of the service.
load_dotenv()

security = HTTPBearer()
app = FastAPI()
decompressor = Decompressor()
converter = Converter()
attributes_reader = AttributesReader()


@app.get("/")
async def main() -> dict:
    return {
        'message': 'Welcome to DICOM Converter Service'
    }


@app.post('/convert')
async def convert(req: Request,
                  credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    if not __valid_credentials(credentials.credentials):
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Invalid access token')
    # Start of the conversion pipeline.
    decompressed_data = __decompress(req)
    converted_data = __convert(decompressed_data)
    encoded_data = __encode(converted_data)
    # Read the pixel spacing attribute, necessary by some micro-services.
    attributes = __read_attributes(decompressed_data)
    # Finish of the endpoint.
    logging.info('Successfully converted submitted image and fetched its attributes')
    return {
        'image': encoded_data,
        'attributes': attributes
    }


def __valid_credentials(credentials: str) -> bool:
    return credentials == os.getenv(ACCESS_TOKEN_ENV_KEY)


def __decompress(req: Request) -> bytes:
    try:
        return Decompressor.decompress(
            req.data,
            req.compression,
            req.encoded
        )
    except NotImplementedError:
        logging.error(f'Decompress: {req.compression} compression is not supported')
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'{req.compression} compression is not supported')
    except Exception as e:
        logging.error(f'Decompress error: {e}')
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 'Internal decompression error occurred')


def __convert(data: bytes) -> bytes:
    try:
        return Converter.convert(io.BytesIO(data))
    except Exception as e:
        logging.error(f'Conversion error: {e}')
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 'Internal conversion error occurred')


def __encode(data: bytes) -> bytes:
    try:
        return base64.b64encode(data)
    except Exception as e:
        logging.error(f'Encoding error: {e}')
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 'Internal error while encoding the result occurred')


def __read_attributes(data: bytes) -> dict:
    try:
        return {
            'pixel_spacing': AttributesReader.read_pixel_spacing(io.BytesIO(data))
        }
    except Exception as e:
        logging.error(f'Reading attributes error: {e}')
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Error while reading DICOM attributes occurred')
