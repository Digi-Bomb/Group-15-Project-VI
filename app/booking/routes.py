from flask import Blueprint, render_template, request, redirect, flash, current_app, session, abort

from booking.booking import Booking
from notifications.email_notification_service import EmailNotificationService
from .booking_service import BookingService
from forms import BookingForm
from database_connection import DatabaseConnection
from database_reading import DatabaseReadingServices
from database_writing import DatabaseWritingServices

booking_bp = Blueprint('booking', __name__)

#TODO
#booking creation
#ID specific booking edit
#include response codes to all response packages
#start writing functions for booking service to handle booking creation / editing

#needs to take room number and date ?room={{ room.roomNumber }}&date={{ selected_date }}
@booking_bp.route('/booking', methods=['GET', 'POST'])
def create_booking():
    db = DatabaseConnection()
    reader = DatabaseReadingServices(db)
    writer = DatabaseWritingServices(db, reader)

    user_id = session.get("user_id")
    room_number = request.args.get('room_number', '').strip()

    if not user_id:
      flash("Please log in to create a booking.", "warning")
      return redirect("/login")

    form = BookingForm()

    # Fetch room data early (used for choices + capacity)
    room = reader.get_room_data_given_room_number(room_number)

    if not room:
        flash("Invalid room selected.", "error")
        return redirect("/")


    #POST
    if form.validate_on_submit():
        service = BookingService()
        #call duration function from reader here - will return a duration
        meeting_id = service.create_booking(
            meetingDate=form.meeting_date.data,
            startTime=form.start_time.data,
            duration="02:00",
            meetingOwner=user_id,
            meetingRoom=room_number,
            meetingCapacity=form.meeting_capacity.data
        )
        if not meeting_id[0]:
            if meeting_id[1] == "Room is NOT Available":
                flash("The selected time slot is already booked. Please choose a different time.", "error")
            flash("Failed to create booking.", "error")
            return redirect("/booking")
        flash("Booking created!", "success")
        return redirect(f'/booking/{meeting_id[1]}') # TODO: test this redirect


    #refactor to use datepicker js to auto submit date and prefill date field on booking form
    date_str = request.args.get('date', '').strip() or form.meeting_date.data

    if date_str:
        form.meeting_date.data = date_str  # Pre-fill the date field if provided in query parameters

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
