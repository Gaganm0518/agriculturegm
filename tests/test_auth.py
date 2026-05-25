import pytest
from backend.models.user import User
from backend.extensions import db
import json

def test_register_success(client):
    res = client.post('/api/auth/register', json={
        'name': 'New User',
        'email': 'new@example.com',
        'password': 'Password123!'
    })
    assert res.status_code == 201
    assert res.json['success'] is True
    assert 'access_token' in res.json['data']

def test_register_duplicate_email(client, test_user):
    res = client.post('/api/auth/register', json={
        'name': 'Another User',
        'email': 'test@example.com',  # Existing email
        'password': 'Password123!'
    })
    assert res.status_code == 409
    assert res.json['success'] is False

def test_register_weak_password(client):
    res = client.post('/api/auth/register', json={
        'name': 'Weak User',
        'email': 'weak@example.com',
        'password': 'weak'
    })
    assert res.status_code == 400

def test_login_success(client, test_user):
    res = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'Password123!'
    })
    assert res.status_code == 200
    assert res.json['success'] is True
    assert 'access_token' in res.json['data']

def test_login_invalid_password(client, test_user):
    res = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'WrongPassword123!'
    })
    assert res.status_code == 401
    assert res.json['success'] is False

def test_get_me_success(client, user_token):
    res = client.get('/api/auth/me', headers={'Authorization': f'Bearer {user_token}'})
    assert res.status_code == 200
    assert res.json['success'] is True
    assert res.json['data']['user']['email'] == 'test@example.com'

def test_get_me_unauthorized(client):
    res = client.get('/api/auth/me')
    assert res.status_code == 401
