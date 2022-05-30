import base64
import io
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from conversion.converter import Converter
from compression.decompressor import Decompressor


class Request(BaseModel):
    compression_method: str
    compressed_data: str
    is_encoded: bool


ACCESS_TOKEN_ENV_KEY = 'ACCESS_TOKEN'

# Preparing the environment of the service.
load_dotenv()

security = HTTPBearer()
app = FastAPI()
decompressor = Decompressor()
converter = Converter()


@app.post("/convert")
async def convert(req: Request,
                  credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    if not __valid_credentials(credentials.credentials):
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Invalid access token')
    # Start of the conversion pipeline.
    decompressed_data = __decompress(req)
    converted_data = __convert(decompressed_data)
    encoded_data = __encode(converted_data)
    return {
        'data': encoded_data
    }


def __valid_credentials(credentials: str) -> bool:
    return credentials == os.getenv(ACCESS_TOKEN_ENV_KEY)


def __decompress(req: Request) -> bytes:
    try:
        return Decompressor.decompress(
            req.compressed_data,
            req.compression_method,
            req.is_encoded
        )
    except NotImplementedError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'{req.compression_method} compression is not supported')
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Decompression error: {e}')


def __convert(data: bytes) -> bytes:
    try:
        return Converter.convert(io.BytesIO(data))
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Conversion error: {e}')


def __encode(data: bytes) -> bytes:
    try:
        return base64.b64encode(data)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f'Base64 encoding error: {e}')

