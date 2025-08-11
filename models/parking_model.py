import sqlite3

DATABASE = 'models/database.db'

def close_db(conn):
    if conn:
        conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            pincode TEXT CHECK (length(pincode) = 6 AND pincode GLOB '[0-9]*') NOT NULL,
            revenue REAL DEFAULT 0.0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_lot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prime_location_name TEXT NOT NULL,
            price REAL NOT NULL,
            address TEXT NOT NULL,
            pincode TEXT CHECK (length(pincode) = 6 AND pincode GLOB '[0-9]*') NOT NULL,
            maximum_number_of_spots INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_spot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'A',
            spot_number TEXT NOT NULL,
            vehicle_type TEXT,
            is_handicap_accessible BOOLEAN DEFAULT 0,
            FOREIGN KEY (lot_id) REFERENCES parking_lot(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reserve_parking_spot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parking_timestamp DATETIME NOT NULL,
            leaving_timestamp DATETIME,
            parking_cost_per_unit_time REAL NOT NULL,
            total_cost REAL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (spot_id) REFERENCES parking_spot(id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    close_db(conn)

def add_new_parking_lot(prime_location_name, price, address, pincode, maximum_number_of_spots):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO parking_lot (prime_location_name, price, address, pincode, maximum_number_of_spots)
        VALUES (?, ?, ?, ?, ?)
    ''', (prime_location_name, price, address, pincode, maximum_number_of_spots))
    lot_id = cursor.lastrowid
    for i in range(1, maximum_number_of_spots + 1):
        spot_number = f"A{i}"
        cursor.execute('''
            INSERT INTO parking_spot (lot_id, status, spot_number, vehicle_type, is_handicap_accessible)
            VALUES (?, 'A', ?, NULL, 0)
        ''', (lot_id, spot_number))
    conn.commit()
    close_db(conn)

def add_user(name, email, password, address, pincode):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email, password, address, pincode) VALUES (?, ?, ?, ?, ?)',
                   (name, email, password, address, pincode))
    conn.commit()
    close_db(conn)

def book_parking_spot(lot_id, user_id, spot_number, vehicle_type, cost_per_unit_time):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM parking_spot
        WHERE lot_id = ? AND status = 'A'
        LIMIT 1
    ''', (lot_id,))
    spot = cursor.fetchone()
    if not spot:
        close_db(conn)
        raise Exception("No available parking spots in the selected lot.")
    spot_id = spot['id']
    cursor.execute('''
        UPDATE parking_spot
        SET status = 'O', vehicle_type = ?, spot_number = ?
        WHERE id = ?
    ''', (vehicle_type, spot_number, spot_id))
    cursor.execute('''
        INSERT INTO reserve_parking_spot (spot_id, user_id, parking_timestamp, parking_cost_per_unit_time, is_active)
        VALUES (?, ?, datetime('now','localtime'), ?, 1)
    ''', (spot_id, user_id, cost_per_unit_time))
    cursor.execute('''
        UPDATE parking_lot
        SET maximum_number_of_spots = maximum_number_of_spots - 1
        WHERE id = ? AND maximum_number_of_spots > 0
    ''', (lot_id,))
    conn.commit()
    close_db(conn)

def delete_parking_lot(lot_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM parking_lot WHERE id = ?', (lot_id,))
    conn.commit()
    close_db(conn)

def delete_parking_spot(spot_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT lot_id FROM parking_spot WHERE id = ?", (spot_id,))
    result = cursor.fetchone()
    if result:
        lot_id = result['lot_id']
        cursor.execute("UPDATE parking_spot SET status = 'X' WHERE id = ?", (spot_id,))
        cursor.execute('''
            UPDATE parking_lot
            SET maximum_number_of_spots = maximum_number_of_spots - 1
            WHERE id = ? AND maximum_number_of_spots > 0
        ''', (lot_id,))
        conn.commit()
    close_db(conn)

def fetch_active_bookings_by_user(user_id):
    conn = get_db()
    cursor = conn.execute('''
        SELECT r.id, p.prime_location_name AS lot_name, s.spot_number AS spot_no, r.parking_timestamp
        FROM reserve_parking_spot r
        JOIN parking_spot s ON r.spot_id = s.id
        JOIN parking_lot p ON s.lot_id = p.id
        WHERE r.user_id = ? AND r.is_active = 1
    ''', (user_id,))
    bookings = cursor.fetchall()
    close_db(conn)
    return bookings

def fetch_all_parking_lots():
    conn = get_db()
    cursor = conn.execute('''SELECT * FROM parking_lot pl
        JOIN parking_spot ps ON pl.id = ps.lot_id
        WHERE ps.status = 'A'
        GROUP BY pl.id
    ''')
    lots = cursor.fetchall()
    close_db(conn)
    return lots

def fetch_all_users():
    conn = get_db()
    cursor = conn.execute('SELECT * FROM users')
    users = cursor.fetchall()
    close_db(conn)
    return users

def fetch_available_spots():
    conn = get_db()
    cursor = conn.execute('''
        SELECT id, spot_number, lot_id
        FROM parking_spot
        WHERE status = 'A'
    ''')
    spots = cursor.fetchall()
    close_db(conn)
    return spots

def fetch_booking_history_by_user(user_id):
    conn = get_db()
    cursor = conn.execute('''
        SELECT r.*, s.spot_number, s.vehicle_type, p.prime_location_name as lot_name
        FROM reserve_parking_spot r
        LEFT JOIN parking_spot s ON r.spot_id = s.id
        LEFT JOIN parking_lot p ON s.lot_id = p.id
        WHERE r.user_id = ?
        ORDER BY r.parking_timestamp DESC
    ''', (user_id,))
    history = cursor.fetchall()
    close_db(conn)
    return history

def fetch_occupancy_data():
    conn = get_db()
    cursor = conn.execute('''
        SELECT p.prime_location_name AS lot_name,
               COUNT(r.id) AS occupied_count
        FROM parking_lot p
        LEFT JOIN parking_spot s ON p.id = s.lot_id
        LEFT JOIN reserve_parking_spot r ON r.spot_id = s.id AND r.is_active = 1
        GROUP BY p.prime_location_name
    ''')
    occupancy_data = cursor.fetchall()
    close_db(conn)
    return occupancy_data


def fetch_occupied_spots_details():
    conn = get_db()
    cursor = conn.execute('''
        SELECT r.spot_id, u.name as user, p.id as lot_id, p.prime_location_name as lot_name, r.parking_timestamp as time
        FROM reserve_parking_spot r
        JOIN users u ON r.user_id = u.user_id
        JOIN parking_spot s ON r.spot_id = s.id
        JOIN parking_lot p ON s.lot_id = p.id
        WHERE r.is_active = 1
    ''')
    bookings = cursor.fetchall()
    close_db(conn)
    return bookings

def fetch_parking_spots_by_lot(lot_id):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM parking_spot WHERE lot_id = ?', (lot_id,))
    spots = cursor.fetchall()
    close_db(conn)
    return spots

def fetch_parking_usage_summary(user_id):
    conn = get_db()
    cursor = conn.execute('''
        SELECT p.prime_location_name AS lot_name,
               COUNT(r.id) AS booking_count
        FROM reserve_parking_spot r
        JOIN parking_spot s ON r.spot_id = s.id
        JOIN parking_lot p ON s.lot_id = p.id
        WHERE r.user_id = ?
        GROUP BY p.prime_location_name
    ''', (user_id,))
    usage_data = cursor.fetchall()
    close_db(conn)
    return usage_data

def get_parking_lot_by_id(lot_id):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM parking_lot WHERE id = ?', (lot_id,))
    lot = cursor.fetchone()
    close_db(conn)
    return lot

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    close_db(conn)
    return user

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    close_db(conn)
    return user

def release_parking_spot(booking_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.spot_id, s.lot_id, r.user_id
        FROM reserve_parking_spot r
        JOIN parking_spot s ON r.spot_id = s.id
        WHERE r.id = ?
    ''', (booking_id,))
    row = cursor.fetchone()
    if not row:
        close_db(conn)
        raise Exception("Booking not found.")
    spot_id = row['spot_id']
    lot_id = row['lot_id']
    user_id = row['user_id']

    cursor.execute('''
        UPDATE reserve_parking_spot
        SET leaving_timestamp = datetime('now','localtime'), is_active = 0
        WHERE id = ?
    ''', (booking_id,))

    cursor.execute('''
        UPDATE parking_spot
        SET status = 'A'
        WHERE id = ?
    ''', (spot_id,))

    cursor.execute('''
        UPDATE parking_lot
        SET maximum_number_of_spots = maximum_number_of_spots + 1
        WHERE id = ?
    ''', (lot_id,))

    cursor.execute('''
        UPDATE reserve_parking_spot
        SET total_cost = ROUND(((julianday(leaving_timestamp) - julianday(parking_timestamp)) * 24) * parking_cost_per_unit_time, 2)
        WHERE id = ?
    ''', (booking_id,))

    cursor.execute('''
        UPDATE users
        SET revenue = revenue + (
            SELECT total_cost FROM reserve_parking_spot WHERE id = ?
        )
        WHERE user_id = ?
    ''', (booking_id, user_id))
    conn.commit()
    close_db(conn)

def update_parking_lot(id, prime_location_name, price, address, pincode, maximum_number_of_spots):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE parking_lot
        SET prime_location_name = ?, price = ?, address = ?, pincode = ?, maximum_number_of_spots = ?
        WHERE id = ?
    ''', (prime_location_name, price, address, pincode, maximum_number_of_spots, id))
    conn.commit()
    close_db(conn)

def update_user_details(user_id, name, address, pincode):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET name = ?, address = ?, pincode = ?
        WHERE user_id = ?
    ''', (name, address, pincode, user_id))
    conn.commit()
    close_db(conn)

def update_user_password(user_id, new_password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET password = ?
        WHERE user_id = ?
    ''', (new_password, user_id))
    conn.commit()
    close_db(conn)
