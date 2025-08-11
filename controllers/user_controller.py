from flask import Blueprint, render_template, session, redirect, url_for, request, flash, make_response
from functools import wraps
from models.parking_model import (
    fetch_all_parking_lots,
    fetch_booking_history_by_user,
    fetch_parking_usage_summary,
    fetch_active_bookings_by_user,
    release_parking_spot,
    book_parking_spot,
    get_parking_lot_by_id,
    get_user_by_email,
    get_user_by_id,
    update_user_details,
    update_user_password
)
import bcrypt

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_protected(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session or session['user_id'] is None:
            return redirect(url_for('auth.login'))
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return wrapped

@user_bp.route('/dashboard')
@user_protected
def user_dashboard():
    lots = fetch_all_parking_lots()
    user = get_user_by_id(session.get('user_id'))
    history = fetch_booking_history_by_user(session['user_id'])
    return render_template('user_dashboard.html', lots=lots, history=history, name=user['name'])

@user_bp.route('/book_parking', methods=['GET', 'POST'])
@user_protected
def book_parking():
    lots = fetch_all_parking_lots()
    from models.parking_model import fetch_available_spots
    spots = fetch_available_spots()

    if request.method == 'POST':
        lot_id = int(request.form.get('lot_id'))
        spot_id = int(request.form.get('spot_id'))  
        vehicle_type = request.form.get('vehicle_type').strip()
        cost_per_unit_time = float(request.form.get('cost_per_unit_time'))
        book_parking_spot(lot_id, session['user_id'], spot_id, vehicle_type, cost_per_unit_time)
        return redirect(url_for('user.user_dashboard'))

    return render_template('book_parking.html', lots=lots, spots=spots)


@user_bp.route('/release', methods=['GET', 'POST'])
@user_protected
def release_parking():
    user_id = session.get('user_id')

    if request.method == 'POST':
        booking_id = int(request.form.get('booking_id'))
        if booking_id:
            release_parking_spot(booking_id)
        return redirect(url_for('user.user_dashboard'))

    active_bookings = fetch_active_bookings_by_user(user_id)
    return render_template('release_parking.html', active_bookings=active_bookings)

@user_bp.route('/user_summary')
@user_protected
def user_summary():
    labels = []
    data = []
    usage_data = fetch_parking_usage_summary(session['user_id'])
    for row in usage_data:
        labels.append(row['lot_name'])
        data.append(row['booking_count'])
    return render_template('user_summary.html', labels=labels, data=data)

@user_bp.route('/search_parking', methods=['GET'])
@user_protected
def search_parking():
    query = request.args.get('query', '').strip().lower()

    all_lots = fetch_all_parking_lots()
    
    filtered_lots = [
        lot for lot in all_lots
        if query in lot['address'].lower() or query in lot['pincode']
    ] if query else all_lots

    user = get_user_by_id(session['user_id'])
    history = fetch_booking_history_by_user(session['user_id'])

    return render_template(
        'user_dashboard.html',
        lots=filtered_lots,
        history=history,
        name=user['name'],
        search_query=query
    )

@user_bp.route('/edit_profile', methods=['GET'])
@user_protected
def edit_profile():
    user = get_user_by_id(session.get('user_id'))
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.login'))
    return render_template('edit_profile.html', user=user)

@user_bp.route('/update_profile_details', methods=['POST'])
@user_protected
def update_profile_details():
    user_id = session['user_id']
    current_password = request.form.get('current_password_details', '')
    new_name = request.form.get('name', '')
    new_address = request.form.get('address', '')
    new_pincode = request.form.get('pincode', '')

    user = get_user_by_id(session.get('user_id'))
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.login'))

    if bcrypt.checkpw(current_password.encode(), user['password']):
        update_user_details(user_id, new_name, new_address, new_pincode)
        flash('Profile updated!', 'success')
    else:
        flash('Incorrect password.', 'error')
    return redirect(url_for('user.edit_profile'))

@user_bp.route('/change_password', methods=['POST'])
@user_protected
def change_password():
    user_id = session['user_id']
    current_password = request.form.get('current_password_password', '')
    new_password = request.form.get('password', '')

    user = get_user_by_id(session.get('user_id'))
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.login'))

    if bcrypt.checkpw(current_password.encode('utf-8'), user['password']):
        update_user_password(user_id, bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()))
        flash('Password changed successfully!', 'success')
    else:
        flash('Incorrect current password!', 'error')


    return redirect(url_for('user.edit_profile'))
