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

    if form.validate_on_submit():
        BookingService.create_booking(
            meetingDate=form.meeting_date.data,
            startTime=form.start_time.data,
            duration=form.duration.data,
            meetingOwner=user_id
        )
        flash("Booking created", "success")
        return redirect('/meeting.html') # TODO: FIX


    date_str = request.args.get('date', '').strip()
     # get room object based on room number
    room = reader.get_room_by_number(room_number)
    #room_capacity = reader.get_room_capacity(room_number)
    if date_str:
        form.meeting_date.data = date_str  # Pre-fill the date field if provided in query parameters

    return render_template("booking.html", form=form, mode="create", room=room)
    


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
