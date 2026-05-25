"""
Unit tests for the Crop Recommendation API.
"""

import pytest
from unittest.mock import patch
from flask_jwt_extended import create_access_token

def test_crop_recommendation_success(client, app):
    """Test successful crop recommendation."""
    # Generate mock token
    with app.app_context():
        access_token = create_access_token(identity="1")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 20.5,
        "humidity": 82,
        "ph": 6.5,
        "rainfall": 202
    }

    # Mock the ML service to avoid actually loading models during tests
    with patch('backend.services.crop_service.CropService.recommend') as mock_recommend:
        mock_recommend.return_value = ("rice", 97.5, {
            "season": "Kharif",
            "water_needs": "High",
            "growing_tips": "Needs standing water."
        })

        response = client.post('/api/recommend/crop', json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['crop'] == "Rice"
        assert data['data']['confidence'] == 97.5
        assert "prediction_id" in data['data']
        assert mock_recommend.called

def test_crop_recommendation_missing_fields(client, app):
    """Test crop recommendation with missing input fields."""
    with app.app_context():
        access_token = create_access_token(identity="1")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Missing 'ph' and 'rainfall'
    payload = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 20.5,
        "humidity": 82
    }

    response = client.post('/api/recommend/crop', json=payload, headers=headers)
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert "Missing required field" in data['error']

def test_crop_recommendation_invalid_range(client, app):
    """Test crop recommendation with unrealistic numeric values."""
    with app.app_context():
        access_token = create_access_token(identity="1")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "nitrogen": 90,
        "phosphorus": 42,
        "potassium": 43,
        "temperature": 150.0,  # Invalid temp (range 0-60)
        "humidity": 82,
        "ph": 6.5,
        "rainfall": 202
    }

    response = client.post('/api/recommend/crop', json=payload, headers=headers)
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert "Temperature must be 0-60." in data['error']
