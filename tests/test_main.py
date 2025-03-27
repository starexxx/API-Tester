import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Starexx API Tester" in response.data

def test_api_request(client):
    test_data = {
        "url": "https://jsonplaceholder.typicode.com/posts/1",
        "method": "GET",
        "headers": {},
        "body": ""
    }
    
    response = client.post('/send-request', 
                         data=json.dumps(test_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'response' in response_data
    assert 'status' in response_data['response']

def test_history_endpoint(client):
    """Test history endpoint returns data"""
    response = client.get('/get-history')
    assert response.status_code == 200
    assert isinstance(json.loads(response.data), list)

def test_invalid_request(client):
    """Test invalid API request handling"""
    response = client.post('/send-request', 
                         data=json.dumps({"bad": "data"}),
                         content_type='application/json')
    assert response.status_code == 500
