"""!
@file shareable_link.py
@brief Generates shareable RSVP link identifiers for bookings.

The ShareableLink ties a booking_id to a unique UUID string that can be embedded
in RSVP URLs (e.g., /rsvp/<uuid>).
"""

import uuid

class ShareableLink:
    """!
    @brief Model for a shareable RSVP link.
    @param booking_id Booking ID the link refers to.

    @var link_id Unique UUIDv4 identifier for the link.
    @var booking_id Booking identifier associated with the link.
    """
    def __init__(self, booking_id: int):
        """!
        @brief Create a new ShareableLink and generate its identifier.
        @param booking_id Booking identifier to associate with the generated link.
        """
        self.link_id = self.generate_link_id()
        self.booking_id = booking_id

    def generate_link_id(self) -> str:
        return str(uuid.uuid4())
