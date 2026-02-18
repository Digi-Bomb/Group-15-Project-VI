import sys
import os
import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

# Ensure project root and `app` package modules like `forms` are importable during tests
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'app'))

import importlib.util

# Load the Flask application module directly to avoid top-level package name conflicts
spec = importlib.util.spec_from_file_location(
    "app_pkg",
    os.path.join(project_root, "app", "app.py"),
)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
flask_app = app_module.app

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

    with patch('booking.routes.DatabaseConnection') as MockDB, patch(
        'booking.routes.DatabaseReadingServices', return_value=mock_reader
    ) as MockReader, patch('booking.routes.DatabaseWritingServices', return_value=mock_writer) as MockWriter, patch(
        'booking.routes.render_template', return_value='rendered') as MockRender:

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

    with patch('booking.routes.DatabaseConnection') as MockDB, patch(
        'booking.routes.DatabaseReadingServices', return_value=mock_reader
    ) as MockReader, patch('booking.routes.DatabaseWritingServices', return_value=mock_writer) as MockWriter:

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

    with patch('booking.routes.DatabaseConnection') as MockDB, patch(
        'booking.routes.DatabaseReadingServices', return_value=mock_reader
    ) as MockReader, patch('booking.routes.DatabaseWritingServices', return_value=mock_writer) as MockWriter:

        with client.session_transaction() as sess:
            sess['user_id'] = 300

        resp = client.delete('/booking/3/edit')
        assert resp.status_code == 302
        assert resp.headers['Location'].endswith('/')

#create booking: get, post

#
