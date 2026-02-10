from datetime import date as Date, time as Time

class Booking:
    def __init__(self, booking_id: int, booking_name: str, booking_owner_id: int, room_id: int, booking_date: Date, start_time: Time, duration_hours: float, meeting_capacity: int, num_confirmed: int, confirmed_attendees: list, status: str):
        self.booking_id = booking_id
        self.booking_name = booking_name
        self.booking_owner_id = booking_owner_id
        self.room_id = room_id
        self.booking_date = booking_date
        self.start_time = start_time
        self.duration_hours = duration_hours
        self.meeting_capacity = meeting_capacity
        self.num_confirmed = num_confirmed
        self.confirmed_attendees = confirmed_attendees
        self.status = status

