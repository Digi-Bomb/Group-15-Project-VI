from werkzeug.security import check_password_hash
from database_connection import DatabaseConnection
from flask import abort
from datetime import time, datetime, timedelta, date


class DatabaseReadingServices:
    def __init__(self, database: DatabaseConnection):
        self.database = database
        # self.conn = self.database.connect()
        self.room_capacity_cache = {}
        # conn = self.database

    # def generic_registered_user_reads_gets_associated_fields(
    #     self, field_to_find, search_field
    # ):
    #     """Function that acts as a generic method to find a field (ex. 'email'), given another field"""

    #     cursor.execute()

    def get_specific_registered_user_email_given_username(self, username: str):
        """Function that returns the username associated with an email (for users who forget)"""
        conn = self.database
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT email FROM RegisteredUser WHERE username = %s",
            (username,),
        )
        try:
            # Needed to ensure we get the first element of the tuple response (only need to know the first email associated with user)
            result = cursor.fetchone()[0]
            cursor.close()  # Empty Cursor

            if result:
                return result

            else:
                return "No user found with that username."
        except TypeError:
            cursor.close()  # Empty Cursor
            return "No user found with that username."

    # function for searching username given email

    def validate_user_information(self, username: str, password: str, email=""):
        """NOTE: NEEDS HASHING SUPPORT; INPUT REQUIRES AT LEAST 2 NON NULL INPUT VALUES. \n
        Function that returns a boolean and a string message confirming that the password matches the provided username or email
        """
        conn = self.database
        cursor = None
        cursor = conn.cursor()
        if email:
            cursor.execute(
                "SELECT RUID, pass FROM RegisteredUser WHERE email = %s", (email,)
            )

        elif username:
            cursor.execute(
                "SELECT RUID, pass FROM RegisteredUser WHERE username = %s", (username,)
            )

        row = cursor.fetchone()
        cursor.close()  # Empty Cursor

        if row:
            ruid, stored_hash = row[0], row[1]
            if check_password_hash(stored_hash, password):
                return True, "Successful Login", ruid
            return False, "Incorrect Login Information", None

        return (
            False,
            "Unable to find the account registered under this email or username",
            None,
        )

    def get_specific_meeting_owner_for_booking(self, BID: int):
        """Function that returns the sole meeting owner (via RID) of a particular booking (specified by BID)"""

        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute("SELECT meetingOwner from Booking WHERE BID = %s", (BID,))
            result = cursor.fetchone()[0]

            if result:
                return result
            else:
                return "Error in Database, no User Specified as Meeting Owner"
        except TypeError:
            return "Error in Database, no User Specified as Meeting Owner"

    def get_username_via_RUID(self, RUID: int):
        """Function that returns the username of a registered user given a RUID (Registered User ID)"""
        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username FROM RegisteredUser WHERE RUID = %s", (RUID,)
            )
            result = cursor.fetchone()[0]
            if result:
                return result
            else:
                return "Error, no Registered User with the specified ID exists"
        except TypeError:
            return "Error, no Registered User with the specified ID exists"

    def get_meetings_owned_by_registered_user(self, RUID: int):
        """Function that returns a TUPLE object of the meetings that a specific user has created"""

        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT BID FROM Booking WHERE meetingOwner = %s",
                (RUID,),
            )

            result = cursor.fetchall()
            if result:

                return result
            else:
                return "No meetings found for that registered user ID."
        except TypeError:
            return "No meetings found for that registered user ID."

    def get_registered_users_associated_with_booking_ID(self, BID: int):
        """Function that returns a TUPLE (list) of all registered attendees for a specific meeting"""
        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT RegisteredAttendee FROM RegisteredBookingAttendees WHERE BID = %s",
                (BID,),
            )

            result = cursor.fetchall()

            if result:
                return result
            else:
                return "No registered users found for that booking ID."
        except TypeError:
            return "No registered users found for that booking ID."

    def get_unregistered_users_associated_with_booking_ID(self, BUID: int):
        """Function that returns a TUPLE (list) of all unregistered attendees for a specific meeting"""

        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT unregisteredAttendee FROM UnregisteredBookingAttendees WHERE BID = %s",
                (BUID,),
            )

            result = cursor.fetchall()

            if result:
                return result
            else:
                return "No unregistered users found for that booking ID."
        except TypeError:
            return "No unregistered users found for that booking ID."

    def check_if_user_is_registered_already(self, username: str, email: str):
        """Function that ensures double registry for a user isn't possible; \n
        REQUIRES USERNAME AND EMAIL \n
        TRUE == REGISTERED \n
        FALSE == UNREGISTERED"""
        conn = self.database
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT RUID FROM RegisteredUser WHERE username = %s OR email = %s",
            (username, email),
        )

        result = cursor.fetchall()

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
        conn = self.database
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT unregisteredAttendee FROM UnregisteredBookingAttendees WHERE BID = %s",
            (BID,),
        )
        user_ids = cursor.fetchall()

        for user in user_ids:

            cursor.execute(
                "SELECT nickName FROM UnregisteredUser WHERE URUID = %s", user
            )
            curnickname = cursor.fetchone()[0]

            if curnickname == nickname:
                cursor.close()  # Empty Cursor
                return False, "Nickname is taken"

        cursor.close()  # Empty Cursor
        return True, "Nickname available"

    # def check_booking_still_active(self, BID: int):
    #     """Function that validates that a booking exists within the database \n
    #     RETURNS BOOLEAN VALUE \n
    #     TRUE == BOOKING EXISTS \n
    #     FALSE == BOOKING ISNT REAL OR EXPIRED"""

    #     cursor.execute("SELECT * FROM Booking WHERE BID = %s LIMIT 1", (BID,))

    #     result = cursor.fetchall()
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
        conn = self.database
        """Function that validates that a room is available for use \n
        NOTE: ONLY INCLUDE BID IF THIS IS AN ATTEMPT TO UPDATE AN EXISTING BOOKING
        \n TRUE == ROOM IS AVAILABLE \n FALSE == ROOM TAKEN"""

        query = """
        SELECT 1 FROM Booking b JOIN RoomsAssociatedWithBookings rwb ON b.BID = rwb.BID WHERE rwb.RID = %s AND b.meetingDate = %s AND b.startTime < ADDTIME(%s, %s) AND ADDTIME(b.startTime, b.duration) > %s
        """
        params = [
            room_number,
            meeting_date,
            start_time,  # used to compute new_end
            duration,
            start_time,  # new_start
        ]

        if BID is not None:
            query += " AND b.BID != %s"
            params.append(BID)

        query += " LIMIT 1"

        cursor = None
        cursor = conn.cursor()
        cursor.execute(query, params)

        # If we find ANY row, an overlap exists
        return cursor.fetchone() is None

    def get_capacity_of_room(self, room_number: int):
        """Function that returns the INTEGER Capacity of the room (specified by room number)"""

        if room_number not in self.room_capacity_cache:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT maximumCapacity FROM Room WHERE roomNumber = %s", (room_number,)
            )
            self.room_capacity_cache[room_number] = cursor.fetchone()[0]
            cursor.close()

        return self.room_capacity_cache[room_number]

    def get_branch_location_of_room_associated_with_room_number(self, room_number: int):
        """Returns the building for which the room exists within (specified by room number)"""
        conn = self.database
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT companyBuilding FROM Room WHERE roomNumber = %s", (room_number,)
        )
        result = cursor.fetchone()[0]
        cursor.close()  # Empty Cursor

        if result:
            return result

    def get_booking_information_of_specific_booking(self, BID: int):
        """Returns the meeting date, time, duration, and room of a particular booking"""
        conn = self.database
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT meetingDate, startTime, duration, meetingRoom, numberOfConfirmations, meetingOwner, reminderSent, shareableLink, BID, meetingSize FROM Booking WHERE BID = %s",
            (BID,),
        )
        row = cursor.fetchone()

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
        prev_booking_id = row[8]
        prev_booking_size = row[9]

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
            prev_shareable_link,
            prev_booking_id,
            prev_booking_size,
        )

    def get_booking_start_and_end_times_for_specific_room_include_date(
        self, room_number: str
    ):
        """Function that returns a list of start times, end times, and dates for all bookings under a particular room \n
        NOTE: IN ORDER OF DATE, START, END TIME"""
        conn = self.database

        # First check room id from associated table
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT BID FROM RoomsAssociatedWithBookings WHERE RID = %s",
            (room_number,),  # Returns ALL bookings for a Room
        )

        bookings = cursor.fetchall()

        booked_times = []

        for (booking,) in bookings:

            cursor.execute(
                "SELECT meetingDate, startTime, duration, ADDTIME(startTime, duration) AS endTime FROM Booking WHERE BID = %s",
                (booking,),
            )

            row = cursor.fetchone()

            curmeetingDate_db = row[0]
            curmeetingStartTime_db = row[1]
            # curstartDuration_db = row[2]
            curendTime_db = row[3]

            # Conversions for string input needed by checking room availability
            total_seconds_meet_start = int(curmeetingStartTime_db.total_seconds())
            hours_ms, remainder_ms = divmod(total_seconds_meet_start, 3600)
            minutes_ms, seconds_ms = divmod(remainder_ms, 60)

            cur_meeting_time = f"{hours_ms:02}:{minutes_ms:02}"

            # Conversions for string input needed by checking room availability
            total_seconds_meet_end = int(curendTime_db.total_seconds())
            hours_me, remainder_me = divmod(total_seconds_meet_end, 3600)
            minutes_me, seconds_me = divmod(remainder_me, 60)

            curendTime_db = f"{hours_me:02}:{minutes_me:02}"

            curmeetingDate_db = curmeetingDate_db.strftime("%Y-%m-%d")

            tupleOfInfo = (
                curmeetingDate_db,
                cur_meeting_time,
                curendTime_db,
            )

            booked_times.append(tupleOfInfo)

        return booked_times

    def get_booking_start_and_end_times_for_specific_room_include_date_with_meeting_owner(
        self, room_number: str
    ):
        """Function that returns a list of start times, end times, and dates WITH meeting owner for all bookings under a particular room \n
        NOTE: IN ORDER OF DATE, START, END TIME"""
        conn = self.database

        # First check room id from associated table
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT BID FROM RoomsAssociatedWithBookings WHERE RID = %s",
            (room_number,),  # Returns ALL bookings for a Room
        )

        bookings = cursor.fetchall()

        booked_times = []

        for (booking,) in bookings:

            cursor.execute(
                "SELECT meetingDate, startTime, duration, meetingOwner, ADDTIME(startTime, duration) AS endTime FROM Booking WHERE BID = %s",
                (booking,),
            )

            row = cursor.fetchone()

            curmeetingDate_db = row[0]
            curmeetingStartTime_db = row[1]
            # curstartDuration_db = row[2]
            curendTime_db = row[4]
            curmeetingOwner_db = row[3]

            # Conversions for string input needed by checking room availability
            total_seconds_meet_start = int(curmeetingStartTime_db.total_seconds())
            hours_ms, remainder_ms = divmod(total_seconds_meet_start, 3600)
            minutes_ms, seconds_ms = divmod(remainder_ms, 60)

            cur_meeting_time = f"{hours_ms:02}:{minutes_ms:02}"

            # Conversions for string input needed by checking room availability
            total_seconds_meet_end = int(curendTime_db.total_seconds())
            hours_me, remainder_me = divmod(total_seconds_meet_end, 3600)
            minutes_me, seconds_me = divmod(remainder_me, 60)

            curendTime_db = f"{hours_me:02}:{minutes_me:02}"

            curmeetingDate_db = curmeetingDate_db.strftime("%Y-%m-%d")

            tupleOfInfo = (
                curmeetingDate_db,
                cur_meeting_time,
                curendTime_db,
                curmeetingOwner_db,
            )

            booked_times.append(tupleOfInfo)

        return booked_times

    def get_booking_start_and_end_times_for_specific_room_include_date_with_BID(
        self, room_number: str
    ):
        """Function that returns a list of start times, end times, and dates WITH meeting owner for all bookings under a particular room \n
        NOTE: IN ORDER OF DATE, START, END TIME"""
        conn = self.database

        # First check room id from associated table
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT BID FROM RoomsAssociatedWithBookings WHERE RID = %s",
            (room_number,),  # Returns ALL bookings for a Room
        )

        bookings = cursor.fetchall()

        booked_times = []

        for (booking,) in bookings:

            cursor.execute(
                "SELECT meetingDate, startTime, duration, BID, ADDTIME(startTime, duration) AS endTime FROM Booking WHERE BID = %s",
                (booking,),
            )

            row = cursor.fetchone()

            curmeetingDate_db = row[0]
            curmeetingStartTime_db = row[1]
            # curstartDuration_db = row[2]
            curendTime_db = row[4]
            curmeetingOwner_db = row[3]

            # Conversions for string input needed by checking room availability
            total_seconds_meet_start = int(curmeetingStartTime_db.total_seconds())
            hours_ms, remainder_ms = divmod(total_seconds_meet_start, 3600)
            minutes_ms, seconds_ms = divmod(remainder_ms, 60)

            cur_meeting_time = f"{hours_ms:02}:{minutes_ms:02}"

            # Conversions for string input needed by checking room availability
            total_seconds_meet_end = int(curendTime_db.total_seconds())
            hours_me, remainder_me = divmod(total_seconds_meet_end, 3600)
            minutes_me, seconds_me = divmod(remainder_me, 60)

            curendTime_db = f"{hours_me:02}:{minutes_me:02}"

            curmeetingDate_db = curmeetingDate_db.strftime("%Y-%m-%d")

            tupleOfInfo = (
                curmeetingDate_db,
                cur_meeting_time,
                curendTime_db,
                curmeetingOwner_db,
            )

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
        conn = self.database

        # First check room id from associated table
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT BID FROM RoomsAssociatedWithBookings WHERE RID = %s",
            (room_number,),  # Returns ALL bookings for a Room
        )

        bookings = cursor.fetchall()

        booked_times = []

        for (booking,) in bookings:

            cursor.execute(
                "SELECT startTime, duration, ADDTIME(startTime, duration) AS endTime FROM Booking WHERE BID = %s AND meetingDate = %s",
                (booking,),
            )

            row = cursor.fetchone()

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
        conn = self.database

        cursor = None
        cursor = conn.cursor()
        cursor.execute("SELECT BID FROM Booking WHERE meetingOwner = %s", (RUID,))

        result = cursor.fetchall()

        if result:
            return result
        else:
            return False, "Unable to find any users for the booking"

    def return_all_bookings_with_info_for_a_user(self, RUID: int):
        """
        Returns all bookings owned by a registered user along with full info.
        Always returns a tuple of bookings; empty tuple if none found.
        """

        conn = self.database

        # Select the relevant booking info
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT meetingRoom, meetingDate, startTime, duration, numberOfConfirmations, meetingOwner, reminderSent, shareableLink, BID, ADDTIME(startTime, duration) AS endTime FROM Booking WHERE meetingOwner = %s",
            (RUID,),
        )

        bookings = cursor.fetchall()
        cursor.close()

        # Return as tuple (even if empty)
        return tuple(bookings)

    def get_registered_user_email_from_RUID(self, RUID: int):
        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            result = cursor.execute(
                "SELECT email FROM RegisteredUser WHERE RUID = %s", (RUID,)
            )
            result = cursor.fetchone()[0]

            if result:
                return result
            else:
                return "No registered user found for that RUID."
        except TypeError:
            return "No registered user found for that RUID."

    def get_booking_by_link_id(self, link_id: str):
        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Booking WHERE shareableLink = %s", (link_id,))
            result = cursor.fetchone()[0]

            if result:
                return result
            else:
                return "No booking found for that shareable link ID."
        except TypeError:
            return "No booking found for that shareable link ID."

    def get_all_bookings(self):
        conn = self.database
        cursor = None
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Booking")
        result = cursor.fetchall()

        if result:
            return result

        else:
            return "No bookings found in the database."

    def get_unregistered_user_email_from_URUID(self, URUID: int):
        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT email FROM UnregisteredUser WHERE URUID = %s", (URUID,)
            )
            result = cursor.fetchone()[0]

            if result:
                return result
            else:
                return "No unregistered user found for that URUID."
        except TypeError:
            return "No unregistered user found for that URUID."

    def get_rooms(self, building: str | None = None):
        """
        Returns a list of rooms.
        If building is provided, filters by companyBuilding.
        """
        # print("[DB] get rooms called")

        conn = self.database
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

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            results = cursor.fetchall()
            return results
        finally:
            if cursor is not None:
                cursor.close()

    def get_room_data_given_room_number(self, room_number: str):
        conn = self.database
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT roomNumber, companyBuilding, wing, wheelchairAccessible, projectorAccess, whiteboardAccess, maximumCapacity FROM Room WHERE roomNumber = %s",
            (room_number,),
        )

        result = cursor.fetchone()

        # result [0] is roomNumber, result[1] is company building, [2] is wing, at [3] is wheelchairAccessible, at [4] is projectorAccess, at [5] is whiteboardAccess, at [6] is maximumCapacity
        if result:
            cursor.close()
            return result

        else:
            return False, "Unable to find the room specified"

    # def get_duration_from_given_end_time(self, start_time:time, end_time: time):

    def get_list_of_registered_and_unregistered_attendees(self, BID: int):
        conn = self.database
        try:
            cursor = None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT RUID FROM RegisteredBookingAttendees WHERE BID = %s", (BID,)
            )

            registered_result = cursor.fetchall()

            cursor.execute(
                "SELECT URUID FROM UnregisteredBookingAttendees WHERE BID = %s", (BID,)
            )

            unregistered_result = cursor.fetchall()

            if registered_result and unregistered_result:
                return registered_result, unregistered_result

            elif registered_result:
                return registered_result

            else:
                return "Unable to find any users associated with the meeting"
        except TypeError:
            return "Unable to find any users associated with the meeting"

    def get_list_of_registered_and_unregistered_attendees_with_user_info(
        self, BID: int
    ):

        conn = self.database

        # Registered attendees
        cursor = None
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT RU.*
            FROM RegisteredBookingAttendees RBA
            JOIN RegisteredUser RU ON RBA.RegisteredAttendee = RU.RUID
            WHERE RBA.BID = %s
        """,
            (BID,),
        )

        registered = cursor.fetchall()

        # Unregistered attendees
        cursor.execute(
            """
            SELECT URU.*
            FROM UnregisteredBookingAttendees UBA
            JOIN UnregisteredUser URU ON UBA.unregisteredAttendee = URU.URUID
            WHERE UBA.BID = %s
        """,
            (BID,),
        )

        unregistered = cursor.fetchall()
        cursor.close()

        all_attendees = tuple(registered + unregistered)
        return all_attendees

    def get_number_of_confirmations_for_booking(self, BID: int):
        try:
            conn = self.database
            cursor = None
            cursor = conn.cursor()
            cursor.execute(
                "SELECT numberOfConfirmations FROM Booking WHERE BID = %s", (BID,)
            )

            result = cursor.fetchone()[0]

            if result is not None:
                return result
            else:
                return "Unable to find the booking specified or no confirmations yet."
        except TypeError:
            return "Unable to find the booking specified or no confirmations yet."

    # def close(self):
    #     """Release DB resources.

    #     With connection pooling, closing the connection returns it to the pool.
    #     """
    #     try:
    #         cur = getattr(self, "cursor", None)
    #         if cur is not None:
    #             try:
    #                 cur.close()
    #             except Exception:
    #                 pass
    #     finally:
    #         try:
    #             if getattr(self, "conn", None) is not None:
    #                 self.conn.close()
    #         except Exception:
    #             pass

    # def __del__(self):
    #     # Best-effort safety net (routes/services can also call .close() explicitly).
    #     try:
    #         self.close()
    #     except Exception:
    #         pass
