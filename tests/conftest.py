# tests/conftest.py
import pytest
from app.app import app as flask_app

@pytest.fixture(scope="session")
def app():
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        WTF_CSRF_ENABLED=False,   # unit + most integration tests
    )
    return flask_app

@pytest.fixture()
def client(app):
    with app.test_client() as c:
        yield c

@pytest.fixture()
def logged_in_client(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1234
    return client
