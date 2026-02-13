from database_connection import DatabaseConnection
from datetime import time, datetime, timedelta


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

        start_dt = datetime.strptime(start_time, "%H:%M:%S")
        start_time_obj = start_dt.time()
        h, m, s = map(int, duration.split(":"))
        duration_td = timedelta(hours=h, minutes=m, seconds=s)

        combined_dt = datetime.combine(datetime.today(), start_time_obj) + duration_td
        end_time_obj = combined_dt.time()
        # First check room id from associated table
        # Second check given time is not taken

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
            # curduration_db = row[2]
            curendTime_db = row[3]

            if isinstance(curstartTime_db, str):
                curstartTime_db = datetime.strptime(curstartTime_db, "%H:%M:%S").time()
            if isinstance(curendTime_db, str):
                curendTime_db = datetime.strptime(curendTime_db, "%H:%M:%S").time()

            # Case 1, start time and date of proposed booking is equal to existing booking
            if meeting_date == curmeetingDate_db and start_time_obj == curstartTime_db:
                return False, "Booking start time already taken for this Room"

            # Case 2, an existing booking leaks into proposed booking start time
            elif meeting_date == curmeetingDate_db and curendTime_db >= start_time_obj:
                return False, "An existing booking will exceed the specified start time"

            elif meeting_date == curmeetingDate_db and end_time_obj == curstartTime_db:
                return (
                    False,
                    "The proposed booking's duration will exceed start time of another meeting",
                )

            # if result:
            #     return False

            # else:
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
            return result
