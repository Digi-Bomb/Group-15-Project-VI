from werkzeug.security import check_password_hash
from database_connection import DatabaseConnection
from flask import abort
from datetime import time, datetime, timedelta, date


class DatabaseReadingServices:
    def __init__(self, database: DatabaseConnection):
        self.database = database
        self.conn = self.database.connect()
        #self.cursor = self.conn.cursor()

    # def generic_registered_user_reads_gets_associated_fields(
    #     self, field_to_find, search_field
    # ):
    #     """Function that acts as a generic method to find a field (ex. 'email'), given another field"""

    #     self.cursor.execute()

    def get_specific_registered_user_email_given_username(self, username: str):
        """Function that returns the username associated with an email (for users who forget)"""
        self.cursor = self.conn.cursor()
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
        self.cursor = self.conn.cursor()
        if email:
            self.cursor.execute(
                "SELECT RUID, pass FROM RegisteredUser WHERE email = %s", (email,)
            )

        elif username:
            self.cursor.execute(
                "SELECT RUID, pass FROM RegisteredUser WHERE username = %s", (username,)
            )

        row = self.cursor.fetchone()
        self.cursor.close()  # Empty Cursor

        if row:
            ruid, stored_hash = row[0], row[1]
            if check_password_hash(stored_hash, password):
                return True, "Successful Login", ruid
            return False, "Incorrect Login Information", None

        return False, "Unable to find the account registered under this email or username", None

    def get_specific_meeting_owner_for_booking(self, BID: int):
        """Function that returns the sole meeting owner (via RID) of a particular booking (specified by BID)"""
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT meetingOwner from Booking WHERE BID = %s", (BID,))
        result = self.cursor.fetchone()[0]

        if result:
            return result
        else:
            return "Error in Database, no User Specified as Meeting Owner"

    def get_username_via_RUID(self, RUID: int):
        """Function that returns the username of a registered user given a RUID (Registered User ID)"""
        self.cursor = self.conn.cursor()
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
        self.cursor = self.conn.cursor()
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
        self.cursor = self.conn.cursor()
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
        self.cursor = self.conn.cursor()
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
        self.cursor = self.conn.cursor()
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
        self.cursor = self.conn.cursor()
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
        NOTE: ONLY INCLUDE BID IF THIS IS AN ATTEMPT TO UPDATE AN EXISTING BOOKING \n
        TRUE == ROOM IS AVAILABLE \n
        FALSE == ROOM TAKEN"""
        self.cursor = self.conn.cursor()
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

        self.cursor = self.conn.cursor()
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
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT companyBuilding FROM Room WHERE roomNumber = %s", (room_number,)
        )
        result = self.cursor.fetchone()[0]
        self.cursor.close()  # Empty Cursor

        if result:
            return result

    def get_booking_information_of_specific_booking(self, BID: int):
        """Returns the meeting date, time, duration, and room of a particular booking"""
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT meetingDate, startTime, duration, meetingRoom, numberOfConfirmations, meetingOwner, reminderSent, shareableLink FROM Booking WHERE BID = %s",
            (int(BID),),
        )
        row = self.cursor.fetchone()

        if not row:
            return False

        prev_meeting_room = row[3]
        prev_meeting_time = row[1]
        prev_meeting_date = row[0]
        prev_meeting_duration = row[2]
        prev_meeting_confirmed = row[4]
        prev_meeting_owner = row[5]
        prev_reminder_sent = row[6]
        prev_shareable_link = row[7]

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
        
        prev_reminder_sent = bool(prev_reminder_sent)

        return (
            prev_meeting_room,
            prev_meeting_date,
            prev_meeting_time,
            prev_meeting_duration,
            prev_meeting_confirmed,
            prev_meeting_owner,
            prev_reminder_sent,
            prev_shareable_link
        )


    def get_booking_start_and_end_times_for_specific_room_include_date(
        self, room_number: str
    ):
        """Function that returns a list of start times, end times, and dates for all bookings under a particular room \n
        NOTE: IN ORDER OF DATE, START, END TIME"""
        self.cursor = self.conn.cursor()

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

    def change_time_object_into_string(self, time_obj):
        """Function that takes a time object input and converts it to a string\n
        RETURNS A STRING IN THE FORMAT OF 'HH:MM:SS'"""
        # Conversions for string input needed by checking room availability
        seconds_of_time = int(time_obj.total_seconds())
        hours, remainder = divmod(seconds_of_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        return_string = f"{hours:02}:{minutes:02}:{seconds:02}"

        return return_string

    def change_date_object_into_string(self, date_obj):
        """Function that takes a date object input and converts it to a string\n
        RETURNS A STRING IN THE FORMAT OF 'YYYY-MM-DD'"""
        return date_obj.strftime("%Y-%m-%d")

    def get_booking_start_and_end_times_for_specific_room_exclude_date(
        self, room_number: str, meeting_date: str
    ):
        """Function that returns a list of start times, and end times for all bookings under a particular room \n
        NOTE: IN ORDER OF START, END TIME"""
        self.cursor = self.conn.cursor()

        # First check room id from associated table
        self.cursor.execute(
            "SELECT BID FROM RoomsAssociatedWithBookings WHERE RID = %s",
            (room_number,),  # Returns ALL bookings for a Room
        )

        bookings = self.cursor.fetchall()

        booked_times = []

        for (booking,) in bookings:

            self.cursor.execute(
                "SELECT startTime, duration, ADDTIME(startTime, duration) AS endTime FROM Booking WHERE BID = %s AND meetingDate = %s",
                (booking,),
            )

            row = self.cursor.fetchone()

            # curmeetingDate_db = row[0]
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

            # curmeetingDate_db = curmeetingDate_db.strftime("%Y-%m-%d")

            tupleOfInfo = (cur_meeting_time, curendTime_db)

            booked_times.append(tupleOfInfo)

        return booked_times

    def return_all_bookings_for_a_user(self, RUID: int):
        """Generic Function for returning all Bookings that a Registered User owns \n
        NOTE RETURNS A LIST OF BOOKINGS OWNED BY A USER \n
        RETURNS FALSE IF NO BOOKINGS OWNED"""
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT BID FROM Booking WHERE meetingOwner = %s", (RUID,))

        result = self.cursor.fetchall()

        if result:
            return result
        else:
            return False, "Unable to find any users for the booking"

    def get_registered_user_email_from_RUID(self, RUID: int):
        self.cursor = self.conn.cursor()
        result = self.cursor.execute(
            "SELECT email FROM RegisteredUser WHERE RUID = %s", (RUID,)
        )
        if result:
            return self.cursor.fetchall()
        else:
            return "No registered user found for that RUID."
    def get_booking_by_link_id(self, link_id: str):
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT * FROM Booking WHERE shareableLink = %s", (link_id,)
        )
        result = self.cursor.fetchone()[0]

        if result:
            return result
        else:
            return "No booking found for that shareable link ID."
        
    
    def get_all_bookings(self):
        self.cursor = self.conn.cursor()
        result = self.cursor.execute("SELECT * FROM Booking")
        if result:
            return self.cursor.fetchall()
        else:
            return "No bookings found in the database."

    def get_unregistered_user_email_from_URUID(self, URUID: int):
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT email FROM UnregisteredUser WHERE URUID = %s", (URUID,)
        )
        result = self.cursor.fetchone()[0]

        if result:
            return result
        else:
            return "No unregistered user found for that RUID."

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
        cursor.execute(sql, params)  # <-- execute the query
        results = cursor.fetchall()  # <-- fetch all rows as a list of dicts
        cursor.close()
        return results

    def get_room_data_given_room_number(self, room_number: str):
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT roomNumber, companyBuilding, wing, wheelchairAccessible, projectorAccess, whiteboardAccess, maximumCapacity FROM Room WHERE roomNumber = %s",
            (room_number,),
        )

        result = self.cursor.fetchone()

        # result [0] is roomNumber, result[1] is company building, [2] is wing, at [3] is wheelchairAccessible, at [4] is projectorAccess, at [5] is whiteboardAccess, at [6] is maximumCapacity
        if result:
            self.cursor.close()
            return result

        else:
            return False, "Unable to find the room specified"

    # def get_duration_from_given_end_time(self, start_time:time, end_time: time):
