from database_connection import DatabaseConnection


class DatabaseReadingServices:
    def __init__(self, database: DatabaseConnection):
        self.database = database
        self.conn = self.database.connect()
        self.cursor = self.conn.cursor()

    def get_specific_registered_user(self, username: str):
        result = self.cursor.execute(
            "SELECT RUID, username FROM RegisteredUser WHERE username = %s", (username,)
        )
        if result:
            return self.cursor.fetchall()
        else:
            return "No user found with that username."

    def get_meetings_owned_by_registered_user(self, RUID: int):
        result = self.cursor.execute("SELECT BID FROM Booking WHERE RUID = %s", (RUID,))
        if result:
            return self.cursor.fetchall()
        else:
            return "No meetings found for that registered user ID."

    def get_registered_users_associated_with_booking_ID(self, BUID: int):
        result = self.cursor.execute(
            "SELECT RegisteredAttendee FROM RegisteredBookingAttendees WHERE booking_ID = %s",
            (BUID,),
        )
        if result:
            return self.cursor.fetchall()
        else:
            return "No registered users found for that booking ID."

    def get_unregistered_users_associated_with_booking_ID(self, BUID: int):
        result = self.cursor.execute(
            "SELECT unregisteredAttendee FROM UnregisteredBookingAttendees WHERE booking_ID = %s",
            (BUID,),
        )
        if result:
            return self.cursor.fetchall()
        else:
            return "No unregistered users found for that booking ID."

    def check_if_user_is_registered_already(self, username: str, email: str):
        result = self.cursor.execute(
            "SELECT RUID FROM RegisteredUser WHERE username = %s OR email = %s",
            (username, email),
        )
        if result:
            return True
        else:
            return False

    def get_capacity_of_room(self, room_number: int):
        result = self.cursor.execute(
            "SELECT maximumCapacity FROM Room WHERE roomNumber = %s", (room_number,)
        )
        if result:
            return self.cursor.fetchone()[0]
        else:
            return "No room found with that ID."

    def get_branch_location_of_room_associated_with_room_number(self, room_number: int):
        result = self.cursor.execute(
            "SELECT companyBuilding FROM Room WHERE roomNumber = %s", (room_number,)
        )
        if result:
            return self.cursor.fetchone()[0]

    def get_meeting_owner_from_BID(self, BID: int):
        result = self.cursor.execute(
            "SELECT meetingOwner FROM Booking WHERE BID = %s", (BID,)
        )
        if result:
            return self.cursor.fetchall()
        else:
            return "No bookings found for that BID."
    
    def get_registered_user_email_from_RUID(self, RUID: int):
        result = self.cursor.execute(
            "SELECT email FROM RegisteredUser WHERE RUID = %s", (RUID,)
        )
        if result:
            return self.cursor.fetchall()
        else:
            return "No registered user found for that RUID."
        
    def get_booking_by_link_id(self, link_id: str):
        result = self.cursor.execute(
            "SELECT * FROM Booking WHERE link_id = %s", (link_id,)
        )
        if result:
            return self.cursor.fetchall()
        else:
            return "No booking found for that shareable link ID."
        
    def get_all_bookings(self):
        result = self.cursor.execute("SELECT * FROM Booking")
        if result:
            return self.cursor.fetchall()
        else:
            return "No bookings found in the database."
        
    def set_send_reminder_email_flag_for_booking(self, booking_id: int, reminder_sent: bool):
        self.cursor.execute(
            "UPDATE Booking SET reminderSent = %s WHERE BID = %s",
            (reminder_sent, booking_id)
        )
        self.conn.commit()