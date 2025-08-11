import sqlite3

DATABASE = 'models/database.db'

def reset_parking_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("[*] Resetting reserve_parking_spot...")
    cursor.execute("DELETE FROM reserve_parking_spot")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='reserve_parking_spot'")

    print("[*] Resetting parking_spot...")
    cursor.execute("DELETE FROM parking_spot")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='parking_spot'")

    print("[*] Resetting parking_lot...")
    cursor.execute("DELETE FROM parking_lot")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='parking_lot'")

    conn.commit()
    conn.close()
    print("[✓] Reset complete.")

if __name__ == "__main__":
    reset_parking_tables()
