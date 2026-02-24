from app.database_connection import DatabaseConnection
from app.database_reading import DatabaseReadingServices
from app.database_writing import DatabaseWritingServices
from werkzeug.security import generate_password_hash


def load_conn():
    conn = DatabaseConnection.connect()
    # assert conn
    return conn


def load_reader():
    conn = load_conn()
    reader = DatabaseReadingServices(conn)
    return reader


def load_writer():
    conn = load_conn()
    reader = load_reader()
    writer = DatabaseWritingServices(conn, reader)

    return writer


def test_load_conns():
    response = load_conn
    assert response


def test_load_reader():
    reader = load_reader()
    assert reader


def test_get_registered_email_from_username():

    reader = load_reader()

    email = reader.get_specific_registered_user_email_given_username("testuser")

    assert email == "testuser1@gmail.com"


def test_validate_user_information():

    reader = load_reader()

    password = "PassW0rd"
    password = generate_password_hash(password)
    valid = reader.validate_user_information(
        "testuser", "testuser1@gmail.com", password
    )

    assert valid[0] == True
    assert valid[1] == "Successful Login"


def test_getting_meeting_owner():

    reader = load_reader()

    owner = reader.get_specific_meeting_owner_for_booking(1083)

    assert owner == 1005


def test_getting_username():

    reader = load_reader()

    user = reader.get_username_via_RUID(1005)

    assert user == "testuser"


# def test_getting_meetings_owned_no_meetings():
def test_getting_meetings_owned_several_meetings():

    reader = load_reader()

    meetings = reader.get_meetings_owned_by_registered_user(1005)
    assert meetings == (1083, 1084, 1085, 1086)


# def test_get_registered_users_in_booking_several_users


def test_get_registered_users_in_booking_one_user():

    reader = load_reader()

    registered_users = reader.get_registered_users_associated_with_booking_ID(1083)
    assert registered_users == 1005


# def test_get_unregistered_users_in_booking_no_users
def test_get_unregistered_users_in_booking_one_user():

    reader = load_reader()

    unregistered_users = reader.get_unregistered_users_associated_with_booking_ID(1083)
    assert unregistered_users == 1005  # FIX THIS!!!


def test_check_for_pre_existing_user_true_for_email_only():

    reader = load_reader()

    exists = reader.check_if_user_is_registered_already(
        "testuder", "testuser1@gmail.com"
    )
    assert exists


def test_check_for_pre_existing_user_true_for_username_only():

    reader = load_reader()

    exists = reader.check_if_user_is_registered_already(
        "testuser", "testuser2@gmail.com"
    )
    assert exists


def test_check_for_pre_existing_user_false():

    reader = load_reader()

    exists = reader.check_if_user_is_registered_already(
        "testuder", "testuser2@gmail.com"
    )
    assert not exists


# def test_check_for_available_unregistered_nickname_true():

#     connection = load_conn()
#     reader = load_reader()

#     available = reader.check_if_unregistered_user_nickname_is_taken_for_specific_meeting()
#     assert available

# def test_check_for_available_unregistered_nickname_false():

#     connection = load_conn()
#     reader = load_reader()

#     available = reader.check_if_unregistered_user_nickname_is_taken_for_specific_meeting()
#     assert not available


def test_checking_room_availability_true():

    reader = load_reader()

    available = reader.check_for_room_availability(
        "2B14", "2006-02-18", "08:00:00", "03:00:00"
    )

    assert available


def test_checking_room_availability_false_same_start_time():

    reader = load_reader()

    available = reader.check_for_room_availability(
        "1F05", "2006-02-04", "15:00:00", "03:00:00"
    )

    assert not available


def test_checking_room_availability_false_duration_leaks_into_existing_booking():

    reader = load_reader()

    available = reader.check_for_room_availability(
        "1F05", "2006-02-04", "12:00:00", "03:30:00"
    )

    assert not available


def test_checking_room_availability_false_existing_duration_leaks_into_booking():

    reader = load_reader()

    available = reader.check_for_room_availability(
        "1F05", "2006-02-04", "10:30:00", "01:00:00"
    )

    assert not available


def test_getting_capacity_acurate():

    reader = load_reader()

    capacity = reader.get_capacity_of_room("1F05")
    assert capacity == 100


def test_getting_capacity_inacurate():

    reader = load_reader()

    capacity = reader.get_capacity_of_room("1C09")
    assert not capacity == 100


def test_getting_branch_location():

    reader = load_reader()

    branch = reader.get_branch_location_of_room_associated_with_room_number("1F05")
    assert branch == "Waterloo Campus"


# def get_rooms(self, building: str | None = None):
# def test_getting_all_rooms():

#     connection = load_conn()
#     reader = load_reader()

#     all_rooms = reader.get_rooms


def test_getting_booking_start_and_end_times():

    reader = load_reader()

    times = reader.get_booking_start_and_end_times_for_specific_room_include_date(
        "1F05"
    )

    expected_times = []

    time_for_booking_tupple1 = ("2006-04-02", "15:00:00", "18:00:00")
    time_for_booking_tupple2 = ("2006-04-02", "12:00:00", "15:00:00")
    time_for_booking_tupple3 = ("2006-04-02", "08:00:00", "11:00:00")

    expected_times.append(time_for_booking_tupple1)
    expected_times.append(time_for_booking_tupple2)
    expected_times.append(time_for_booking_tupple3)

    assert times == expected_times


def test_create_new_user_success():

    writer = load_writer()
    test_pass = "IamATest"
    test_pass = generate_password_hash(test_pass)
    # need to randomly generate a running user to avoid double up
    user_info = ("testrunninguser", "testrunning@gmail.com", "bleh", "blah", test_pass)
    adding = writer.create_new_user(
        user_info[0], user_info[1], user_info[2], user_info[3], user_info[4]
    )

    assert adding


def test_create_new_user_failure():

    writer = load_writer()
    test_pass = "IamATest"
    test_pass = generate_password_hash(test_pass)
    user_info = ("testrunninguser", "testrunninggmail.com", "bleh", "blah", test_pass)
    adding = writer.create_new_user(
        user_info[0], user_info[1], user_info[2], user_info[3], user_info[4]
    )

    assert not adding[0]


def test_create_new_unregistered_user_success_no_email():

    writer = load_writer()
    adding = writer.create_new_unregistered_user(1087, "tester")
    assert adding[0]


def test_create_new_unregistered_user_success_with_email():

    writer = load_writer()
    adding = writer.create_new_unregistered_user(
        1087, "testee", email="tester@gmail.com"
    )
    assert adding[0]


def test_create_new_unregistered_user_failure_no_nickname():

    writer = load_writer()
    adding = writer.create_new_unregistered_user(1087, "")
    assert not adding[0]


def test_create_new_unregistered_user_failure_nickname_taken():

    writer = load_writer()
    adding = writer.create_new_unregistered_user(1087, "tester")
    assert not adding[0]


def test_create_new_unregistered_user_failure_invalid_BID():

    writer = load_writer()
    adding = writer.create_new_unregistered_user(1000, "testeee")
    assert not adding[0]


def test_create_new_booking_success():

    writer = load_writer()

    booking_info = ("2008-02-02", "08:00:00", "03:00:00", 1005, "1F05", 40)

    booking_created = writer.create_new_booking(
        booking_info[0],
        booking_info[1],
        booking_info[2],
        booking_info[3],
        booking_info[4],
    )
    assert booking_created[0]


def test_create_new_booking_failure_room_already_booked_at_datetime():

    writer = load_writer()

    booking_info = ("2008-02-02", "08:00:00", "03:00:00", 1005, "1F05", 40)

    booking_created = writer.create_new_booking(
        booking_info[0],
        booking_info[1],
        booking_info[2],
        booking_info[3],
        booking_info[4],
    )
    assert booking_created[0] == False
    assert booking_created[1] == "Room is NOT Available"


def test_create_new_booking_failure_booking_size_too_large():

    writer = load_writer()

    booking_info = ("2008-02-02", "12:00:00", "03:00:00", 1005, "1F05", 110)

    booking_created = writer.create_new_booking(
        booking_info[0],
        booking_info[1],
        booking_info[2],
        booking_info[3],
        booking_info[4],
    )
    assert booking_created[0] == False
    assert (
        booking_created[1]
        == "Room IS Available, but the specified meetingSize is greater than the room's capacity"
    )


def test_deleting_booking_success():

    writer = load_writer()

    deletion = writer.delete_booking(1084)
    assert deletion


def test_deleting_booking_failure_invalid_BID():

    writer = load_writer()

    deletion = writer.delete_booking(1000)
    assert deletion[0] == False


def test_update_room_as_available_failure_invalid_BID():

    writer = load_writer()

    updated = writer.update_room_as_available(1000)

    assert not updated[0]


def test_update_meeting_time_success():

    writer = load_writer()

    updated = writer.update_meeting_time(1087, "15:00:00")
    assert updated


def test_update_meeting_time_failure_invalid_bid():

    writer = load_writer()

    updated = writer.update_meeting_time(1000, "15:00:00")
    assert not updated[0]


def test_update_meeting_time_failure_overlap_in_meeting_time():

    writer = load_writer()

    updated = writer.update_meeting_time(1087, "08:00:00")
    assert not updated[0]


def test_update_meeting_date_success():

    writer = load_writer()

    updated = writer.update_meeting_date(1087, "2006-03-05")
    assert updated


def test_update_meeting_date_failure_invalid_bid():

    writer = load_writer()

    updated = writer.update_meeting_date(1000, "2006-03-05")
    assert not updated[0]


def test_update_meeting_date_failure_overlap_in_meeting_date_and_time():

    writer = load_writer()

    updated = writer.update_meeting_date(1087, "2026-02-18")
    assert not updated[0]


def test_update_meeting_duration_success():

    writer = load_writer()

    updated = writer.update_meeting_duration(1087, "02:00:00")
    assert updated


def test_update_meeting_duration_failure_invalid_bid():

    writer = load_writer()

    updated = writer.update_meeting_duration(1000, "02:00:00")
    assert not updated[0]


def test_update_meeting_duration_failure_overlap_in_endtime_with_new_duration():

    writer = load_writer()

    updated = writer.update_meeting_duration(1087, "08:00:00")
    assert not updated[0]


def test_update_meeting_room_success():

    writer = load_writer()

    updated = writer.update_meeting_room(1087, "1G10")
    assert updated


def test_update_meeting_room_failure_invalid_bid():

    writer = load_writer()

    updated = writer.update_meeting_room(1000, "1G10")
    assert not updated[0]


def test_update_meeting_room_failure_no_such_room():

    writer = load_writer()

    updated = writer.update_meeting_room(1087, "1G01")
    assert not updated[0]


def test_update_meeting_room_failure_overlap_in_room_availability():

    writer = load_writer()

    updated = writer.update_meeting_room(1087, "1F05")
    assert not updated[0]


def test_update_meeting_capacity_success():

    writer = load_writer()

    updated = writer.update_meeting_capacity(1087, 10)
    assert updated


def test_update_meeting_capacity_failure_capacity_too_large():

    writer = load_writer()

    updated = writer.update_meeting_capacity(1087, 105)
    assert not updated[0]


def test_update_meeting_capacity_failure_invalid_bid():

    writer = load_writer()

    updated = writer.increase_number_of_confirmations(1000, 10)
    assert not updated[0]
    # Maybe poll for the updated number of confirmations too


def test_update_number_of_confirmations_success():

    writer = load_writer()

    updated = writer.increase_number_of_confirmations(1087)
    assert updated


def test_update_reminder_sent_to_true_success():

    writer = load_writer()

    updated = writer.update_booking_reminder_sent(1087)
    assert updated


def test_update_reminder_sent_to_true_failure_invalid_BID():

    writer = load_writer()

    updated = writer.update_booking_reminder_sent(1000)
    assert not updated[0]


def test_update_shareable_link_success():

    writer = load_writer()

    updated = writer.update_bookings_shareable_link(
        1087, "b7049b44-f929-4e3a-9fe1-63f0fw2dc386"
    )
    assert updated


def test_update_shareable_link_failure_shareable_link_too_long():

    writer = load_writer()

    updated = writer.update_bookings_shareable_link(
        1087,
        "b7049b44-f929-4e3a-9fe1-63f0fccdc386b7049b44-f929-4e3a-9fe1-63f0fccdc386b7049b44-f929-4e3a-9fe1-63f0fccdc386",
    )
    assert not updated[0]


def test_update_shareable_link_failure_invalid_BID():

    writer = load_writer()

    updated = writer.update_bookings_shareable_link(
        1000, "c7579b44-f329-4e4a-9fe1-63f0fw2dc386"
    )
    assert not updated[0]

    # def update_bookings_shareable_link(self, shareable_link: str, BID: int):
