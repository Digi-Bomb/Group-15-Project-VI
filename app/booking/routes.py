from flask import Blueprint, render_template, request, redirect, flash, current_app
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


@booking_bp.route('/booking', methods=['GET', 'POST'])
def create_booking():
    #renders booking creation form on GET, processes form data and creates new booking on POST
    form = BookingForm()
    if form.validate_on_submit():
        #process form data and create new booking
        newBooking = BookingService.create_booking(
            meeting_date=form.meeting_date.data,
            start_time=form.start_time.data,
            duration=form.duration.data,
            meeting_owner=form.meeting_owner.data,
            meeting_room=form.meeting_room.data,
            meeting_capacity=form.meeting_capacity.data
        )

        if newBooking:
            flash("Booking created successfully!", "success")
            return redirect('/')
        else:
            flash("Failed to create booking.", "danger")
    #if no form, or form validation fails, render the booking creation form again
    return render_template('create_booking.html', form=form)


#pull a booking by ID and allow viewing / editing of it (1 page or 2?)
@booking_bp.route('/booking/<int:booking_id>', methods=['GET', 'POST'])
def manage_booking(booking_id):
    form = BookingForm()
    if form.validate_on_submit():
        # Process form data and update booking


        flash("Booking updated successfully!", "success")
        return redirect('/')

    return render_template('manage_booking.html', booking=booking)


@booking_bp.route('/rsvp', methods=['GET', 'POST'])
@booking_bp.route('/rsvp/<link_id>', methods=['GET', 'POST'])
def rsvp(link_id=None):
    link = link_id or request.args.get('link')
    booking = Booking()
    booking = DatabaseReadingServices(DatabaseConnection()).get_booking_by_link_id(link)

    if request.method == 'POST':
        name = request.form.get('name')
        EmailNotificationService(DatabaseConnection()).send_new_rsvp_notification_email(booking.booking_owner_id, name, booking.booking_id)
        flash('RSVP received. Thank you!', 'success')
        return redirect('/')

    return render_template('rsvp.html', booking=booking)
