"""
@file routes.py
@brief Booking blueprint routes for creating, viewing, editing, and RSVPing to bookings.
@details
This module defines the Flask Blueprint responsible for booking-related HTTP endpoints:
- Create booking (GET/POST/OPTIONS)
- View booking details (GET)
- Edit booking (GET/PATCH/DELETE)
- RSVP via shareable link (GET/POST)

The routes rely on the application's database service layer:
- DatabaseConnection
- DatabaseReadingServices
- DatabaseWritingServices

And utilize:
- WTForms BookingForm for input validation
- TimeManager for time calculations
- AuditLogger for security/audit event logging
- EmailNotificationService for notification emails

@note
These routes use session-based authentication for registered-user flows.
Some endpoints use redirects and flash messages rather than JSON responses.
"""

import random
from flask import Blueprint, render_template, request, redirect, flash, session, abort, make_response
from datetime import datetime, timedelta
import uuid

from booking.booking import Booking
from notifications.email_notification_service import EmailNotificationService
from .booking_service import BookingService
from forms import BookingForm
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices
from database_writing import DatabaseWritingServices
from time_manager import TimeManager

from audit_logging.audit_logger import AuditLogger

## @brief Blueprint for booking-related routes.
## @details All booking endpoints are registered under this blueprint.
booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/booking", methods=["GET", "POST", "OPTIONS"])
def create_booking():
    """
    @brief Create a new booking or render the booking creation form.
    @details
    - OPTIONS: Returns allowed methods with HTTP 204 and no body.
    - GET: Renders the booking creation page. If query string includes `date`,
      it attempts to prefill the form date.
    - POST: Validates the submitted form and creates a booking if the room/time slot
      is available. On success redirects to the booking detail page.

    Authentication:
    - Requires a logged-in user (session["user_id"]).

    Query string parameters (GET):
    @param room_number str Room identifier to book (required for creation flow).
    @param date str Optional date string in format "YYYY-MM-DD" to prefill form.

    Form fields (POST):
    - meeting_date (date)
    - start_time (time)
    - end_time (time)
    - meeting_capacity (int)

    Side effects:
    - Creates DB records via DatabaseWritingServices.create_new_booking().
    - Writes audit events via AuditLogger.
    - Uses flash messages for user feedback.
    - Generates a UUID shareable_link.

    @return
    - OPTIONS: Flask Response with status 204 and Allow header.
    - GET: Rendered "booking.html".
    - POST success: Redirect to "/booking/<booking_id>".
    - POST failure: Redirect back to "/booking?room_number=...&date=...".
    - Auth failure: Redirect to "/login".

    @throws abort
    - Does not directly abort, but may redirect on validation/auth problems.
    """
    # OPTIONS
    if request.method == "OPTIONS":
        response = make_response("", 204)  # no content, just headers no body
        response.headers["Allow"] = "GET, POST, OPTIONS"
        return response

    db = DatabaseConnection()
    db.connect()
    reader = DatabaseReadingServices(db)
    writer = DatabaseWritingServices(db, reader)

    audit_logger = AuditLogger()

    user_id = session.get("user_id")
    room_number = request.args.get("room_number", "").strip()
    date_qs = request.args.get("date", "").strip()  # "YYYY-MM-DD" from query string

    if not user_id:
        audit_logger.log_audit_event(
            "Unauthorized booking creation attempt",
            "Attempt to access booking creation without being logged in.",
        )
        flash("Please log in to create a booking.", "warning")
        return redirect("/login")

    if not room_number:
        audit_logger.log_audit_event(
            "Booking creation failed - no room selected",
            f"User ID {user_id} attempted to create a booking without selecting a room first.",
        )
        flash("No room selected.", "error")
        return redirect("/")

    form = BookingForm()
    room = reader.get_room_data_given_room_number(room_number)
    if not room:
        audit_logger.log_audit_event(
            "Booking creation failed - invalid room",
            f"User ID {user_id} attempted to create a booking with invalid room number: {room_number}.",
        )
        flash("Invalid room selected.", "error")
        return redirect("/")

    # GET: prefill date safely (string -> date object)
    if request.method == "GET" and date_qs:
        try:
            form.meeting_date.data = datetime.strptime(date_qs, "%Y-%m-%d").date()
        except ValueError:
            audit_logger.log_audit_event(
                "Booking creation - invalid date format in query string",
                f"User ID {user_id} provided invalid date format in query string: {date_qs}.",
            )
            flash("Invalid date format in URL. Use YYYY-MM-DD.", "error")

    # POST
    if form.validate_on_submit():
        # WTForms TimeField gives datetime.time, convert to "HH:MM:SS" required by DB logic
        start_time_str = form.start_time.data.strftime("%H:%M") + ":00"
        meeting_date = form.meeting_date.data.strftime("%Y-%m-%d")
        end_time_str = form.end_time.data.strftime("%H:%M") + ":00"

        # calculate duration from start & end time
        duration = TimeManager.get_duration_from_start_time_and_end_time(start_time_str, end_time_str)

        shareable_link = str(uuid.uuid4())
        create_booking = writer.create_new_booking(
            meeting_date,
            start_time=start_time_str,
            duration=duration,
            meeting_owner=user_id,
            meeting_room=room_number,
            meeting_capacity=form.meeting_capacity.data,
            shareable_link=shareable_link,
        )

        if not create_booking[0]:
            if create_booking[1] == "Room is NOT Available":
                audit_logger.log_audit_event(
                    "Booking creation failed - time slot unavailable",
                    f"User ID {user_id} attempted to create a booking for room {room_number} on {meeting_date} "
                    f"at {start_time_str} for 2 hr, but the time slot was already booked.",
                )
                flash(
                    "The selected time slot is already booked. Please choose a different time.",
                    "error",
                )
            else:
                audit_logger.log_audit_event(
                    "Booking creation failed - database error",
                    f"User ID {user_id} attempted to create a booking but encountered a database error: {create_booking[1]}",
                )
                flash("Failed to create booking.", "error")

            # keep user on same room/date page instead of losing query params
            safe_date = form.meeting_date.data.strftime("%Y-%m-%d") if form.meeting_date.data else ""
            return redirect(f"/booking?room_number={room_number}&date={safe_date}")

        audit_logger.log_audit_event(
            "Booking created",
            f"User ID {user_id} created a booking for room {room_number} on {meeting_date} at {start_time_str} "
            f"for {duration} hours with booking ID {create_booking[1]}.",
        )
        flash("Booking created!", "success")
        return redirect(f"/booking/{create_booking[1]}")

    return render_template("booking.html", form=form, mode="create", room=room)


@booking_bp.route("/booking/<int:booking_id>", methods=["GET"])
def view_booking(booking_id):
    """
    @brief Display a booking (meeting) detail page.
    @details
    Fetches booking information, room information, attendee list, and existing booked
    times for the room. Renders a meeting page including time slot display.

    @param booking_id int Booking identifier from the URL path.

    Side effects:
    - Writes audit events.
    - Uses abort(404) if booking/room/attendee/times data is missing.

    @return Rendered "meeting.html" template.

    @throws abort
    - 404 if booking not found
    - 404 if room not found
    - 404 if attendees not found
    - 404 if booked_times not found
    """
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    audit_logger = AuditLogger()

    booking = reader.get_booking_information_of_specific_booking(booking_id)

    # 1) FIRST validate booking exists and has expected shape
    if not booking:
        audit_logger.log_audit_event(
            "View booking failed - booking not found",
            f"User attempted to view booking with ID {booking_id} but it was not found in the database.",
        )
        abort(404, description="Booking not found")

    # 2) NOW it’s safe to index booking[0]
    room_number = booking[0]

    room = reader.get_room_data_given_room_number(room_number)
    if not room:
        audit_logger.log_audit_event(
            "Get Room failed - couldn't get room data given room number",
            f"User attempted to view room with ID {room_number} but it was not found in the database.",
        )
        abort(404, description="Room not found")

    user_id = session.get("user_id")

    # UI time slots shown on the meeting page
    time_slots = [
        ("08:00", "8:00"),
        ("09:00", "9:00"),
        ("10:00", "10:00"),
        ("11:00", "11:00"),
        ("12:00", "12:00"),
        ("13:00", "13:00"),
        ("14:00", "14:00"),
        ("15:00", "15:00"),
        ("16:00", "16:00"),
        ("17:00", "17:00"),
        ("18:00", "18:00"),
        ("19:00", "19:00"),
        ("20:00", "20:00"),
    ]

    attendees = reader.get_list_of_registered_and_unregistered_attendees_with_user_info(booking_id)
    if not attendees:
        audit_logger.log_audit_event("Get attendees failed", "Get attendees failed for booking")
        abort(404, description="Attendees not found")

    booked_times = reader.get_booking_start_and_end_times_for_specific_room_include_date_with_BID(room_number)
    if not booked_times:
        audit_logger.log_audit_event("Get booked_times failed", "Get booked_times failed for booking")
        abort(404, description="booking_times not found")

    return render_template(
        "meeting.html",
        room=room,
        booking=booking,
        attendees=attendees,
        booked_times=booked_times,
        time_slots=time_slots,
        user=user_id,
    )


@booking_bp.route("/booking/<int:booking_id>/edit", methods=["GET", "PATCH", "DELETE"])
def edit_booking(booking_id):
    """
    @brief Edit or delete an existing booking.
    @details
    This endpoint supports three operations:
    - GET: Render a pre-filled edit form for the booking (owner-only).
    - PATCH: Accept a JSON payload to update one or more booking fields (owner-only).
    - DELETE: Delete the booking (owner-only).

    Authorization:
    - Requires session["user_id"] (logged in).
    - Requires the logged-in user to be the booking owner (booking[5] == user_id).

    PATCH JSON fields supported:
    @param meeting_date str "YYYY-MM-DD"
    @param start_time str "HH:MM" or "HH:MM:SS" (normalized to HH:MM:SS)
    @param duration str Duration format expected by DB layer
    @param meeting_room str Room identifier
    @param meeting_capacity int Capacity (validated/coerced to int)

    Side effects:
    - Updates DB fields via DatabaseWritingServices update_* methods.
    - Sends notification emails on PATCH/DELETE.
    - Resets confirmed attendees on PATCH (writer.reset_confirmed_attendees()).
    - Uses flash messages and redirects for outcome reporting.
    - Writes audit events.

    @param booking_id int Booking identifier from the URL path.

    @return
    - GET: Rendered "editbooking.html".
    - PATCH: Redirect to "/booking/<booking_id>" after update attempt.
    - DELETE: Redirect to "/" on success, else redirect back to booking page.

    @throws abort
    - 404 if booking not found
    - 403 if not booking owner
    """
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    writer = DatabaseWritingServices(db, reader)
    audit_logger = AuditLogger()

    user_id = session.get("user_id")
    if not user_id:
        audit_logger.log_audit_event(
            "Unauthorized booking edit attempt",
            f"Attempt to access booking edit for booking ID {booking_id} without being logged in.",
        )
        flash("Please log in to edit the booking.", "warning")
        return redirect("/login")

    booking = reader.get_booking_information_of_specific_booking(booking_id)

    if not booking:
        audit_logger.log_audit_event(
            "View booking failed - booking not found",
            f"User attempted to view booking with ID {booking_id} but it was not found in the database.",
        )
        abort(404, description="Booking not found")

    if booking[5] != user_id:
        audit_logger.log_audit_event(
            "Unauthorized booking edit attempt",
            f"User ID {user_id} attempted to edit booking ID {booking_id} but is not the booking owner.",
        )
        abort(403, description="You do not have permission to edit this booking")

    # GET: render edit form pre-filled
    if request.method == "GET":
        form = BookingForm()
        # populate form fields from booking object where possible
        try:
            b = booking[1]
            # booking meetingDate expected as string 'YYYY-MM-DD' or date-like
            if hasattr(b, "meetingDate") and b.meetingDate:
                try:
                    form.meeting_date.data = datetime.strptime(str(b.meetingDate), "%Y-%m-%d").date()
                except Exception:
                    pass

            if hasattr(b, "startTime") and b.startTime:
                try:
                    form.start_time.data = datetime.strptime(str(b.startTime), "%H:%M:%S").time()
                except Exception:
                    try:
                        form.start_time.data = datetime.strptime(str(b.startTime), "%H:%M").time()
                    except Exception:
                        pass

            if hasattr(b, "meetingSize") and b.meetingSize:
                try:
                    form.meeting_capacity.data = int(b.meetingSize)
                except Exception:
                    pass
        except Exception:
            pass

        current_room = reader.get_room_data_given_room_number((booking[0]))
        rooms = reader.get_rooms()

        start_str = booking[2]
        duration_str = booking[3]
        end_time = TimeManager.get_end_time_from_start_time_and_duration(start_str, duration_str)

        return render_template(
            "editbooking.html",
            form=form,
            booking=booking,
            current_room=current_room,
            end_time=end_time,
            rooms=rooms,
        )

    # PATCH: accept JSON payload to update one or more fields
    if request.method == "PATCH":
        updated_data = request.get_json() or {}

        # Track update outcomes
        success = True
        error_msg = None

        # Update date
        if "meeting_date" in updated_data:
            new_date = updated_data.get("meeting_date")
            result = writer.update_meeting_date(booking_id, new_date)
            if not result:
                success = False
                error_msg = (
                    result[1]
                    if isinstance(result, tuple) and len(result) > 1
                    else "Failed to update meeting date"
                )

        # Update start time
        if success and "start_time" in updated_data:
            new_start = updated_data.get("start_time")
            # normalize to HH:MM:SS if user provided HH:MM
            if new_start and len(new_start.split(":")) == 2:
                new_start = new_start + ":00"
            result = writer.update_meeting_time(booking_id, new_start)
            if not result:
                success = False
                error_msg = (
                    result[1]
                    if isinstance(result, tuple) and len(result) > 1
                    else "Failed to update start time"
                )

        # Update duration
        if success and "duration" in updated_data:
            new_duration = updated_data.get("duration")
            result = writer.update_meeting_duration(booking_id, new_duration)
            if not result:
                success = False
                error_msg = (
                    result[1]
                    if isinstance(result, tuple) and len(result) > 1
                    else "Failed to update duration"
                )

        # Update room
        if success and "meeting_room" in updated_data:
            new_room = updated_data.get("meeting_room")
            result = writer.update_meeting_room(booking_id, new_room)
            if not result:
                success = False
                error_msg = (
                    result[1]
                    if isinstance(result, tuple) and len(result) > 1
                    else "Failed to update meeting room"
                )

        # Update capacity
        if success and "meeting_capacity" in updated_data:
            try:
                new_cap = int(updated_data.get("meeting_capacity"))
            except Exception:
                new_cap = None
            if new_cap is None:
                success = False
                error_msg = "Invalid meeting_capacity specified"
            else:
                result = writer.update_meeting_capacity(booking_id, new_cap)
                if not result:
                    success = False
                    error_msg = (
                        result[1]
                        if isinstance(result, tuple) and len(result) > 1
                        else "Failed to update meeting capacity"
                    )

        if not success:
            flash(error_msg or "Failed to update booking.", "error")
            return redirect(f"/booking/{booking_id}")

        EmailNotificationService(DatabaseConnection()).send_booking_update_notification_email(booking_id)

        if writer.reset_confirmed_attendees(booking_id):
            flash("Booking updated successfully.", "success")
        else:
            flash("Booking updated, but failed to reset RSVPs and send notifications.", "warning")
        return redirect(f"/booking/{booking_id}")

    # DELETE: remove booking
    if request.method == "DELETE":
        EmailNotificationService(DatabaseConnection()).send_booking_delete_notification_email(booking_id)
        deleted = writer.delete_booking(booking_id)
        if deleted:
            flash("Booking deleted.", "success")
            return redirect("/")
        else:
            flash("Failed to delete booking.", "error")
            return redirect(f"/booking/{booking_id}")


@booking_bp.route("/rsvp/<string:link_id>", methods=["GET", "POST"])
def rsvp(link_id):
    """
    @brief RSVP to a booking using a shareable RSVP link.
    @details
    - GET: Render RSVP form (unregistered users allowed).
    - POST: Validate capacity and insert an unregistered attendee record.
      If successful, sends an email notification to the meeting owner,
      increments confirmations, and redirects to home.

    @param link_id str Shareable link UUID/token used to look up the booking.

    Capacity enforcement:
    - Reads current confirmations and compares against booking capacity.
    - If capacity reached, RSVP is rejected.

    Side effects:
    - DB writes: create_new_unregistered_user(), increase_number_of_confirmations()
    - Email: send_new_rsvp_notification_email()
    - Audit logging and flash messages.

    @return
    - GET: Rendered "rsvp.html"
    - POST success: Redirect to "/"
    - POST failure: Redirect back to RSVP page or home

    @throws abort
    - This route does not abort; it redirects with flash messages on errors.
    """
    db = DatabaseConnection()
    db.connect()
    reader = DatabaseReadingServices(db)
    writer = DatabaseWritingServices(db, reader)
    result = reader.get_booking_by_link_id(link_id)
    tm = TimeManager()
    audit_logger = AuditLogger()

    if isinstance(result, str) or (isinstance(result, tuple) and result[0] == "N"):
        audit_logger.log_audit_event(f"Failed RSVP attempt with invalid link_id: {link_id}")
        flash("No booking found for that shareable link ID.", "error")
        return redirect("/")

    booking_id = result

    # [0] room, [1] date, [2] start time, [3] duration, [4] "confirmed",
    # [5] owner ID, [6] reminder sent flag, [7]shareable link, [8]booking ID, [9] booking 'size'
    booking_info = reader.get_booking_information_of_specific_booking(booking_id)
    room = reader.get_room_data_given_room_number(booking_info[0])

    meeting_owner = reader.get_username_via_RUID(booking_info[5])

    start_str = booking_info[2]
    duration_str = booking_info[3]
    end_time = TimeManager.get_end_time_from_start_time_and_duration(start_str, duration_str)

    if request.method == "POST":
        name = request.form.get("guest_name")
        email = request.form.get("guest_email")

        # check for capacity before allowing RSVP
        current_confirmations = reader.get_number_of_confirmations_for_booking(booking_id)

        if (
            current_confirmations is not None
            and booking_info[9] is not None
            and current_confirmations >= booking_info[9]
        ):
            audit_logger.log_audit_event(
                f"Failed RSVP attempt for booking ID {booking_id} with name {name} and email {email} due to capacity limit reached."
            )
            flash("Sorry, this meeting has reached its capacity limit.", "error")
            return redirect("/")

        add_attendee = writer.create_new_unregistered_user(booking_id, name, email)
        if not add_attendee[0]:
            audit_logger.log_audit_event(
                f"Failed RSVP attempt for booking ID {booking_id} with name {name} and email {email} due to database error: {add_attendee[1]}"
            )
            flash(add_attendee[1], "error")
            return redirect(f"/rsvp/{link_id}")

        EmailNotificationService(DatabaseConnection()).send_new_rsvp_notification_email(
            booking_info[5], name, booking_id
        )

        # +1 to number of confirmations after successful create
        writer.increase_number_of_confirmations(booking_id)
        audit_logger.log_audit_event(f"Received new RSVP for booking ID {booking_id} from {name} ({email}).")
        flash("RSVP received. Thank you!", "success")
        return redirect("/")

    return render_template(
        "rsvp.html",
        room=room,
        booking=booking_info,
        end_time=end_time,
        start_time=start_str,
        meeting_owner=meeting_owner,
    )
