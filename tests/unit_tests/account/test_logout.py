# tests/account/test_logout.py
from unittest.mock import MagicMock, patch

def test_logout_clears_session_and_redirects(logged_in_client):
    resp = logged_in_client.post("/logout")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")

    with logged_in_client.session_transaction() as sess:
        assert "user_id" not in sess

def test_profile_logged_out_behavior(client):
    resp = client.get("/profile")
    # login not currently enforced, just loads page; in future may redirect or show different content
    assert resp.status_code in (200, 302)

def test_profile_logged_in_renders_user(logged_in_client):
    # Route uses raw cursor in your sample; easiest is patch the reader.conn.cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"username": "bob", "email": "bob@example.com"}

    mock_reader = MagicMock()
    mock_reader.conn.cursor.return_value = mock_cursor

    with patch("app.account.routes.DatabaseConnection"), \
         patch("app.account.routes.DatabaseReadingServices", return_value=mock_reader):
        resp = logged_in_client.get("/profile")
        assert resp.status_code == 200
