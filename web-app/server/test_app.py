
import pytest
from app import app as flask_app
from unittest.mock import MagicMock

@pytest.fixture
def flask_app_fixture():
    """Provides a testing app fixture."""
    flask_app.config["TESTING"] = True
    flask_app.secret_key = "testsecret"
    flask_app.config["MONGO_URI"] = "mongodb://localhost:27017/test_db"  
    return flask_app

@pytest.fixture
def client_fixture(flask_app_fixture):
    """Provides a testing client fixture."""
    with flask_app_fixture.test_client() as testing_client:
        yield testing_client

def test_login(client_fixture):
    """Test login functionality."""
    response = client_fixture.post('/login', data={'username': 'test', 'password': 'test'})
    assert response.status_code == 404  



def test_add_sku(client_fixture):
    """Test adding a new SKU."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})  # Mock login
    response = client_fixture.post('/add_sku', data={'sku': '12345', 'product_name': 'Test Product', 'stock': '10'})
    assert response.status_code in [200, 302]  

def test_signout(client_fixture):
    """Test signout functionality."""
    response = client_fixture.get('/signout')
    assert response.status_code in [302, 200]  

def test_sku_details(client_fixture):
    """Test SKU details page."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})  # Mock login
    response = client_fixture.get('/sku/12345')  
    # If SKU is not found
    assert response.status_code == 302  

def test_add_log(client_fixture):
    """Test adding a log entry."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})  # Mock login
    response = client_fixture.post('/add_log', data={'sku': '12345', 'action': 'increase', 'quantity': '5'})
    assert response.status_code in [200, 302]  

def test_edit_sku(client_fixture):
    """Test editing an SKU."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})  # Mock login
    response = client_fixture.post('/sku/12345/edit_sku', data={'sku': '12345', 'product_name': 'Updated Product', 'stock': '15'})
    assert response.status_code in [200, 302]

def test_delete_sku(client_fixture):
    """Test deleting an SKU."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})  # Mock login
    response = client_fixture.post('/sku/12345/confirm_delete_sku')
    assert response.status_code in [200, 302]  


def test_add_duplicate_sku(client_fixture):
    """Test adding a SKU that already exists."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})
    # Add a SKU
    client_fixture.post('/add_sku', data={'sku': '12345', 'product_name': 'Product', 'stock': '10'})
    # Attempt to add the same SKU again
    response = client_fixture.post('/add_sku', data={'sku': '12345', 'product_name': 'Product', 'stock': '10'})
    assert response.status_code == 302  


def test_edit_nonexistent_sku(client_fixture):
    """Test editing a non-existing SKU."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})
    response = client_fixture.post('/sku/nonexistent_sku/edit_sku', data={'sku': '54321', 'product_name': 'New Product', 'stock': '20'})
    assert response.status_code == 302  




def test_search_functionality(client_fixture):

    # Test search by SKU
    response = client_fixture.get('/search', query_string={'query': '12345'})
    assert response.status_code == 302  

    # Test search by product name
    response = client_fixture.get('/search', query_string={'query': 'Product Name'})
    assert response.status_code == 302  


def test_add_existing_sku(client_fixture):
    """Test adding a SKU that already exists."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})
    # Setup: Add a SKU first
    client_fixture.post('/add_sku', data={'sku': '12345', 'product_name': 'Existing Product', 'stock': '10'})
    # Test adding the same SKU again
    response = client_fixture.post('/add_sku', data={'sku': '12345', 'product_name': 'Duplicate Product', 'stock': '15'})
    assert response.status_code == 302  # Assuming redirection on failure due to existing SKU


def test_edit_sku_invalid_format(client_fixture):
    """Test editing a SKU with invalid SKU format."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})
    # Setup: Add a SKU first
    client_fixture.post('/add_sku', data={'sku': '12345', 'product_name': 'Some Product', 'stock': '10'})
    # Test editing the SKU with invalid format
    response = client_fixture.post('/sku/12345/edit_sku', data={'sku': 'invalid_sku', 'product_name': 'Updated Product', 'stock': '20'})
    assert response.status_code == 302  # Assuming redirection on invalid SKU format


def test_delete_sku_and_access(client_fixture):
    """Test deleting a SKU and then attempting to access it."""
    client_fixture.post('/login', data={'username': 'test', 'password': 'test'})
    # Setup: Add a SKU first
    client_fixture.post('/add_sku', data={'sku': '12345', 'product_name': 'Delete Me', 'stock': '5'})
    # Delete the SKU
    client_fixture.post('/sku/12345/confirm_delete_sku')
    # Attempt to access the deleted SKU's details page
    response = client_fixture.get('/sku/12345')
    assert response.status_code == 302  

