import pytest
from unittest.mock import patch

@patch('backend.routes.recommend.FertilizerService.recommend')
def test_fertilizer_success(mock_recommend, client, user_token):
    mock_recommend.return_value = ("Urea", 95.5, {"info": "test"})
    
    res = client.post('/api/recommend/fertilizer', json={
        'nitrogen': 50, 'phosphorus': 50, 'potassium': 50,
        'temperature': 25, 'humidity': 60, 'moisture': 40,
        'soil_type': 'Sandy', 'crop': 'Wheat'
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 200
    assert res.json['success'] is True
    assert res.json['data']['fertilizer'] == 'Urea'

@patch('backend.routes.recommend.FertilizerService.recommend')
def test_fertilizer_invalid_inputs(mock_recommend, client, user_token):
    res = client.post('/api/recommend/fertilizer', json={
        'nitrogen': -50,  # Invalid
        'phosphorus': 50, 'potassium': 50,
        'temperature': 25, 'humidity': 60, 'moisture': 40,
        'soil_type': 'Sandy', 'crop': 'Wheat'
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 400

def test_fertilizer_missing_inputs(client, user_token):
    res = client.post('/api/recommend/fertilizer', json={
        'nitrogen': 50
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 400

@patch('backend.routes.recommend.FertilizerService.recommend')
def test_fertilizer_model_unavailable(mock_recommend, client, user_token):
    mock_recommend.side_effect = RuntimeError('Model unavailable')
    
    res = client.post('/api/recommend/fertilizer', json={
        'nitrogen': 50, 'phosphorus': 50, 'potassium': 50,
        'temperature': 25, 'humidity': 60, 'moisture': 40,
        'soil_type': 'Sandy', 'crop': 'Wheat'
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 500

def test_fertilizer_unauthorized(client):
    res = client.post('/api/recommend/fertilizer', json={
        'nitrogen': 50, 'phosphorus': 50, 'potassium': 50,
        'temperature': 25, 'humidity': 60, 'moisture': 40,
        'soil_type': 'Sandy', 'crop': 'Wheat'
    })
    assert res.status_code == 401
