import json
import os

from fastapi.testclient import TestClient
from fastapi import status
from main import app, ACCESS_TOKEN_ENV_KEY


main_url = '/'
convert_url = '/convert'
access_token = 'access_token'
client = TestClient(app)

os.environ[ACCESS_TOKEN_ENV_KEY] = access_token


def test_main_request():
    resp = client.get(url=main_url)
    resp_body = json.loads(resp.content.decode())

    assert resp.status_code == status.HTTP_200_OK
    assert resp_body['message'] is not None


def test_unauthorized_request():
    resp = client.post(
        url=convert_url,
        json={
            'encoded': True,
            'compression': 'lz',
            'image': 'HelloWorld!'
        }
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_invalid_access_token_request():
    resp = client.post(
        url=convert_url,
        headers={
            'Authorization': 'Bearer invalid_token'
        },
        json={
            'encoded': True,
            'compression': 'lz',
            'image': 'HelloWorld!'
        }
    )

    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_invalid_compressed_data_request():
    resp = client.post(
        url=convert_url,
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            'encoded': True,
            'compression': 'lz',
            'image': 'HelloWorld'
        }
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_invalid_compression_method_request():
    with open('test/data/valid_base64_lz_compressed_dcm.txt') as f:
        data = f.read()

    resp = client.post(
        url=convert_url,
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            'encoded': True,
            'compression': 'unknown',
            'image': data
        }
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_invalid_image_bytes_request():
    resp = client.post(
        url=convert_url,
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            'encoded': False,
            'compression': 'none',
            'image': 'HelloWorld'
        }
    )

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_valid_request():
    with open('test/data/valid_base64_lz_compressed_dcm.txt') as f:
        data = f.read()

    resp = client.post(
        url=convert_url,
        headers={
            'Authorization': f'Bearer {access_token}'
        },
        json={
            'encoded': True,
            'compression': 'lz',
            'image': data
        }
    )
    resp_body = json.loads(resp.content.decode())

    assert resp.status_code == status.HTTP_200_OK
    assert resp_body.get('photo') is not None
    assert resp_body.get('attributes') is not None
    assert resp_body.get('attributes').get('pixel_spacing') is not None
    assert resp_body.get('attributes').get('image_size') is not None
