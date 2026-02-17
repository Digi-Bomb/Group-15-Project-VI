from flask import Blueprint, render_template, request, redirect, flash, current_app, session, abort
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
    user_id = session.get("user_id")
    # TEMP COMMENT
    # if not user_id:
    #   flash("Please log in to create a booking.", "warning")
    #   return redirect("/login")

    form = BookingForm()
    # TODO: needs to generate meetingcapacity based on roomcapacity, colin issue

    if request.method == 'GET':
        date_str = request.args.get('date', '').strip()
        if date_str:
            form.meeting_date.data = date_str  # Pre-fill the date field if provided in query parameters
            return render_template("booking.html", form=form, mode="create")

    if form.validate_on_submit():
        BookingService.create_booking(
            meetingDate=form.meeting_date.data,
            startTime=form.start_time.data,
            duration=form.duration.data,
            meetingOwner=user_id
        )
        flash("Booking created", "success")
        return redirect('/meeting.html') # TODO: FIX

    return render_template("booking.html", form=form, mode="create")
    


@booking_bp.route('/rsvp', methods=['GET', 'POST'])
@booking_bp.route('/rsvp/<link_id>', methods=['GET', 'POST'])
def rsvp(link_id=None):
    link = link_id or request.args.get('link')
    booking = None
    if link:
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT booking_id FROM shareable_links WHERE link_id = %s', (link,))
            row = cursor.fetchone()
            if row:
                cursor.execute('SELECT * FROM bookings WHERE id = %s', (row['booking_id'],))
                booking = cursor.fetchone()
        except Exception as e:
            current_app.logger.debug(f"rsvp lookup failed: {e}")
            booking = {'booking_name': '(unresolved)'}
        finally:
            try:
                cursor.close()
                conn.close()
            except Exception:
                pass

    if request.method == 'POST':
        name = request.form.get('name')
        flash('RSVP received. Thank you!', 'success')
        return redirect('/')

    return render_template('rsvp.html', booking=booking)
