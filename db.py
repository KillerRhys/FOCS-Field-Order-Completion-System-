import os.path
import sqlite3


# Connects to SQLite3 DB creates data folder if none existent.
def connect_db():
    file_path = "data/"
    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)

    connection = sqlite3.connect(file_path + "FOCS.db")
    return connection


# Create work orders table / fields.
def create_work_orders_table(connection, cursor):
    create_work_orders = '''
    CREATE TABLE IF NOT EXISTS work_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE,
        customer_name TEXT,
        address TEXT,
        date TEXT,
        arrival_time TEXT,
        end_time TEXT,
        meter_number TEXT,
        ert_number TEXT,
        read TEXT,
        notes TEXT
    );
        '''
    #
    cursor.execute(create_work_orders)
    connection.commit()


# function to submit work orders.
def submit_order(connection, cursor, order_number, customer_name, address, date, arrival_time,
                 end_time, meter_number, ert_number, read, notes):
    cursor.execute(
        "INSERT INTO work_orders(order_number, customer_name, address, date, arrival_time, end_time, "
        "meter_number, ert_number, read, notes) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (order_number, customer_name, address, date, arrival_time, end_time, meter_number,
         ert_number, read, notes)
    )

    connection.commit()


# Function that fetches all orders in database.
def fetch_orders(cursor):
    query = "SELECT * FROM work_orders"
    cursor.execute(query)

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
    connection = connect_db()
    cursor = connection.cursor()
    create_work_orders_table(connection, cursor)
    submit_order(connection, cursor, "000123", "Bob Ross", "612 Wharf Ave", "2026.03.25",
                 "08:00", "08:25", "3007416", "00894751", "00517",
                 "Repaired small leak, Performed safety checks!")
    submit_order(connection, cursor, "000124", "Lois Griffin", "31 Spooner ST", "2026.03.25",
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
