import pytest
from unittest.mock import patch

@patch('backend.routes.recommend.CropService.recommend')
def test_crop_success(mock_recommend, client, user_token):
    mock_recommend.return_value = ("Wheat", 95.5, {"info": "test"})
    
    res = client.post('/api/recommend/crop', json={
        'nitrogen': 50, 'phosphorus': 50, 'potassium': 50,
        'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 200
    assert res.json['success'] is True
    assert res.json['data']['crop'] == 'Wheat'
    assert res.json['data']['confidence'] == 95.5

@patch('backend.routes.recommend.CropService.recommend')
def test_crop_invalid_inputs(mock_recommend, client, user_token):
    res = client.post('/api/recommend/crop', json={
        'nitrogen': -50,  # Invalid negative
        'phosphorus': 50, 'potassium': 50,
        'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 400
    assert res.json['success'] is False

@patch('backend.routes.recommend.CropService.recommend')
def test_crop_missing_inputs(mock_recommend, client, user_token):
    res = client.post('/api/recommend/crop', json={
        'nitrogen': 50
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 400

@patch('backend.routes.recommend.CropService.recommend')
def test_crop_model_unavailable(mock_recommend, client, user_token):
    mock_recommend.side_effect = RuntimeError('Model unavailable')
    
    res = client.post('/api/recommend/crop', json={
        'nitrogen': 50, 'phosphorus': 50, 'potassium': 50,
        'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 500

def test_crop_unauthorized(client):
    res = client.post('/api/recommend/crop', json={
        'nitrogen': 50, 'phosphorus': 50, 'potassium': 50,
        'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100
    })
    assert res.status_code == 401
