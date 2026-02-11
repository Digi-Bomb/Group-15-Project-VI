
from flask import Blueprint, render_template, request, redirect, flash, current_app
from database_connection import DatabaseConnection
booking_bp = Blueprint('booking', __name__)

#TODO
#booking creation
#ID specific booking edit
#include response codes to all response packages

#refactor to create new booking page
# will room or any other info be passed in the URL or will it all be selected during create?
@booking_bp.route('/booking', methods=['GET', 'POST'])
def create_booking():
    db = DatabaseConnection()
    conn = db.connect()
    cursor = conn.cursor()

    # Placeholder for booking creation logic
    # Process form data to create a new booking
    flash('Booking created successfully!', 'success')
    return redirect('/')

#pull a booking by ID and allow viewing / editing of it (1 page or 2?)
@booking_bp.route('/booking/<int:booking_id>', methods=['GET', 'POST'])
def manage_booking(booking_id):
    db = DatabaseConnection()
    conn = db.connect()
    cursor = conn.cursor()

    # Placeholder for booking management logic
    if request.method == 'POST':
        # Process form data to update the booking
        flash('Booking updated successfully!', 'success')
        return redirect('/booking?id=' + str(booking_id))

    # For GET request, fetch booking details and render the management page
    booking = None
    try:
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM bookings WHERE id = %s', (booking_id,))
        booking = cursor.fetchone()
    except Exception as e:
        current_app.logger.debug(f"booking lookup failed: {e}")
        booking = None
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

    return render_template('manage_booking.html', booking=booking)


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
