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
        BID="",
    ):
        """Generic function for adding a user to the Database \n
        NOTE: CHECKS FOR EXISTING USERS, NEEDS EMAIL VALIDATION(?) \n
        TRUE == USER ADDED \n
        FALSE == USER ALREADY EXISTED"""

        checkExists = self.reader.check_if_user_is_registered_already(
            username=username, email=email
        )

        if not checkExists:
            if BID:
                print("inserting with BID")
                query = """
                    INSERT INTO RegisteredUser
                    (BID, username, email, pass, firstName, lastName)
                    VALUES ( %s, %s, %s, %s, %s, %s)
                """
                values = (BID, username, email, password, first_name, last_name)

            else:
                query = """
                    INSERT INTO RegisteredUser
                    (username, email, pass, firstName, lastName)
                    VALUES ( %s, %s, %s, %s, %s)
                """
                values = (username, email, password, first_name, last_name)

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
        TRUE == BOOKING ADDED \n
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

                attempt_to_associate = self.associate_registered_user_with_booking(
                    booking_id, meeting_owner
                )
                return True

            else:
                return (
                    False,
                    "Room IS Available, but the specified meetingSize is greater than the room's capacity",
                )

        return False, "Room is NOT Available"

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
        return True
