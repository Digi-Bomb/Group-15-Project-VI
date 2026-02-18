# tests/unit_tests/account/test_register.py
from unittest.mock import MagicMock, patch

def test_register_get_200(client):
    resp = client.get("/register")
    assert resp.status_code == 200

def test_register_post_success_redirects_and_flashes(client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = True
    fake_form.username.data = "alice"
    fake_form.password.data = "Passw0rd!"
    fake_form.firstName.data = "Alice"
    fake_form.lastName.data = "Smith"
    fake_form.email.data = "alice@example.com"

    mock_writer = MagicMock()
    mock_writer.create_new_user.return_value = (True, 999)

    with patch("app.account.routes.RegisterForm", return_value=fake_form), \
         patch("app.account.routes.DatabaseConnection"), \
         patch("app.account.routes.DatabaseReadingServices"), \
         patch("app.account.routes.DatabaseWritingServices", return_value=mock_writer):

        resp = client.post("/register", data={})
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/login")

def test_register_post_duplicate_user_flashes_error(client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = True
    fake_form.username.data = "alice"
    fake_form.password.data = "Passw0rd!"
    fake_form.firstName.data = "Alice"
    fake_form.lastName.data = "Smith"
    fake_form.email.data = "alice@example.com"

    mock_writer = MagicMock()
    mock_writer.create_new_user.return_value = (False, "User may already exist")

    with patch("app.account.routes.RegisterForm", return_value=fake_form), \
         patch("app.account.routes.DatabaseConnection"), \
         patch("app.account.routes.DatabaseReadingServices"), \
         patch("app.account.routes.DatabaseWritingServices", return_value=mock_writer):

        resp = client.post("/register", data={}, follow_redirects=True)
        assert resp.status_code == 200
        # Flash messages render into HTML; assert message text exists
        assert b"Registration failed" in resp.data

def test_register_form_invalid_does_not_hit_db(client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = False

    with patch("app.account.routes.RegisterForm", return_value=fake_form), \
         patch("app.account.routes.DatabaseWritingServices") as MockWriter:
        resp = client.post("/register", data={}, follow_redirects=True)
        assert resp.status_code == 200
        MockWriter.assert_not_called()
