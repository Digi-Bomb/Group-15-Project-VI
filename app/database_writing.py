from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices


class DatabaseWritingServices:
    def __init__(self, database: DatabaseConnection, reader: DatabaseReadingServices):
        self.database = database
        # conn = self.database.connect()
        # cursor = conn.cursor()
        self.reader = reader

    def create_new_user(
        self,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: str,
    ):
        """Generic function for adding a user to the Database \n
        NOTE: CHECKS FOR EXISTING USERS, NEEDS EMAIL VALIDATION(?) \n
        TRUE == USER ADDED \n
        FALSE == USER ALREADY EXISTED"""

        checkExists = self.reader.check_if_user_is_registered_already(
            username=username, email=email
        )

        conn = self.database
        if not checkExists:

            try:
                query = """
                INSERT INTO RegisteredUser
                (username, email, pass, firstName, lastName)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (username, email, password, first_name, last_name)

                # else:
                #     query = """
                #         INSERT INTO RegisteredUser
                #         (username, email, pass, firstName, lastName)
                #         VALUES ( %s, %s, %s, %s, %s)
                #     """
                #     values = (username, email, password, first_name, last_name)
                cursor = None
                cursor = conn.cursor(())
                cursor.execute(query, values)
                conn.commit()
                return True, "Register successful"

            except Exception as e:
                # conn.rollback()
                print("UPDATE ERROR: ", e)
                return False, str(e)

        return False, "User already registered"

    def create_new_unregistered_user(self, BID: int, nickname: str, email: str = ""):
        """Generic function for adding an unregistered user to the Database \n
        NOTE: CHECKS FOR EXISTING NICKNAMES BY BID, NEEDS NICKNAME \n
        TRUE == USER ADDED \n
        FALSE == USER ALREADY EXISTED"""

        nickname_available = self.reader.check_if_unregistered_user_nickname_is_taken_for_specific_meeting(
            BID, nickname
        )
        conn = self.database
        if nickname_available[0]:

            try:
                if email:
                    query = """
                    INSERT INTO UnregisteredUser
                    (nickname, email)
                    VALUES (%s, %s)
                    """
                    values = (nickname, email)
                else:
                    query = """
                    INSERT INTO UnregisteredUser
                    (nickname)
                    VALUES (%s)
                    """
                    values = (nickname,)
                cursor = None
                cursor = conn.cursor(())
                cursor.execute(query, values)
                conn.commit()
                URUID = cursor.lastrowid  # POTENTIALLY unsafe for multiple users (?)

                attempt_to_associate = self.associate_unregistered_user_with_booking(
                    BID, URUID
                )
                if attempt_to_associate:
                    return True, "Unregistered user associated succesfully"
                else:
                    return (
                        False,
                        "Unable to associate Unregistered user with booking",
                    )

            except Exception as e:
                conn.rollback()
                # print("CREATE ERROR: ", e)
                return False, str(e)
        else:
            return False, "Nickname provided is already taken for this meeting"

    def create_new_booking(
        self,
        meeting_date: str,
        start_time: str,
        duration: str,
        meeting_owner: str,
        meeting_room: str,
        meeting_capacity: int,
        shareable_link: str,
    ):
        """Generic function for adding a booking to the Database \n
        NOTE: CHECKS FOR EXISTING BOOKED ROOMS AND ROOM CAPACITY \n
        TRUE == BOOKING ADDED, AND RETURNS GENERATED BID \n
        FALSE == BOOKING DETAILS FAILED; ROOM TAKEN OR MEETING SIZE TOO LARGE"""

        checkAvailable = self.reader.check_for_room_availability(
            room_number=meeting_room,
            meeting_date=meeting_date,
            start_time=start_time,
            duration=duration,
        )
        conn = self.database
        # print("chck available: ", checkAvailable)

        roomCapacity = self.reader.get_capacity_of_room(room_number=meeting_room)

        if not checkAvailable:
            return False, "Room is NOT Available"

        if meeting_capacity > roomCapacity:
            return (
                False,
                "Room IS Available, but the specified meetingSize is greater than the room's capacity",
            )

        try:
            query = """
                INSERT INTO Booking
                (meetingDate, startTime, duration, meetingOwner, meetingRoom, meetingSize, shareableLink)
                VALUES ( %s, %s, %s, %s, %s, %s, %s)
                """
            values = (
                meeting_date,
                start_time,
                duration,
                meeting_owner,
                meeting_room,
                meeting_capacity,
                shareable_link,
            )
            cursor = None
            cursor = conn.cursor(())
            cursor.execute(query, values)

            booking_id = cursor.lastrowid  # POTENTIALLY unsafe for multiple users (?)

            cursor.execute(
                """
                    INSERT INTO RoomsAssociatedWithBookings (BID, RID)
                    VALUES (%s, %s)
                    """,
                (booking_id, meeting_room),
            )

            cursor.execute(
                """
                    INSERT INTO RegisteredBookingAttendees (BID, RegisteredAttendee)
                    VALUES (%s, %s)
                    """,
                (booking_id, meeting_owner),
            )

            conn.commit()
            return True, booking_id
            # attempt_to_associate = self.associate_registered_user_with_booking(
            #     booking_id, meeting_owner
            # )
        except Exception as e:
            conn.rollback()
            return False, str(e)

    def book_a_room_after_booking(self, BID: int, meeting_room):
        """Generic function for assignment of a room to a particular booking \n
        TRUE == ABLE TO BOOK ROOM \n
        FALSE == ROOM ALREADY BOOKED"""
        conn = self.database
        try:
            query = """
                INSERT INTO RoomsAssociatedWithBookings(BID, RID)
                VALUES (%s, %s)
            """

            values = (BID, meeting_room)
            cursor = None
            cursor = conn.cursor(())
            cursor.execute(query, values)
            conn.commit()

            return True

        except Exception as e:
            conn.rollback()
            # print("INSERT ERROR: ", e)
            return False, str(e)

    def associate_registered_user_with_booking(self, BID: int, RUID: str):
        """Generic function for associating a booking to Registered Users \n
        NOTE: CALLED AUTOMATICALLY WHEN A BOOKING IS CREATED, ATTACHES MEETING OWNER TO BOOKING IN THIS TABLE \n
        TRUE == ASSOCIATION RECORD ADDED \n
        FALSE == ASSOCIATION RECORD FAILED"""

        # isBookingExists = self.reader.check_booking_still_active(BID=BID)
        conn = self.database
        cursor = None
        cursor = conn.cursor(())
        query = """
            INSERT INTO RegisteredBookingAttendees
            (BID, RegisteredAttendee)
            VALUES ( %s, %s)
        """

        values = (BID, RUID)

        cursor.execute(query, values)
        conn.commit()
        # cursor.close()
        return True

    def associate_unregistered_user_with_booking(self, BID: int, URUID: str):
        """Generic function for associating a booking to Registered Users \n
        TRUE == ASSOCIATION RECORD ADDED \n
        FALSE == ASSOCIATION RECORD FAILED"""
        conn = self.database
        query = """
            INSERT INTO UnregisteredBookingAttendees
            (BID, unregisteredAttendee)
            VALUES (%s, %s)
        """

        values = (BID, URUID)
        cursor = None
        cursor = conn.cursor(())
        cursor.execute(query, values)
        conn.commit()
        return True

    def delete_booking(self, BID: int):
        """Generic function to delete a booking from the Database \n
        NOTE: REMOVES MEETING OWNER AND ATTENDEES ASSOCIATED WITH BOOKING FROM THE RELATION TABLE \n
        TRUE == BOOKING DELETED \n
        FALSE == BOOKING DIDNT EXIST OR OTHER FAILURE"""
        conn = self.database
        try:
            cursor = None
            cursor = conn.cursor(())
            attempt_delete_association = self.delete_association(BID=BID)
            attempt_free_room = self.update_room_as_available(BID=BID)

            # print(attempt_delete_association)
            # print(attempt_free_room)

            if attempt_delete_association and attempt_free_room:
                cursor.execute("DELETE FROM Booking WHERE BID = %s", (BID,))
                conn.commit()

                return True

        except Exception as e:
            conn.rollback()
            # print("DELETE ERROR: ", e)
            return False, str(e)

    def delete_association(self, BID: int):
        """Generic function to remove an association between a Booking and an Attendee \n
        NOTE: ASSOCIATION BETWEEN BOOKING AND ALL RELATED ATTENDEES MUST BE DELETED BEFORE A BOOKING IS DELETED
        TRUE == ASSOCIATION DELETED \n
        FALSE == ASSOCIATION DELETION ERROR + ERROR MSG"""
        conn = self.database
        try:
            cursor = None
            cursor = conn.cursor(())
            cursor.execute(
                "DELETE FROM RegisteredBookingAttendees WHERE BID = %s", (BID,)
            )
            conn.commit()

            cursor.execute(
                "DELETE FROM UnregisteredBookingAttendees WHERE BID = %s", (BID,)
            )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            # print("DELETE ERROR: ", e)
            return False, str(e)

    def reset_confirmed_attendees(self, BID: int):
        """Generic function to reset all RSVPs for a booking when the meeting time, date, duration, or room is updated \n
        NOTE: CALLED WHEN UPDATING A BOOKING'S TIME, DATE, DURATION, OR ROOM \n
        TRUE == RSVPS RESET \n
        FALSE == RSVPS NOT RESET"""
        conn = self.database
        booking_info = self.reader.get_booking_information_of_specific_booking(BID)
        meeting_owner = booking_info[5]

        try:
            cursor = None
            cursor = conn.cursor(())
            cursor.execute(
                "DELETE FROM RegisteredBookingAttendees WHERE BID = %s AND registeredAttendee != %s",
                (BID, meeting_owner),
            )
            conn.commit()

            cursor.execute(
                "DELETE FROM UnregisteredBookingAttendees WHERE BID = %s", (BID,)
            )

            cursor.execute(
                "UPDATE Booking SET numberOfConfirmations = %s WHERE BID = %s",
                (1, BID),
            )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            # print("DELETE ERROR: ", e)
            return False, str(e)

    def update_room_as_available(self, BID: int):
        """Generic function to update the database that a room is now available when deleting a booking \n
        NOTE: CALLED WHEN DELETING A BOOKING \n
        TRUE == ROOM UPDATED AS AVAILABLE \n
        FALSE == ROOM NOT UPDATED"""
        conn = self.database
        try:
            cursor = None
            cursor = conn.cursor(())
            cursor.execute(
                "DELETE FROM RoomsAssociatedWithBookings WHERE BID = %s", (BID,)
            )
            conn.commit()

            return True

        except Exception as e:
            conn.rollback()
            # print("UPDATE ERROR: ", e)
            return False, str(e)

    def update_meeting_time(self, BID: int, new_start_time: str):
        """Generic function to update a booking's meeting time, given a Booking ID, and a new meeting time \n
        TRUE == BOOKING UPDATED AS AVAILABLE \n
        FALSE == BOOKING NOT UPDATED"""
        conn = self.database
        # First check if new start time is valid:
        try:
            previous_booking = self.reader.get_booking_information_of_specific_booking(
                BID
            )

            check = self.reader.check_for_room_availability(
                previous_booking[0],
                previous_booking[1],
                new_start_time,
                previous_booking[3],
                BID=BID,
            )

        except Exception as e:
            conn.rollback()
            # print("UPDATE ERROR: ", e)
            return False, str(e)

        if check:
            try:
                cursor = None
                cursor = conn.cursor(())
                cursor.execute(
                    "UPDATE Booking SET startTime = %s  WHERE BID = %s",
                    (new_start_time, BID),
                )
                conn.commit()

                return True

            except Exception as e:
                conn.rollback()
                # print("UPDATE ERROR: ", e)
                return False, str(e)

        return False, "New Meeting Time specified unavailable"

    def update_meeting_date(self, BID: int, new_date: str):
        """Generic function to update a booking's meeting date, given a Booking ID, and a new meeting date\n
        NOTE: CHECKS FOR OVERLAP WHEN UPDATING \n
        TRUE == BOOKING UPDATED \n
        FALSE == BOOKING NOT UPDATED"""
        conn = self.database
        # First check if new date is valid:
        try:
            previous_booking = self.reader.get_booking_information_of_specific_booking(
                BID
            )

            check = self.reader.check_for_room_availability(
                previous_booking[0],
                new_date,
                previous_booking[2],
                previous_booking[3],
                BID=BID,
            )

        except Exception as e:
            conn.rollback()
            # print("UPDATE ERROR: ", e)
            return False, str(e)

        if check:
            try:
                cursor = None
                cursor = conn.cursor(())
                cursor.execute(
                    "UPDATE Booking SET meetingDate = %s  WHERE BID = %s",
                    (new_date, BID),
                )
                conn.commit()

                return True

            except Exception as e:
                conn.rollback()
                # print("UPDATE ERROR: ", e)
                return False, str(e)

        return False, "New Meeting Date specified unavailable"

    def update_meeting_duration(self, BID: int, new_duration: str):
        """Generic function to update a booking's duration, given a Booking ID, and a new duration\n
        NOTE: CHECKS FOR OVERLAP WHEN UPDATING \n
        TRUE == BOOKING UPDATED \n
        FALSE == BOOKING NOT UPDATED"""
        conn = self.database
        # First check if new duration is valid:
        try:
            previous_booking = self.reader.get_booking_information_of_specific_booking(
                BID
            )

            check = self.reader.check_for_room_availability(
                previous_booking[0],
                previous_booking[1],
                previous_booking[2],
                new_duration,
                BID=BID,
            )

        except Exception as e:
            conn.rollback()
            # print("UPDATE ERROR: ", e)
            return False, str(e)

        if check:
            try:
                cursor = None
                cursor = conn.cursor(())
                cursor.execute(
                    "UPDATE Booking SET duration = %s  WHERE BID = %s",
                    (new_duration, BID),
                )
                conn.commit()

                return True

            except Exception as e:
                conn.rollback()
                # print("UPDATE ERROR: ", e)
                return False, str(e)

        return False, "New Meeting Duration specified unavailable"

    def update_meeting_room(self, BID: int, new_room: str):
        """Generic function to update a booking's room, given a Booking ID, and a new room\n
        NOTE: CHECKS FOR OVERLAP WHEN UPDATING \n
        TRUE == BOOKING UPDATED \n
        FALSE == BOOKING NOT UPDATED"""
        conn = self.database
        # First check if new room is available:
        try:
            previous_booking = self.reader.get_booking_information_of_specific_booking(
                BID
            )

            check = self.reader.check_for_room_availability(
                new_room,
                previous_booking[1],
                previous_booking[2],
                previous_booking[3],
                BID=BID,
            )

        except Exception as e:
            conn.rollback()
            # print("UPDATE ERROR: ", e)
            return False, str(e)

        if check:
            try:
                cursor = None
                cursor = conn.cursor(())
                cursor.execute(
                    "UPDATE Booking SET meetingRoom = %s  WHERE BID = %s",
                    (new_room, BID),
                )
                conn.commit()

                cursor.execute(
                    "UPDATE RoomsAssociatedWithBookings SET RID = %s  WHERE BID = %s",
                    (new_room, BID),
                )

                conn.commit()
                return True

            except Exception as e:
                conn.rollback()
                # print("UPDATE ERROR: ", e)
                return False, str(e)

        return False, "New Meeting Room specified is unavailable"

    def update_meeting_capacity(self, BID: int, new_capacity: int):
        """Generic function to update a booking's capacity, given a Booking ID, and a new capacity \n
        NOTE: CHECKS FOR VALID CAPACITY SPECIFIED WHEN UPDATING \n
        TRUE == BOOKING UPDATED \n
        FALSE == BOOKING NOT UPDATED"""
        conn = self.database
        cursor = None
        cursor = conn.cursor(())
        cursor.execute(
            "SELECT RID FROM RoomsAssociatedWithBookings WHERE BID = %s", (BID,)
        )
        RID = cursor.fetchone()[0]

        capcity_of_room_for_this_booking = self.reader.get_capacity_of_room(RID)

        if new_capacity <= capcity_of_room_for_this_booking:
            try:
                cursor.execute(
                    "UPDATE Booking SET meetingSize = %s  WHERE BID = %s",
                    (new_capacity, BID),
                )
                conn.commit()

                return True

            except Exception as e:
                conn.rollback()
                # print("UPDATE ERROR: ", e)
                return False, str(e)

        return (
            False,
            "New Meeting Capacity specified is too large for the room of the booking",
        )

    def increase_number_of_confirmations(self, BID: int):
        """Generic function to update a booking's number of confirmed attendees by 1 \n
        TRUE == BOOKING UPDATED \n
        FALSE == BOOKING NOT UPDATED"""
        conn = self.database
        cursor = None
        cursor = conn.cursor(())
        cursor.execute(
            "SELECT numberOfConfirmations FROM Booking WHERE BID = %s",
            (BID,),
        )

        curNumberOfCons = cursor.fetchone()[0]
        curNumberOfCons += 1
        try:

            cursor.execute(
                "UPDATE Booking SET numberOfConfirmations = %s WHERE BID = %s",
                (curNumberOfCons, BID),
            )

            conn.commit()

            return True

        except Exception as e:
            conn.rollback()
            # print("UPDATE ERROR: ", e)
            return False, str(e)

    def update_booking_reminder_sent(self, BID: int):
        """Generic function to update a booking's number of confirmed attendees by 1 \n
        TRUE == BOOKING UPDATED \n
        FALSE == BOOKING NOT UPDATED"""
        conn = self.database
        try:
            cursor = None
            cursor = conn.cursor(())
            cursor.execute(
                "UPDATE Booking SET reminderSent = %s WHERE BID = %s",
                (1, BID),
            )

            conn.commit()

            return True

        except Exception as e:
            conn.rollback()
            # print("UPDATE ERROR: ", e)
            return False, str(e)

    def update_bookings_shareable_link(self, shareable_link: str, BID: int):
        """Generic function to update a booking's shareable link \n
        TRUE == BOOKING UPDATED \n
        FALSE == BOOKING NOT UPDATED"""
        conn = self.database
        try:
            cursor = None
            cursor = conn.cursor(())
            cursor.execute(
                "UPDATE Booking SET shareableLink = %s WHERE BID = %s",
                (shareable_link, BID),
            )

            conn.commit()

            return True

        except Exception as e:
            conn.rollback()
            # print("UPDATE ERROR: ", e)
            return False, str(e)

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
    #                 conn.close()
    #         except Exception:
    #             pass

    # def __del__(self):
    #     # Best-effort safety net (routes/services can also call .close() explicitly).
    #     try:
    #         self.close()
    #     except Exception:
    #         pass
