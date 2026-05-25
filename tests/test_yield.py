import pytest
from unittest.mock import patch

@patch('backend.routes.predict.YieldService.predict_yield')
def test_yield_success(mock_predict, client, user_token):
    mock_predict.return_value = 2500.5
    
    res = client.post('/api/predict/yield', json={
        'crop': 'Wheat',
        'season': 'Kharif',
        'region': 'Karnataka',
        'area_ha': 10,
        'rainfall': 150,
        'fertilizer_kg': 50,
        'pesticide_kg': 5
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 200
    assert res.json['success'] is True
    assert 'total_yield_kg' in res.json['data']

@patch('backend.routes.predict.YieldService.predict_yield')
def test_yield_invalid_inputs(mock_predict, client, user_token):
    res = client.post('/api/predict/yield', json={
        'crop': 'Wheat',
        'season': 'Kharif',
        'region': 'Karnataka',
        'area_ha': 'invalid',  # Invalid numeric
        'rainfall': 150,
        'fertilizer_kg': 50,
        'pesticide_kg': 5
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 400

def test_yield_missing_inputs(client, user_token):
    res = client.post('/api/predict/yield', json={
        'crop': 'Wheat'
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 400

@patch('backend.routes.predict.YieldService.predict_yield')
def test_yield_model_unavailable(mock_predict, client, user_token):
    mock_predict.side_effect = RuntimeError('Model unavailable')
    
    res = client.post('/api/predict/yield', json={
        'crop': 'Wheat',
        'season': 'Kharif',
        'region': 'Karnataka',
        'area_ha': 10,
        'rainfall': 150,
        'fertilizer_kg': 50,
        'pesticide_kg': 5
    }, headers={'Authorization': f'Bearer {user_token}'})
    
    assert res.status_code == 500

def test_yield_unauthorized(client):
    res = client.post('/api/predict/yield', json={
        'crop': 'Wheat',
        'season': 'Kharif',
        'region': 'Karnataka',
        'area_ha': 10,
        'rainfall': 150,
        'fertilizer_kg': 50,
        'pesticide_kg': 5
    })
    assert res.status_code == 401

