import pytest
from app import app as flask_app

@pytest.fixture()
def app():
    flask_app.config.update({
        'TESTING': True
    })

    yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_index(client):
    assert client.get('/').status_code == 302
    assert client.get('/', follow_redirects=True).request.path == '/login'

def test_login(client):
    assert client.get('/login').status_code == 200

def test_static(client):
    assert client.get('/static/bootstrap.bundle.min.js').status_code == 200
    assert client.get('/static/bootstrap.min.css').status_code == 200

def test_register(client):
    assert client.get('/register').status_code == 200

