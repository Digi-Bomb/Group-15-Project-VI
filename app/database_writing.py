from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices


class DatabaseWritingServices:
    def __init__(self, database: DatabaseConnection, reader: DatabaseReadingServices):
        self.database = database
        self.conn = self.database.connect()
        self.cursor = self.conn.cursor()
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

        if not checkExists:

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

            self.cursor.execute(query, values)
            self.conn.commit()
            return True

        return False, "User already registered"

    def create_new_booking(
        self,
        meeting_date: str,
        start_time: str,
        duration: str,
        meeting_owner: str,
        meeting_room: str,
        meeting_capacity: int,
    ):
        """Generic function for adding a booking to the Database \n
        NOTE: CHECKS FOR EXISTING BOOKED ROOMS AND ROOM CAPACITY \n
        TRUE == BOOKING ADDED, AND RETURNS GENERATED BID \n
        FALSE == BOOKING DETAILS FAILED; ROOM TAKEN OR MEETING SIZE TOO LARGE"""

        checkAvailable = self.reader.check_for_room_availability(
            room_number=meeting_room
        )

        roomCapacity = self.reader.get_capacity_of_room(room_number=meeting_room)

        if checkAvailable:

            if meeting_capacity <= roomCapacity:
                query = """
                    INSERT INTO Booking
                    (meetingDate, startTime, duration, meetingOwner, meetingRoom, meetingSize)
                    VALUES ( %s, %s, %s, %s, %s, %s)
                """
                values = (
                    meeting_date,
                    start_time,
                    duration,
                    meeting_owner,
                    meeting_room,
                    meeting_capacity,
                )

                self.cursor.execute(query, values)
                self.conn.commit()
                booking_id = (
                    self.cursor.lastrowid
                )  # POTENTIALLY unsafe for multiple users (?)

                attempt_to_book_room = self.book_a_room_after_booking(
                    booking_id, meeting_room
                )
                attempt_to_associate = self.associate_registered_user_with_booking(
                    booking_id, meeting_owner
                )

                if attempt_to_associate and attempt_to_book_room:

                    self.cursor.close()
                    return True, (booking_id)
                else:
                    return False, "Unable to associate"

            else:
                return (
                    False,
                    "Room IS Available, but the specified meetingSize is greater than the room's capacity",
                )

        return False, "Room is NOT Available"

    def book_a_room_after_booking(self, BID: int, meeting_room):
        """Generic function for assignment of a room to a particular booking \n
        TRUE == ABLE TO BOOK ROOM \n
        FALSE == ROOM ALREADY BOOKED"""

        try:
            query = """
                UPDATE Room
                SET BID = (%s)
                WHERE roomNumber = (%s)
                AND BID IS NULL
            """

            values = (BID, meeting_room)

            self.cursor.execute(query, values)
            self.conn.commit()

            return True

        except Exception as e:
            self.conn.rollback()
            print("INSERT ERROR: ", e)
            return False, str(e)

    def associate_registered_user_with_booking(self, BID: int, RUID: str):
        """Generic function for associating a booking to Registered Users \n
        NOTE: CALLED AUTOMATICALLY WHEN A BOOKING IS CREATED, ATTACHES MEETING OWNER TO BOOKING IN THIS TABLE \n
        TRUE == ASSOCIATION RECORD ADDED \n
        FALSE == ASSOCIATION RECORD FAILED"""

        # isBookingExists = self.reader.check_booking_still_active(BID=BID)

        query = """
            INSERT INTO RegisteredBookingAttendees
            (BID, RegisteredAttendee)
            VALUES ( %s, %s)
        """

        values = (BID, RUID)

        self.cursor.execute(query, values)
        self.conn.commit()
        self.cursor.close()
        return True

    def associate_unregistered_user_with_booking(self, BID: int, URUID: str):
        """Generic function for associating a booking to Registered Users \n
        TRUE == ASSOCIATION RECORD ADDED \n
        FALSE == ASSOCIATION RECORD FAILED"""

        query = """
            INSERT INTO UnregisteredBookingAttendees
            (BID, unregisteredAttendee)
            VALUES ( %s, %s)
        """

        values = (BID, URUID)

        self.cursor.execute(query, values)
        self.conn.commit()
        return True

    def delete_booking(self, BID: int):
        """Generic function to delete a booking from the Database \n
        NOTE: REMOVES MEETING OWNER AND ATTENDEES ASSOCIATED WITH BOOKING FROM THE RELATION TABLE \n
        TRUE == BOOKING DELETED \n
        FALSE == BOOKING DIDNT EXIST OR OTHER FAILURE"""

        try:
            attempt_delete_association = self.delete_association(BID=BID)
            attempt_free_room = self.update_room_as_available(BID=BID)

            if attempt_delete_association and attempt_free_room:
                self.cursor.execute("DELETE FROM Booking WHERE BID = %s", (BID,))
                self.conn.commit()

                return True

        except Exception as e:
            self.conn.rollback()
            print("DELETE ERROR: ", e)
            return False, str(e)

    def delete_association(self, BID: int):
        """Generic function to remove an association between a Booking and an Attendee \n
        NOTE: ASSOCIATION BETWEEN BOOKING AND ALL RELATED ATTENDEES MUST BE DELETED BEFORE A BOOKING IS DELETED
        TRUE == ASSOCIATION DELETED \n
        FALSE == ASSOCIATION DELETION ERROR + ERROR MSG"""

        try:
            self.cursor.execute(
                "DELETE FROM RegisteredBookingAttendees WHERE BID = %s", (BID,)
            )
            self.conn.commit()

            self.cursor.execute(
                "DELETE FROM UnregisteredBookingAttendees WHERE BID = %s", (BID,)
            )

            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            print("DELETE ERROR: ", e)
            return False, str(e)

    def update_room_as_available(self, BID: int):
        """Generic function to update the database that a room is now available when deleting a booking \n
        NOTE: CALLED WHEN DELETING A BOOKING \n
        TRUE == ROOM UPDATED AS AVAILABLE \n
        FALSE == ROOM NOT UPDATED"""

        try:
            self.cursor.execute("UPDATE Room SET BID = NULL WHERE BID = %s", (BID,))
            self.conn.commit()

            return True

        except Exception as e:
            self.conn.rollback()
            print("UPDATE ERROR: ", e)
            return False, str(e)
