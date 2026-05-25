import os
import pytest
from datetime import timedelta
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'MAIL_SUPPRESS_SEND': True,
        'RATELIMIT_ENABLED': False,
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=15)
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(name="Test User", email="test@example.com", role="user")
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()
        # Return a detached instance or fetch fresh when needed
        return user.id

@pytest.fixture
def admin_user(app):
    with app.app_context():
        admin = User(name="Admin User", email="admin@example.com", role="admin")
        admin.set_password("Admin123!")
        db.session.add(admin)
        db.session.commit()
        return admin.id

@pytest.fixture
def user_token(app, test_user):
    with app.app_context():
        return create_access_token(identity=str(test_user))

@pytest.fixture
def admin_token(app, admin_user):
    with app.app_context():
        return create_access_token(identity=str(admin_user))
