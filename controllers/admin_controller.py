from flask import Blueprint, render_template, session, redirect, url_for, request, make_response
from functools import wraps
from models.parking_model import (
    get_db,
    fetch_all_parking_lots,
    add_new_parking_lot,
    get_parking_lot_by_id,
    update_parking_lot,
    delete_parking_lot,
    fetch_parking_spots_by_lot,
    delete_parking_spot,
    fetch_occupied_spots_details,
    fetch_occupancy_data,
    fetch_all_users
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_protected(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session or session.get('user_id') is None:
            return redirect(url_for('auth.login'))
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return wrapped

@admin_bp.route('/dashboard')
@admin_protected
def admin_dashboard():
    return render_template('admin.html')

@admin_bp.route('/add_parking', methods=['GET', 'POST'])
@admin_protected
def add_parking():
    if request.method == 'POST':
        prime_location_name = request.form['prime_location_name']
        price = request.form['price']
        address = request.form['address']
        pincode = request.form['pincode']
        maximum_number_of_spots = request.form['maximum_number_of_spots']
        add_new_parking_lot(prime_location_name, float(price), address, pincode, int(maximum_number_of_spots))
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('add_parking.html')

@admin_bp.route('/edit_parking', methods=['GET', 'POST'])
@admin_protected
def edit_parking():
    if request.method == 'POST':
        lot_id = request.form.get('lot_id')
        prime_location_name = request.form.get('prime_location_name')
        price = request.form.get('price')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        maximum_number_of_spots = request.form.get('maximum_number_of_spots')
        existing_lot = get_parking_lot_by_id(lot_id)
        if existing_lot:
            prime_location_name = prime_location_name or existing_lot['prime_location_name']
            price = price or existing_lot['price']
            address = address or existing_lot['address']
            pincode = pincode or existing_lot['pincode']
            maximum_number_of_spots = maximum_number_of_spots or existing_lot['maximum_number_of_spots']
            update_parking_lot(lot_id, prime_location_name, float(price), address, pincode, int(maximum_number_of_spots))
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return render_template('edit_parking.html', error="Parking Lot ID not found.")
    return render_template('edit_parking.html')

@admin_bp.route('/view_parking_spots')
@admin_protected
def view_parking_spots():
    query = request.args.get('query', '').strip().lower()
    lots = fetch_all_parking_lots()
    spots = []

    for lot in lots:
        lot_spots = fetch_parking_spots_by_lot(lot['id'])
        for spot in lot_spots:
            lot_name = lot['prime_location_name']
            status = spot['status']
            if query:
                if query in lot_name.lower() or query in status.lower():
                    spots.append({
                        'id': spot['id'],
                        'lot_name': lot_name,
                        'status': status,
                    })
            else:
                spots.append({
                    'id': spot['id'],
                    'lot_name': lot_name,
                    'status': status,
                })

    return render_template('view_parking_spots.html', spots=spots)


@admin_bp.route('/delete_spot/<int:spot_id>')
@admin_protected
def delete_spot(spot_id):
    delete_parking_spot(spot_id)
    return redirect(url_for('admin.view_parking_spots'))

@admin_bp.route('/occupied_spot_details')
@admin_protected
def occupied_spot_details():
    bookings = fetch_occupied_spots_details()
    return render_template('occupied_spot_details.html', bookings=bookings)

@admin_bp.route('/admin_summary')
@admin_protected
def admin_summary():
    labels = []
    data = []
    occupancy_data = fetch_occupancy_data()
    for row in occupancy_data:
        labels.append(row['lot_name'])
        data.append(row['occupied_count'])
    return render_template('admin_summary.html', labels=labels, data=data)

@admin_bp.route('/view_users')
@admin_protected
def view_users():
    users = fetch_all_users()
    if not users:
        return render_template('view_users.html', error="No users found.")
    return render_template('view_users.html', users=users)
