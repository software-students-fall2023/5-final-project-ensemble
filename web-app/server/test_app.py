import pytest
from app import app as flask_app
from flask import session, url_for, redirect
from unittest.mock import patch
import mongomock
from user.authentication import UserAuthentication
from user.user import User
from pymongo.mongo_client import MongoClient
from passlib.hash import pbkdf2_sha256

# Mock MongoDB Client
class MockMongoClient(MongoClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = mongomock.MongoClient().db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = flask_app
    app.config.update({
        "TESTING": True,
        "MONGO_URI": "mongomock://localhost"
    })
    with app.app_context():
        app.mongo = MockMongoClient()
        flask_app.mongo = app.mongo

    yield app

@pytest.fixture   
def auth(client):
    def login(username='test', password='test'):
        return client.post('/', data={'username': username, 'password': password})
    
    def logout():
        return client.get('/signout')

    return {'login': login, 'logout': logout}

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

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b"register" in response.data

def test_user_registration(client):
    user_data = {
        "username": "new_user",
        "password": "new_password",
        "name": "New User"
    }

    with patch('user.authentication.UserAuthentication') as MockAuthClass:
        instance = MockAuthClass.return_value
        instance.sign_up.return_value = ('', 200) 

        response = client.post('/register', data=user_data)
        assert response.status_code == 200

def test_register_and_login(client, auth):
    with patch('pymongo.collection.Collection.find_one', mongomock.MongoClient().db.users.find_one), \
         patch('pymongo.collection.Collection.insert_one', mongomock.MongoClient().db.users.insert_one):

        new_user_data = {
            "username": "newuser",
            "password": "newpassword",
            "name": "New User"
        }
        response = client.post('/register', data=new_user_data)
        assert response.status_code in [200, 302]

        login_response = auth['login'](new_user_data['username'], new_user_data['password'])
        assert login_response.status_code in [200, 302, 401]

def test_add_sku_page(client):
    response = client.get('/add_sku')
    assert response.status_code == 302
    assert b'Redirecting' in response.data

def test_add_sku(client, auth):
    with patch('pymongo.collection.Collection.find_one', return_value={'_id': 'mocked_user_id', 'username': 'username', 'password': 'dummy_hashed_password'}), \
         patch('passlib.hash.pbkdf2_sha256.verify', return_value=True):
        auth_response = auth['login']('username', 'password')
        assert auth_response.status_code in [200, 302]

        with patch('pymongo.collection.Collection.find_one', return_value=None), \
             patch('pymongo.collection.Collection.insert_one') as mock_insert:
            
            sku_data = {
                "sku": "12345",
                "product_name": "Test Product",
                "stock": "50"
            }
            response = client.post('/add_sku', data=sku_data)
            assert response.status_code == 302

            mock_insert.assert_called_once_with({
                "sku": "12345",
                "product_name": "Test Product",
                "stock": "50",
                "user_id": "mocked_user_id"
            })

def test_update_sku(client, auth):
    mock_user = {'_id': 'mocked_user_id', 'username': 'username', 'password': 'dummy_hashed_password'}
    mock_sku = {'sku': '123456', 'product_name': 'Test Product', 'stock': '50', 'user_id': 'mocked_user_id'}
    updated_data = {
        "sku": '123456',
        "product_name": "Updated Product",
        "stock": "60"
    }
    
    with patch('pymongo.collection.Collection.find_one', side_effect=[mock_user, mock_sku, None]), \
         patch('passlib.hash.pbkdf2_sha256.verify', return_value=True), \
         patch('pymongo.collection.Collection.find_one_and_update') as mock_update:
        
        auth_response = auth['login']('username', 'password')
        assert auth_response.status_code in [200, 302]

        response = client.post(f'/sku/{mock_sku["sku"]}/edit_sku', data=updated_data)
        assert response.status_code == 302
        mock_update.assert_called_with(
            {"sku": mock_sku["sku"], "user_id": mock_user["_id"]},
            {'$set': updated_data}
        )