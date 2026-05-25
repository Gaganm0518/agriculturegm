import pytest
import io
from unittest.mock import patch
from PIL import Image

def _make_test_jpeg():
    """Create a real tiny JPEG image for testing."""
    img = Image.new('RGB', (100, 100), color=(0, 128, 0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

@patch('backend.routes.detect.DiseaseService.predict')
def test_disease_success(mock_predict, client, user_token):
    mock_predict.return_value = {
        "disease_name": "Apple Scab",
        "confidence": 92.5,
        "remedy": "Apply fungicide",
        "symptoms": "Dark spots on leaves",
        "severity": "Medium",
        "affected_crops": ["Apple"],
        "disease_key": "apple_scab"
    }
    
    res = client.post(
        '/api/detect/disease',
        data={'image': (_make_test_jpeg(), 'test.jpg')},
        content_type='multipart/form-data',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    
    assert res.status_code == 200
    assert res.json['success'] is True
    assert res.json['data']['disease'] == 'Apple Scab'

def test_disease_no_image(client, user_token):
    res = client.post(
        '/api/detect/disease',
        data={},
        content_type='multipart/form-data',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert res.status_code == 400

def test_disease_invalid_file_type(client, user_token):
    fake_file = b'This is just a text file, not an image.'
    
    res = client.post(
        '/api/detect/disease',
        data={'image': (io.BytesIO(fake_file), 'test.txt')},
        content_type='multipart/form-data',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert res.status_code == 400

@patch('backend.routes.detect.DiseaseService.predict')
def test_disease_model_unavailable(mock_predict, client, user_token):
    mock_predict.side_effect = RuntimeError('Model unavailable')
    
    res = client.post(
        '/api/detect/disease',
        data={'image': (_make_test_jpeg(), 'test.jpg')},
        content_type='multipart/form-data',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert res.status_code == 500

def test_disease_unauthorized(client):
    res = client.post(
        '/api/detect/disease',
        data={'image': (_make_test_jpeg(), 'test.jpg')},
        content_type='multipart/form-data'
    )
    assert res.status_code == 401
