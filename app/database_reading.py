from werkzeug.security import check_password_hash
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
        row = self.cursor.fetchone()

        if not row:
            return False, "Unable to find account"

        result = row[0]
        self.cursor.close()

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
            #moved comparison of password hash to here since we need to pull the hash from the database first before we can compare it to the plaintext password input by the user
            if check_password_hash(result, password):
                return True, "Successful Login"

            else:
                return False, "Incorrect Login Information"

        else:
            return False, "Unable to find the account registered under this email or username"

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
        self,
        room_number: str,
        meeting_date: str,
        start_time: str,
        duration: str,
        BID: int = None,
    ):
        """Function that validates that a room is available for use \n
        NOTE: ONLY INCLUDE BID IF THIS IS AN ATTEMPT TO UPATE AN EXISTING BOOKING \n
        TRUE == ROOM IS AVAILABLE \n
        FALSE == ROOM TAKEN"""

        start_hours, start_minutes, start_seconds = map(int, start_time.split(":"))
        start_time = timedelta(
            hours=start_hours, minutes=start_minutes, seconds=start_seconds
        )

        duration_hours, duration_minutes, duration_seconds = map(
            int, duration.split(":")
        )
        duration = timedelta(
            hours=duration_hours, minutes=duration_minutes, seconds=duration_seconds
        )

        end_time = duration + start_time
        meeting_date = datetime.strptime(meeting_date, "%Y-%m-%d").date()

        # if a BID is provided
        if BID:
            self.cursor.execute(
                "SELECT BID FROM RoomsAssociatedWithBookings WHERE RID = %s AND BID != %s",
                (room_number, BID),  # Returns ALL bookings for a Room
            )

        else:
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
                # print("error1create")
                return False

            # Case 2, an existing booking leaks into proposed booking start time
            elif meeting_date == curmeetingDate_db and (
                curstartTime_db < start_time and curendTime_db > start_time
            ):
                # print("error2create")

                return False

            # Case 3, the proposed booking leaks into a specific Booking's time
            elif meeting_date == curmeetingDate_db and (
                start_time < curstartTime_db and end_time > curstartTime_db
            ):
                # print("error3create")
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
            return result

    def get_booking_information_of_specific_booking(self, BID: int):
        """Returns the meeting date, time, duration, and room of a particular booking"""
        self.cursor.execute(
            "SELECT meetingDate, startTime, duration, meetingRoom FROM Booking WHERE BID = %s",
            (BID,),
        )
        row = self.cursor.fetchone()
        prev_meeting_room = row[3]
        prev_meeting_time = row[1]
        prev_meeting_date = row[0]
        prev_meeting_duration = row[2]

        # Conversions for string input needed by checking room availability
        total_seconds_meet_time = int(prev_meeting_time.total_seconds())
        hours_mt, remainder_mt = divmod(total_seconds_meet_time, 3600)
        minutes_mt, seconds_mt = divmod(remainder_mt, 60)

        prev_meeting_time = f"{hours_mt:02}:{minutes_mt:02}:{seconds_mt:02}"

        total_seconds_meet_duration = int(prev_meeting_duration.total_seconds())
        hours_md, remainder_md = divmod(total_seconds_meet_duration, 3600)
        minutes_md, seconds_md = divmod(remainder_md, 60)

        prev_meeting_duration = f"{hours_md:02}:{minutes_md:02}:{seconds_md:02}"

        prev_meeting_date = prev_meeting_date.strftime("%Y-%m-%d")

        if row:
            return (
                prev_meeting_room,
                prev_meeting_date,
                prev_meeting_time,
                prev_meeting_duration,
            )

        return False
    
    def get_rooms(self, building: str | None = None):
            """
            Returns a list of rooms.
            If building is provided, filters by companyBuilding.
            """
            sql = """
                SELECT
                    roomNumber,
                    companyBuilding,
                    wheelchairAccessible,
                    projectorAccess,
                    whiteboardAccess,
                    maximumCapacity
                FROM Room
            """
            params = []

            if building:
                sql += " WHERE companyBuilding = %s"
                params.append(building)

            sql += " ORDER BY companyBuilding, wing, roomNumber"

            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(sql, params)          # <-- execute the query
            results = cursor.fetchall()          # <-- fetch all rows as a list of dicts
            cursor.close()
            return results 

    def get_booking_start_and_end_times_for_specific_room(self, room_number: str):
        """Function that returns a list of start times, end times, and dates for all bookings under a particular room"""

        # First check room id from associated table
        self.cursor.execute(
            "SELECT BID FROM RoomsAssociatedWithBookings WHERE RID = %s",
            (room_number,),  # Returns ALL bookings for a Room
        )

        bookings = self.cursor.fetchall()

        booked_times = []

        for (booking,) in bookings:

            self.cursor.execute(
                "SELECT meetingDate, startTime, duration, ADDTIME(startTime, duration) AS endTime FROM Booking WHERE BID = %s",
                (booking,),
            )

            row = self.cursor.fetchone()

            curmeetingDate_db = row[0]
            curmeetingStartTime_db = row[1]
            # curstartDuration_db = row[2]
            curendTime_db = row[3]

            # Conversions for string input needed by checking room availability
            total_seconds_meet_start = int(curmeetingStartTime_db.total_seconds())
            hours_ms, remainder_ms = divmod(total_seconds_meet_start, 3600)
            minutes_ms, seconds_ms = divmod(remainder_ms, 60)

            cur_meeting_time = f"{hours_ms:02}:{minutes_ms:02}:{seconds_ms:02}"

            # Conversions for string input needed by checking room availability
            total_seconds_meet_end = int(curendTime_db.total_seconds())
            hours_me, remainder_me = divmod(total_seconds_meet_end, 3600)
            minutes_me, seconds_me = divmod(remainder_me, 60)

            curendTime_db = f"{hours_me:02}:{minutes_me:02}:{seconds_me:02}"

            curmeetingDate_db = curmeetingDate_db.strftime("%Y-%m-%d")

            tupleOfInfo = (curmeetingDate_db, cur_meeting_time, curendTime_db)

            booked_times.append(tupleOfInfo)

        return booked_times
    
    