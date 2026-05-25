import pytest
from backend.models.user import User
from backend.extensions import db

def test_admin_dashboard_success(client, admin_token):
    res = client.get('/api/admin/stats', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    assert res.json['success'] is True
    assert 'total_users' in res.json['data']

def test_admin_dashboard_forbidden(client, user_token):
    res = client.get('/api/admin/stats', headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 403
    assert res.json['success'] is False

def test_admin_users_success(client, admin_token):
    res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
    assert res.status_code == 200
    assert res.json['success'] is True
    assert isinstance(res.json['data']['users'], list)

def test_admin_users_forbidden(client, user_token):
    res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 403

def test_admin_dashboard_unauthorized(client):
    res = client.get('/api/admin/stats')
    assert res.status_code == 401
