# tests/test_auth_in_routes.py
import pytest

BOOKING_ROUTES_REQUIRING_LOGIN = [
    "/booking?room_number=2B04&date=2026-02-18",
    "/booking/1/edit",
]

@pytest.mark.parametrize("path", BOOKING_ROUTES_REQUIRING_LOGIN)
def test_booking_routes_require_login(client, path):
    resp = client.get(path)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

def test_rsvp_does_not_require_login(client):
    resp = client.get("/rsvp")
    assert resp.status_code in (200, 302)
