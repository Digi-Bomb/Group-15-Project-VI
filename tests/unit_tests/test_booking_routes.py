import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from app.app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


def make_booking_obj(owner_id=42):
    return SimpleNamespace(
        booking_owner_id=owner_id,
        meetingDate='2026-02-17',
        startTime='09:00:00',
        meetingSize=10,
        meetingRoom='1F05'
    )


def test_edit_booking_get_owner(client):
    booking = make_booking_obj(owner_id=100)

    mock_reader = MagicMock()
    mock_reader.get_booking_information_of_specific_booking.return_value = (True, booking)
    mock_reader.get_room_data_given_room_number.return_value = {'RID': '1F05'}

    mock_writer = MagicMock()

    with patch('app.booking.routes.DatabaseConnection') as MockDB, patch(
        'app.booking.routes.DatabaseReadingServices', return_value=mock_reader
    ) as MockReader, patch('app.booking.routes.DatabaseWritingServices', return_value=mock_writer) as MockWriter:

        # set session user_id to owner
        with client.session_transaction() as sess:
            sess['user_id'] = 100

        resp = client.get('/booking/1/edit')
        assert resp.status_code == 200


def test_edit_booking_patch_success(client):
    booking = make_booking_obj(owner_id=200)

    mock_reader = MagicMock()
    mock_reader.get_booking_information_of_specific_booking.return_value = (True, booking)

    mock_writer = MagicMock()
    mock_writer.update_meeting_date.return_value = True
    mock_writer.update_meeting_time.return_value = True
    mock_writer.update_meeting_duration.return_value = True
    mock_writer.update_meeting_room.return_value = True
    mock_writer.update_meeting_capacity.return_value = True

    with patch('app.booking.routes.DatabaseConnection') as MockDB, patch(
        'app.booking.routes.DatabaseReadingServices', return_value=mock_reader
    ) as MockReader, patch('app.booking.routes.DatabaseWritingServices', return_value=mock_writer) as MockWriter:

        with client.session_transaction() as sess:
            sess['user_id'] = 200

        resp = client.patch('/booking/2/edit', json={'meeting_date': '2026-02-18'})
        assert resp.status_code == 302
        assert resp.headers['Location'].endswith('/booking/2')


def test_edit_booking_delete_success(client):
    booking = make_booking_obj(owner_id=300)

    mock_reader = MagicMock()
    mock_reader.get_booking_information_of_specific_booking.return_value = (True, booking)

    mock_writer = MagicMock()
    mock_writer.delete_booking.return_value = True

    with patch('app.booking.routes.DatabaseConnection') as MockDB, patch(
        'app.booking.routes.DatabaseReadingServices', return_value=mock_reader
    ) as MockReader, patch('app.booking.routes.DatabaseWritingServices', return_value=mock_writer) as MockWriter:

        with client.session_transaction() as sess:
            sess['user_id'] = 300

        resp = client.delete('/booking/3/edit')
        assert resp.status_code == 302
        assert resp.headers['Location'].endswith('/')
