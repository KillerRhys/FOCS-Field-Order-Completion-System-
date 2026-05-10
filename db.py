import os.path
import sqlite3
from dotenv import load_dotenv
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash


IntegrityError = sqlite3.IntegrityError
DatabaseError = sqlite3.Error
load_dotenv()
PEPPER = os.getenv("PEPPER")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "FOCS.db")


# Connects to SQLite3 DB with specified settings using context managers..
@contextmanager
def connect_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.close()


# Create user tables.
def create_user_table():
    with connect_db() as conn:
        cursor = conn.cursor()
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
        conn.commit()


# First run to build tables and install test user.
def initial_setup():
    create_tables()
    create_default_user()


# Helper to log techs last login.
def last_login(time_data):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE user_id = ?",
            (time_data['last_login'], time_data['user_id'])
        )

        conn.commit()


# Create work orders table / fields.
def create_work_orders_table():
    with connect_db() as conn:
        cursor = conn.cursor()
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
            has_updated BOOLEAN DEFAULT 0,
            update_timestamp DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            CHECK (end_time >= arrival_time)
        );
            '''

        cursor.execute(create_work_orders)
        conn.commit()


# Create all tables
def create_tables():
    create_user_table()
    create_work_orders_table()


# Creates new user for system.
def create_user(user_info):
    with connect_db() as conn:
        cursor = conn.cursor()
        peppered_pin = user_info['pin'] + PEPPER
        hashed_pin = generate_password_hash(peppered_pin)
        cursor.execute(
            "INSERT INTO users(name, user_id, pin) VALUES(?, ?, ?)",
            (user_info['name'], user_info['user_id'], hashed_pin)
        )

        conn.commit()


def create_default_user():
    with connect_db as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fectchne()[0]

    if count == 0:
        user_info = {
            "name": "Joe Bob",
            "user_id": "0813",
            "pin": "7777"
        }

        create_user(user_info)
    else:
        pass


# Validates user against database.
def validate_user(login_data):
    with connect_db() as conn:
        cursor = conn.cursor()
        query = "SELECT user_id, name, pin FROM users WHERE user_id = ?"
        cursor.execute(query, (login_data["user_id"],))
        result = cursor.fetchone()

        if result:
            if check_password_hash(result['pin'], login_data['pin'] + PEPPER):
                return True, result

        return False, None


# function to submit work orders.
def submit_order(order_data):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO work_orders(
                user_id, order_number, customer_name, address, date, 
                arrival_time, end_time, meter_number, ert_number, read, notes, has_updated, update_timestamp
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                order_data['user_id'], order_data['order_number'], order_data['customer_name'],
                order_data['address'], order_data['date'], order_data['arrival_time'],
                order_data['end_time'], order_data['meter_number'], order_data['ert_number'],
                order_data['read'], order_data['notes'], order_data['has_updated'], order_data['update_timestamp']
            )
        )
        conn.commit()


# Function to update work order.
def update_record(table, record_id, data):
    blacklist = ['id', 'order_number', 'created_at']

    # 2. Filter the incoming data
    updates = {k: v for k, v in data.items() if k not in blacklist and v is not None}

    if not updates:
        return False

    columns = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values())
    values.append(record_id)  # Add ID for the WHERE clause

    query = f"UPDATE {table} SET {columns} WHERE id = ?"

    with connect_db() as conn:
        conn.execute(query, values)
        conn.commit()

    return True


# Helper to find order's by tech or with params.
def fetch_orders(user_id, search=None):
    with connect_db() as conn:
        cursor = conn.cursor()
        if search:
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
            term = f"%{search}%"
            cursor.execute(query, (user_id, term, term, term, term, term))

        else:
            query = """
                SELECT * FROM work_orders 
                WHERE user_id = ? 
                ORDER BY date DESC, arrival_time DESC
            """
            cursor.execute(query, (user_id,))

        return cursor.fetchall()


def get_order_by_number(order_number, user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM work_orders WHERE order_number = ? AND user_id = ?"
        cursor.execute(query, (order_number, user_id))
        return cursor.fetchone()


# Multi-faceted function to search any and all fields with specified input.
def data_search(filters):
    with connect_db() as conn:
        cursor = conn.cursor()
        """
        filters: A dictionary like {"date": "2026.03.25", "customer_name": "Lois Griffin"}
        """
        query = "SELECT * FROM work_orders"
        params = []

        if filters:
            conditions = [f"{field} = ?" for field in filters.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(filters.values())

        cursor.execute(query, params)
        return cursor.fetchall()
