from database_connection import DatabaseConnection
from datetime import time, datetime, timedelta, date


class DatabaseReadingServices:
    def __init__(self, database: DatabaseConnection):
        self.database = database
        self.conn = self.database.connect()
        self.cursor = self.conn.cursor()

    # def generic_registered_user_reads_gets_associated_fields(
    #     self, field_to_find, search_field
    # ):
    #     """Function that acts as a generic method to find a field (ex. 'email'), given another field"""

    #     self.cursor.execute()

    def get_specific_registered_user_email_given_username(self, username: str):
        """Function that returns the username associated with an email (for users who forget)"""
        self.cursor.execute(
            "SELECT email FROM RegisteredUser WHERE username = %s",
            (username,),
        )

        # Needed to ensure we get the first element of the tuple response (only need to know the first email associated with user)
        result = self.cursor.fetchone()[0]
        self.cursor.close()  # Empty Cursor

        if result:
            return result

        else:
            return "No user found with that username."

    # function for searching username given email

    def validate_user_information(self, username: str, password: str, email=""):
        """NOTE: NEEDS HASHING SUPPORT; INPUT REQUIRES AT LEAST 2 NON NULL INPUT VALUES. \n
        Function that returns a boolean and a string message confirming that the password matches the provided username or email
        """

        if email:
            self.cursor.execute(
                "SELECT pass FROM RegisteredUser WHERE email = %s", (email,)
            )

        elif username:
            self.cursor.execute(
                "SELECT pass FROM RegisteredUser WHERE username = %s", (username,)
            )

        result = self.cursor.fetchone()[0]
        self.cursor.close()  # Empty Cursor

        if result:

            if result == password:
                return True, "Successful Login"

            else:
                return False, "Incorrect Login Information"

        else:
            False, "Unable to find the account registered under this email or username"

    def get_specific_meeting_owner_for_booking(self, BID: int):
        """Function that returns the sole meeting owner (via RID) of a particular booking (specified by BID)"""

        self.cursor.execute("SELECT meetingOwner from Booking WHERE BID = %s", (BID,))
        result = self.cursor.fetchone()[0]

        if result:
            return result
        else:
            return "Error in Database, no User Specified as Meeting Owner"

    def get_username_via_RUID(self, RUID: int):
        """Function that returns the username of a registered user given a RUID (Registered User ID)"""

        self.cursor.execute(
            "SELECT username FROM RegisteredUser WHERE RUID = %s", (RUID,)
        )
        result = self.cursor.fetchone()[0]
        if result:
            return result
        else:
            return "Error, no Registered User with the specified ID exists"

    def get_meetings_owned_by_registered_user(self, RUID: int):
        """Function that returns a TUPLE object of the meetings that a specific user has created"""

        self.cursor.execute(
            "SELECT BID FROM Booking WHERE meetingOwner = %s",
            (RUID,),
        )

        result = self.cursor.fetchall()
        if result:

            return result
        else:
            return "No meetings found for that registered user ID."

    def get_registered_users_associated_with_booking_ID(self, BID: int):
        """Function that returns a TUPLE (list) of all registered attendees for a specific meeting"""

        self.cursor.execute(
            "SELECT RegisteredAttendee FROM RegisteredBookingAttendees WHERE BID = %s",
            (BID,),
        )

        result = self.cursor.fetchall()

        if result:
            return result
        else:
            return "No registered users found for that booking ID."

    def get_unregistered_users_associated_with_booking_ID(self, BUID: int):
        """Function that returns a TUPLE (list) of all unregistered attendees for a specific meeting"""

        self.cursor.execute(
            "SELECT unregisteredAttendee FROM UnregisteredBookingAttendees WHERE BID = %s",
            (BUID,),
        )

        result = self.cursor.fetchall()

        if result:
            return result
        else:
            return "No unregistered users found for that booking ID."

    def check_if_user_is_registered_already(self, username: str, email: str):
        """Function that ensures double registry for a user isn't possible; \n
        REQUIRES USERNAME AND EMAIL \n
        TRUE == REGISTERED \n
        FALSE == UNREGISTERED"""
        self.cursor.execute(
            "SELECT RUID FROM RegisteredUser WHERE username = %s OR email = %s",
            (username, email),
        )

        result = self.cursor.fetchall()

        if result:
            return True
        else:
            return False

    def check_if_unregistered_user_nickname_is_taken_for_specific_meeting(
        self, BID: int, nickname: str
    ):
        """Function that ensures that anonymous users cannot have duplicate names for a particular meeting \n
        REQUIRES BOOKING ID AND NICKNAME TO CHECK; RETURNS TUPLE OF BOOLEAN AND RESP MESSAGE \n
        TRUE == Nickname Available \n
        FALSE == Nickname Taken"""

        self.cursor.execute(
            "SELECT unregisteredAttendee FROM UnregisteredBookingAttendees WHERE BID = %s",
            (BID,),
        )
        user_ids = self.cursor.fetchall()

        for user in user_ids:

            self.cursor.execute(
                "SELECT nickName FROM UnregisteredUser WHERE URUID = %s", user
            )
            curnickname = self.cursor.fetchone()[0]

            if curnickname == nickname:
                self.cursor.close()  # Empty Cursor
                return False, "Nickname is taken"

        self.cursor.close()  # Empty Cursor
        return True, "Nickname available"

    # def check_booking_still_active(self, BID: int):
    #     """Function that validates that a booking exists within the database \n
    #     RETURNS BOOLEAN VALUE \n
    #     TRUE == BOOKING EXISTS \n
    #     FALSE == BOOKING ISNT REAL OR EXPIRED"""

    #     self.cursor.execute("SELECT * FROM Booking WHERE BID = %s LIMIT 1", (BID,))

    #     result = self.cursor.fetchall()
    #     if result[0][0]:

    #         return True
    #     else:
    #         return False

    def check_for_room_availability(
        self, room_number: str, meeting_date: str, start_time: str, duration: str
    ):
        """Function that validates that a room is available for use \n
        RETURNS BOOLEAN VALUE \n
        TRUE == ROOM IS AVAILABLE \n
        FALSE == ROOM TAKEN"""

        start_hours, start_minutes, start_seconds = map(int, start_time.split(':'))
        start_time = timedelta(hours=start_hours, minutes=start_minutes, seconds=start_seconds)

        duration_hours, duration_minutes, duration_seconds = map(int, duration.split(':'))
        duration = timedelta(hours=duration_hours, minutes=duration_minutes, seconds=duration_seconds)

        end_time = duration + start_time
        meeting_date = datetime.strptime(meeting_date, "%Y-%m-%d").date()
      
        # First check room id from associated table
        self.cursor.execute(
            "SELECT BID FROM RoomsAssociatedWithBookings WHERE RID = %s",
            (room_number,),  # Returns ALL bookings for a Room
        )

        bookings = self.cursor.fetchall()
        
        # Check the Booking times of each
        for (booking_id,) in bookings:
            self.cursor.execute(
                "SELECT meetingDate, startTime, duration, ADDTIME(startTime, duration) AS endTime FROM Booking WHERE BID = %s",
                (booking_id,),
            )
        
            row = self.cursor.fetchone()

            curmeetingDate_db = row[0]
            curstartTime_db = row[1]
            curendTime_db = row[3]  
            
              # Case 1, start time and date of proposed booking is equal to existing booking
            if meeting_date == curmeetingDate_db and start_time == curstartTime_db:
                #print("error1create")
                return False

            # Case 2, an existing booking leaks into proposed booking start time
            elif meeting_date == curmeetingDate_db and (curstartTime_db < start_time and curendTime_db > start_time):
                #print("error2create")
                
                return False

            # Case 3, the proposed booking leaks into a specific Booking's time
            elif meeting_date == curmeetingDate_db and (start_time < curstartTime_db and end_time > curstartTime_db):
                #print("error3create")
                return False
            
        return True

    def get_capacity_of_room(self, room_number: int):
        """Function that returns the INTEGER Capacity of the room (specified by room number)"""
        self.cursor.execute(
            "SELECT maximumCapacity FROM Room WHERE roomNumber = %s", (room_number,)
        )
        result = self.cursor.fetchone()[0]
        self.cursor.close()  # Empty Cursor

        if result:
            return result
        else:
            return "No room found with that ID."

    def get_branch_location_of_room_associated_with_room_number(self, room_number: int):
        """Returns the building for which the room exists within (specified by room number)"""
        self.cursor.execute(
            "SELECT companyBuilding FROM Room WHERE roomNumber = %s", (room_number,)
        )
        result = self.cursor.fetchone()[0]
        self.cursor.close()  # Empty Cursor

        if result:
            return self.cursor.fetchone()[0]

    # def get_meeting_owner_from_BID(self, BID: int):
    #     result = self.cursor.execute(
    #         "SELECT meetingOwner FROM Booking WHERE BID = %s", (BID,)
    #     )
    #     if result:
    #         return self.cursor.fetchall()
    #     else:
    #         return "No bookings found for that BID."
    
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