from flask import Blueprint, render_template, request, redirect, flash, session, abort
from datetime import datetime

from booking.booking import Booking
from .booking_service import BookingService
from forms import BookingForm
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices
from database_writing import DatabaseWritingServices

booking_bp = Blueprint("booking", __name__)


@booking_bp.route("/booking", methods=["GET", "POST"])
def create_booking():
    db = DatabaseConnection()
    db.connect()
    reader = DatabaseReadingServices(db)
    writer = DatabaseWritingServices(db, reader)

    user_id = session.get("user_id")
    room_number = request.args.get("room_number", "").strip()
    date_qs = request.args.get("date", "").strip()  # "YYYY-MM-DD" from query string

    if not user_id:
        flash("Please log in to create a booking.", "warning")
        return redirect("/login")

    if not room_number:
        flash("No room selected.", "error")
        return redirect("/")

    form = BookingForm()
    room = reader.get_room_data_given_room_number(room_number)
    if not room:
        flash("Invalid room selected.", "error")
        return redirect("/")

    # GET: prefill date safely (string -> date object)
    if request.method == "GET" and date_qs:
        try:
            form.meeting_date.data = datetime.strptime(
                date_qs, "%Y-%m-%d"
            ).date()  # swap to date format for form field
        except ValueError:
            flash("Invalid date format in URL. Use YYYY-MM-DD.", "error")

    # POST
    if form.validate_on_submit():
        # WTForms TimeField gives datetime.time, convert to "HH:MM:SS" required by DB logic
        start_time_str = form.start_time.data.strftime("%H:%M") + ":00"
        meeting_date = form.meeting_date.data.strftime("%Y-%m-%d")

        # debugging print data that prints ONLY after ctrl+C
        # print(
        #     meeting_date,
        #     start_time_str,
        #     "02:00:00",
        #     user_id,
        #     room_number,
        #     form.meeting_capacity,
        # )

        # meeting_date is a datetime.date from DateField (good)
        create_booking = writer.create_new_booking(
            meeting_date,
            start_time=start_time_str,
            duration="02:00:00",  # keep your default for now
            meeting_owner=user_id,
            meeting_room=room_number,
            meeting_capacity=form.meeting_capacity.data,
        )

        if not create_booking[0]:
            if create_booking[1] == "Room is NOT Available":
                flash(
                    "The selected time slot is already booked. Please choose a different time.",
                    "error",
                )
            else:
                flash("Failed to create booking.", "error")

            # keep user on same room/date page instead of losing query params
            safe_date = (
                form.meeting_date.data.strftime("%Y-%m-%d")
                if form.meeting_date.data
                else ""
            )
            return redirect(f"/booking?room_number={room_number}&date={safe_date}")

        flash("Booking created!", "success")
        return redirect(f"/booking/{create_booking[1]}")

    return render_template("booking.html", form=form, mode="create", room=room)


# rename to meeting for frontend?
@booking_bp.route("/booking/<int:booking_id>", methods=["GET"])
def view_booking(booking_id):
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)

    booking = reader.get_booking_information_of_specific_booking(booking_id)
    room = reader.get_room_data_given_room_number(
        getattr(booking[1], "meetingRoom", None)
    )
    if not booking[0]:
        abort(404, description="Booking not found")

    return render_template("meeting.html", room=room)


# GET: get booking info and prefill form for editing (only if owner)
# PATCH: accept JSON payload to update one or more fields (only if owner)
# DELETE: delete booking (only if owner)
@booking_bp.route("/booking/<int:booking_id>/edit", methods=["GET", "PATCH", "DELETE"])
def edit_booking(booking_id):
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    writer = DatabaseWritingServices(db, reader)

    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to edit the booking.", "warning")
        return redirect("/login")

    booking = reader.get_booking_information_of_specific_booking(booking_id)
    if not booking[0]:
        abort(404, description="Booking not found")

    if booking[1].booking_owner_id != user_id:
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
                    form.meeting_date.data = datetime.strptime(
                        str(b.meetingDate), "%Y-%m-%d"
                    ).date()
                except Exception:
                    pass

            if hasattr(b, "startTime") and b.startTime:
                try:
                    form.start_time.data = datetime.strptime(
                        str(b.startTime), "%H:%M:%S"
                    ).time()
                except Exception:
                    try:
                        form.start_time.data = datetime.strptime(
                            str(b.startTime), "%H:%M"
                        ).time()
                    except Exception:
                        pass

            if hasattr(b, "meetingSize") and b.meetingSize:
                try:
                    form.meeting_capacity.data = int(b.meetingSize)
                except Exception:
                    pass
        except Exception:
            pass

        room = reader.get_room_data_given_room_number(
            getattr(booking[1], "meetingRoom", None)
        )
        return render_template(
            "booking.html", form=form, mode="edit", booking=booking, room=room
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

        flash("Booking updated successfully.", "success")
        return redirect(f"/booking/{booking_id}")

    # DELETE: remove booking
    if request.method == "DELETE":
        deleted = writer.delete_booking(booking_id)
        if deleted:
            flash("Booking deleted.", "success")
            return redirect("/")
        else:
            flash("Failed to delete booking.", "error")
            return redirect(f"/booking/{booking_id}")


@booking_bp.route("/rsvp", methods=["GET", "POST"])
@booking_bp.route("/rsvp/<link_id>", methods=["GET", "POST"])
def rsvp(link_id=None):
    link = link_id or request.args.get("link")
    booking = Booking()
    # booking = DatabaseReadingServices(DatabaseConnection()).get_booking_by_link_id(link)

    if request.method == "POST":
        name = request.form.get("name")
        # EmailNotificationService(DatabaseConnection()).send_new_rsvp_notification_email(booking.booking_owner_id, name, booking.booking_id)
        flash("RSVP received. Thank you!", "success")
        return redirect("/")

    return render_template("rsvp.html", booking=booking)
