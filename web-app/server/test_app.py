import pytest
from app import app as flask_app
from flask import session
import mongomock
from user.authentication import UserAuthentication
from user.user import User
from pymongo.mongo_client import MongoClient

# Mock MongoDB Client
class MockMongoClient(MongoClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = mongomock.MongoClient().db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a Flask application configured for testing
    app = flask_app
    app.config.update({
        "TESTING": True,
        "MONGO_URI": "mongomock://localhost"
    })

    # Use the mock MongoDB client
    with app.app_context():
        app.mongo = MockMongoClient()
        flask_app.mongo = app.mongo  # Ensure the app uses the mock client

    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def test_home(client):
    with client:
        response = client.get('/home/')
        assert response.status_code == 302

def test_search(client):
    with client:
        response = client.get('/search?query=test')
        assert response.status_code == 302

def test_add_sku(client):
    with client:
        response = client.post('/add_sku', data=dict(
            sku='123', product_name='Test Product', stock='10'
        ))
        assert response.status_code == 302

def test_sku_details(client):
    with client:
        response = client.get('/sku/123')
        assert response.status_code == 302

def test_add_log(client):
    with client:
        response = client.post('/add_log', data=dict(
            sku='123', action='increase', quantity='5'
        ))
        assert response.status_code == 302

def test_edit_sku(client):
    with client:
        response = client.post('/sku/123/edit_sku', data=dict(
            sku='123', product_name='Updated Test Product', stock='15'
        ))
        assert response.status_code == 302

def test_delete_sku(client):
    with client:
        response = client.get('/sku/123/delete_sku')
        assert response.status_code == 302

def test_confirm_delete_sku(client):
    with client:
        response = client.post('/sku/123/confirm_delete_sku')
        assert response.status_code == 302
