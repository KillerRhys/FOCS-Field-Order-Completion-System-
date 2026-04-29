import os.path
import sqlite3


# Connects to SQLite3 DB creates data folder if none existent.
def connect_db():
    file_path = "data/"
    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)

    connection = sqlite3.connect(file_path + "FOCS.db")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    return connection, cursor


# Closes Database.
def close_connections(connection):
    connection.close()


# Create user tables.
def create_user_table(connection, cursor):
    create_users = """
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    user_id TEXT UNIQUE,
    pin TEXT,
    last_login TEXT
    );
        """

    cursor.execute(create_users)
    connection.commit()


# Create work orders table / fields.
def create_work_orders_table(connection, cursor):
    create_work_orders = '''
    CREATE TABLE IF NOT EXISTS work_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id NOT NULL,
        order_number TEXT UNIQUE,
        customer_name TEXT,
        address TEXT,
        date TEXT,
        arrival_time TEXT,
        end_time TEXT,
        meter_number TEXT,
        ert_number TEXT,
        read TEXT,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
        '''

    cursor.execute(create_work_orders)
    connection.commit()


# Create all tables
def create_tables(connection, cursor):
    create_user_table(connection, cursor)
    create_work_orders_table(connection, cursor)


# Creates new user for system.
def create_user(connection, cursor, user_info):
    cursor.execute(
        "INSERT INTO users(name, user_id, pin) VALUES(?, ?, ?)",
        (user_info['name'], user_info['user_id'], user_info['pin'])
    )

    connection.commit()


# Validates user against database.
def validate_user(cursor, login_data):
    query = "SELECT user_id, name, pin FROM users WHERE user_id = ? AND pin = ?"

    cursor.execute(query, (login_data["user_id"], login_data['pin']))

    result = cursor.fetchone()
    if result:
        return True, result

    else:
        return False, result


# function to submit work orders.
def submit_order(connection, cursor, order_data):
    cursor.execute(
        "INSERT INTO work_orders(user_id, order_number, customer_name, address, date, arrival_time, end_time, "
        "meter_number, ert_number, read, notes) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (order_data['user_id'], order_data['order_number'], order_data['customer_name'], order_data['address'],
         order_data['date'], order_data['arrival_time'], order_data['end_time'], order_data['meter_number'],
         order_data['ert_number'], order_data['read'], order_data['notes'])
    )

    connection.commit()


# Function that fetches all orders in database.
def fetch_orders(cursor, user_id):
    query = "SELECT * FROM work_orders WHERE user_id = ?"
    cursor.execute(query, (user_id,))

    rows = cursor.fetchall()
    return rows


# Multi-faceted function to search any and all fields with specified input.
def data_search(cursor, filters):
    """
    filters: A dictionary like {"date": "2026.03.25", "customer_name": "Lois Griffin"}
    """
    # 1. Start with the base query
    query = "SELECT * FROM work_orders"
    params = []

    # 2. If there are filters, build the WHERE clause dynamically
    if filters:
        # Create "column_name = ?" strings
        conditions = [f"{field} = ?" for field in filters.keys()]
        # Join them with " AND "
        query += " WHERE " + " AND ".join(conditions)
        # Collect the actual values in the same order
        params = list(filters.values())

    cursor.execute(query, params)
    return cursor.fetchall()


# Test function performs all checks on system.
def test_db():
    connection, cursor = connect_db()
    create_tables(connection, cursor)
    user_info = {"name": "Joe Bob", "user_id": "0813", "pin": "7777"}
    create_user(connection, cursor, user_info)
    submit_order(connection, cursor, "0813","000123", "Bob Ross", "612 Wharf Ave", "2026.03.25",
                 "08:00", "08:25", "3007416", "00894751", "00517",
                 "Repaired small leak, Performed safety checks!")
    submit_order(connection, cursor, "0813", "000124", "Lois Griffin", "31 Spooner ST", "2026.03.25",
                 "08:40", "09:00", "3005216", "90704781", "9184",
                 "Restored service per customer request, All checks ok!")
    rows = fetch_orders(cursor)
    if not rows:
        print("No results!")
    else:
        print(f"--- {len(rows)} Work Orders Completed! ---")
        for row in rows:
            print(row)
    criteria = {
        "date": "2026.03.25",
        "customer_name": "Lois Griffin"
    }
    search_result = data_search(cursor, criteria)
    if not search_result:
        print("No results were found!")
    else:
        print(f"--- {len(search_result)} Work Orders Completed! ---")
        for result in search_result:
            print(result)
    connection.close()


if __name__ == "__main__":
    test_db()
