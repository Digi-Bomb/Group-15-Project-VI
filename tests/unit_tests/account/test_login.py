# tests/account/test_login.py
from unittest.mock import MagicMock, patch

def test_login_get_200(client):
    resp = client.get("/login")
    assert resp.status_code == 200

def test_login_post_success_sets_session_and_redirects(client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = True
    fake_form.username.data = "bob"
    fake_form.password.data = "Passw0rd!"

    mock_reader = MagicMock()
    mock_reader.validate_user_information.return_value = (True, "Successful Login")
    mock_reader.get_ruid_by_username.return_value = 777

    with patch("app.account.routes.LoginForm", return_value=fake_form), \
         patch("app.account.routes.DatabaseConnection"), \
         patch("app.account.routes.DatabaseReadingServices", return_value=mock_reader):

        resp = client.post("/login", data={})
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/")

        with client.session_transaction() as sess:
            assert sess["user_id"] == 777

def test_login_wrong_password_flashes_and_no_session(client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = True
    fake_form.username.data = "bob"
    fake_form.password.data = "wrong"

    mock_reader = MagicMock()
    mock_reader.validate_user_information.return_value = (False, "Incorrect Login Information")

    with patch("app.account.routes.LoginForm", return_value=fake_form), \
         patch("app.account.routes.DatabaseConnection"), \
         patch("app.account.routes.DatabaseReadingServices", return_value=mock_reader):

        resp = client.post("/login", data={}, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Invalid username or password" in resp.data

        with client.session_transaction() as sess:
            assert "user_id" not in sess

def test_login_db_down_runtimeerror(client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = True
    fake_form.username.data = "bob"
    fake_form.password.data = "Passw0rd!"

    mock_reader = MagicMock()
    mock_reader.validate_user_information.side_effect = RuntimeError("db offline")

    with patch("app.account.routes.LoginForm", return_value=fake_form), \
         patch("app.account.routes.DatabaseConnection"), \
         patch("app.account.routes.DatabaseReadingServices", return_value=mock_reader):

        resp = client.post("/login", data={}, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Login temporarily unavailable" in resp.data

def test_login_userid_lookup_fails(client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = True
    fake_form.username.data = "bob"
    fake_form.password.data = "Passw0rd!"

    mock_reader = MagicMock()
    mock_reader.validate_user_information.return_value = (True, "Successful Login")
    mock_reader.get_ruid_by_username.return_value = None

    with patch("app.account.routes.LoginForm", return_value=fake_form), \
         patch("app.account.routes.DatabaseConnection"), \
         patch("app.account.routes.DatabaseReadingServices", return_value=mock_reader):

        resp = client.post("/login", data={}, follow_redirects=True)
        # Depending on your code, you may redirect or render with an error.
        # This asserts you didn't set a user_id.
        with client.session_transaction() as sess:
            assert "user_id" not in sess
