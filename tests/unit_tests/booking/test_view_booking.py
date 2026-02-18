# tests/booking/test_view_booking.py
from unittest.mock import MagicMock, patch

def test_view_booking_success(client):
    mock_reader = MagicMock()
    # booking dict shape (matches your “dictionary part” approach)
    mock_reader.get_booking_information_of_specific_booking.return_value = {
        "roomNumber": "2B04",
        "meetingDate": "2026-02-18",
        "startTime": "09:00:00",
        "duration": "02:00:00",
        "BID": 1092,
    }
    mock_reader.get_room_data_given_room_number.return_value = {"roomNumber": "2B04"}

    with patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader):

        resp = client.get("/booking/1092")
        assert resp.status_code == 200

def test_view_booking_missing_404(client):
    mock_reader = MagicMock()
    mock_reader.get_booking_information_of_specific_booking.return_value = None

    with patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader):

        resp = client.get("/booking/999999")
        assert resp.status_code == 404
