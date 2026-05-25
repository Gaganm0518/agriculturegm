import pytest
from backend.models.prediction import Prediction
from backend.extensions import db
import json

@pytest.fixture
def test_prediction(app, test_user):
    with app.app_context():
        pred = Prediction(
            user_id=test_user,
            prediction_type='crop_recommendation',
            recommended_crop='Wheat',
            confidence_score=95.5,
            raw_output=json.dumps({"input": {}, "info": "test"})
        )
        db.session.add(pred)
        db.session.commit()
        return pred.id

def test_get_history_success(client, user_token, test_prediction):
    res = client.get('/api/history/', headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 200
    assert res.json['success'] is True
    assert len(res.json['data']['history']) > 0
    assert res.json['data']['history'][0]['prediction_type'] == 'crop_recommendation'

def test_get_history_pagination(client, user_token, test_prediction):
    res = client.get('/api/history/?page=1&per_page=1', headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 200
    assert res.json['success'] is True
    assert len(res.json['data']['history']) == 1

def test_delete_history_success(client, user_token, test_prediction):
    res = client.delete(f'/api/history/{test_prediction}', headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 200
    assert res.json['success'] is True

def test_delete_history_not_found(client, user_token):
    res = client.delete('/api/history/99999', headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 404

def test_history_unauthorized(client):
    res = client.get('/api/history/')
    assert res.status_code == 401
