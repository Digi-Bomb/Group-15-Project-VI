from flask import Blueprint, render_template, request, redirect, flash, current_app
from app.database_connection import get_db

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/booking', methods=['GET'])
def booking():
    booking_id = request.args.get('id')
    booking = None
    if booking_id:
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
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
    return render_template('booking.html', booking=booking)


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
