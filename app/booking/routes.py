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

    # Fetch room data early (used for display/capacity)
    room = reader.get_room_data_given_room_number(room_number)
    if not room:
        flash("Invalid room selected.", "error")
        return redirect("/")

    # GET: prefill date safely (string -> date object)
    if request.method == "GET" and date_qs:
        try:
            form.meeting_date.data = datetime.strptime(date_qs, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format in URL. Use YYYY-MM-DD.", "error")

    # POST
    if form.validate_on_submit():
        # WTForms TimeField gives datetime.time, convert to "HH:MM:SS" required by DB logic
        # Your UI doesn't track seconds, so force ":00"
        start_time_str = form.start_time.data.strftime("%H:%M") + ":00"

        # meeting_date is a datetime.date from DateField (good)
        create_booking = writer.create_new_booking(
            meeting_date=form.meeting_date.data,
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
            safe_date = form.meeting_date.data.strftime("%Y-%m-%d") if form.meeting_date.data else ""
            return redirect(f"/booking?room_number={room_number}&date={safe_date}")

        flash("Booking created!", "success")
        return redirect(f"/booking/{create_booking[1]}")

    return render_template("booking.html", form=form, mode="create", room=room)


@booking_bp.route('/booking/<int:booking_id>', methods=['GET'])
def view_booking(booking_id):
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)

    booking = reader.get_booking_information_of_specific_booking(booking_id)
    if not booking[0]:
        abort(404, description="Booking not found")

    return render_template("meeting.html", booking=booking)

#write patch route for booking editing - only allow owner of booking to edit - add delete?
@booking_bp.route('/booking/<int:booking_id>/edit', methods=['GET','PATCH', 'DELETE'])
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

    # Extract updated data from request (this is just an example, you would need to implement the actual update logic)
    updated_data = request.get_json()

    # Call the booking service to update the booking (you would need to implement this method in your BookingService)
    update_result = BookingService.update_booking(booking_id, updated_data)

    if not update_result[0]:
        flash("Failed to update booking.", "error")
        return redirect(f"/booking/{booking_id}")

    flash("Booking updated successfully.", "success")
    return redirect(f"/booking/{booking_id}")


@booking_bp.route('/rsvp', methods=['GET', 'POST'])
@booking_bp.route('/rsvp/<link_id>', methods=['GET', 'POST'])
def rsvp(link_id=None):
    link = link_id or request.args.get('link')
    booking = Booking()
    # booking = DatabaseReadingServices(DatabaseConnection()).get_booking_by_link_id(link)

    if request.method == 'POST':
        name = request.form.get('name')
        # EmailNotificationService(DatabaseConnection()).send_new_rsvp_notification_email(booking.booking_owner_id, name, booking.booking_id)
        flash('RSVP received. Thank you!', 'success')
        return redirect('/')

    return render_template('rsvp.html', booking=booking)
