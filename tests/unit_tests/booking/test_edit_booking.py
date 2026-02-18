# tests/booking/test_edit_booking.py
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

def make_booking_obj(owner_id=42):
    return SimpleNamespace(booking_owner_id=owner_id)

def test_edit_booking_logged_out_redirects(client):
    resp = client.get("/booking/1/edit")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

def test_edit_booking_not_found_404(logged_in_client):
    mock_reader = MagicMock()
    mock_reader.get_booking_information_of_specific_booking.return_value = (False, None)

    with patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader), \
         patch("app.booking.routes.DatabaseWritingServices"):

        resp = logged_in_client.get("/booking/1/edit")
        assert resp.status_code == 404

def test_edit_booking_forbidden_if_not_owner(logged_in_client):
    mock_reader = MagicMock()
    mock_reader.get_booking_information_of_specific_booking.return_value = (True, make_booking_obj(owner_id=9999))

    with patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader), \
         patch("app.booking.routes.DatabaseWritingServices"):

        resp = logged_in_client.get("/booking/1/edit")
        assert resp.status_code == 403

def test_edit_booking_patch_success_redirects(logged_in_client):
    mock_reader = MagicMock()
    mock_reader.get_booking_information_of_specific_booking.return_value = (True, make_booking_obj(owner_id=1234))

    with patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader), \
         patch("app.booking.routes.DatabaseWritingServices"), \
         patch("app.booking.routes.BookingService.update_booking", return_value=(True, "ok")):

        resp = logged_in_client.patch("/booking/2/edit", json={"meeting_date": "2026-02-18"})
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/booking/2")

def test_edit_booking_delete_success_redirects_home(logged_in_client):
    mock_reader = MagicMock()
    mock_reader.get_booking_information_of_specific_booking.return_value = (True, make_booking_obj(owner_id=1234))

    with patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader), \
         patch("app.booking.routes.DatabaseWritingServices") as MockWriter:

        mock_writer = MockWriter.return_value
        mock_writer.delete_booking.return_value = True

        resp = logged_in_client.delete("/booking/3/edit")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/")
