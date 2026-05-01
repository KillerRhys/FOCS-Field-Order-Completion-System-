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


def last_login(connection, cursor, time_data):
    cursor.execute(
        "UPDATE users SET last_login = ? WHERE user_id = ?",
        (time_data['last_login'], time_data['user_id'])
    )

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


def fetch_orders(cursor, user_id, search=None):
    if search:
        # 1. The Search Query
        # We use OR so it checks every field for the match
        query = """
            SELECT * FROM work_orders 
            WHERE user_id = ? 
            AND (
                date LIKE ? OR 
                customer_name LIKE ? OR 
                address LIKE ? OR 
                meter_number LIKE ? OR 
                ert_number LIKE ?
            )
            ORDER BY date DESC, arrival_time DESC
        """
        # We wrap the search term in % so it finds partial matches (e.g. "Main" finds "123 Main St")
        term = f"%{search}%"
        cursor.execute(query, (user_id, term, term, term, term, term))

    else:
        # 2. The Standard Query
        # Runs when the tech first opens the page or clears the search
        query = """
            SELECT * FROM work_orders 
            WHERE user_id = ? 
            ORDER BY date DESC, arrival_time DESC
        """
        cursor.execute(query, (user_id,))

    return cursor.fetchall()


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
