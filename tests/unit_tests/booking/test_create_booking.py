# tests/booking/test_create_booking.py
from datetime import date, time
from unittest.mock import MagicMock, patch

def test_booking_get_logged_out_redirects(client):
    resp = client.get("/booking?room_number=2B04&date=2026-02-18")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

def test_booking_get_invalid_room_redirects(logged_in_client):
    mock_reader = MagicMock()
    mock_reader.get_room_data_given_room_number.return_value = None

    with patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader), \
         patch("app.booking.routes.DatabaseWritingServices"):
        resp = logged_in_client.get("/booking?room_number=NOPE&date=2026-02-18")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/")

def test_booking_post_success_redirects_to_new_booking(logged_in_client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = True
    fake_form.start_time.data = time(9, 0)                 # datetime.time
    fake_form.meeting_date.data = date(2026, 2, 18)        # datetime.date
    fake_form.meeting_capacity.data = 5

    mock_reader = MagicMock()
    mock_reader.get_room_data_given_room_number.return_value = {"roomNumber": "2B04", "maximumCapacity": 10}

    mock_writer = MagicMock()
    mock_writer.create_new_booking.return_value = (True, 1099)

    with patch("app.booking.routes.BookingForm", return_value=fake_form), \
         patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader), \
         patch("app.booking.routes.DatabaseWritingServices", return_value=mock_writer):

        resp = logged_in_client.post("/booking?room_number=2B04&date=2026-02-18", data={})
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/booking/1099")

def test_booking_post_room_not_available(logged_in_client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = True
    fake_form.start_time.data = time(9, 0)
    fake_form.meeting_date.data = date(2026, 2, 18)
    fake_form.meeting_capacity.data = 5

    mock_reader = MagicMock()
    mock_reader.get_room_data_given_room_number.return_value = {"roomNumber": "2B04", "maximumCapacity": 10}

    mock_writer = MagicMock()
    mock_writer.create_new_booking.return_value = (False, "Room is NOT Available")

    with patch("app.booking.routes.BookingForm", return_value=fake_form), \
         patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader), \
         patch("app.booking.routes.DatabaseWritingServices", return_value=mock_writer):

        resp = logged_in_client.post("/booking?room_number=2B04&date=2026-02-18", data={}, follow_redirects=True)
        assert resp.status_code == 200
        assert b"already booked" in resp.data.lower()

def test_booking_post_form_invalid_does_not_call_writer(logged_in_client):
    fake_form = MagicMock()
    fake_form.validate_on_submit.return_value = False

    mock_reader = MagicMock()
    mock_reader.get_room_data_given_room_number.return_value = {"roomNumber": "2B04", "maximumCapacity": 10}

    with patch("app.booking.routes.BookingForm", return_value=fake_form), \
         patch("app.booking.routes.DatabaseConnection"), \
         patch("app.booking.routes.DatabaseReadingServices", return_value=mock_reader), \
         patch("app.booking.routes.DatabaseWritingServices") as MockWriter:

        resp = logged_in_client.post("/booking?room_number=2B04&date=2026-02-18", data={})
        assert resp.status_code == 200
        MockWriter.assert_not_called()
