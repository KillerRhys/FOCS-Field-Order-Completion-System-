""" Field Order Completion System
    Coded by TechGYQ
    www.mythosworks.com
    OC:2026.03.28-1300 | Web App: 2026.04.27-2000
"""
import datetime
import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import db
from datetime import datetime as dt


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
setup_connection, setup_cursor = db.connect_db()
db.create_tables(setup_connection, setup_cursor)
db.close_connections(setup_connection)


# Default login page for technician.
@app.route('/', methods=['GET', 'POST'])
def login():
    connection, cursor = db.connect_db()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        pin = request.form.get('pin')
        login_data = {'user_id': user_id, 'pin': pin}

        result = db.validate_user(cursor, login_data)

        if result[0]:
            time_data = {
                'last_login': dt.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': result[1][0]
            }
            db.last_login(connection, cursor, time_data)
            db.close_connections(connection)
            session['user_id'] = result[1][0]
            session['name'] = result[1][1]
            return redirect(url_for('display_orders'))
        else:
            db.close_connections(connection)
            flash("Invalid credentials, please try again.", 'auth')

    db.close_connections(connection)
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


# Default orders page shows all the techs orders for the day.
@app.route('/orders')
def display_orders():
    user_id = session.get('user_id')
    # This looks for ?search=... in the URL
    search_query = request.args.get('search', '').strip()

    connection, cursor = db.connect_db()

    if search_query:
        orders = db.fetch_orders(cursor, user_id, search=search_query)
    else:
        orders = db.fetch_orders(cursor, user_id)

    db.close_connections(connection)
    return render_template('orders.html', orders=orders, search_query=search_query)


# Submit order screen.
@app.route('/submit', methods=['GET', 'POST'])
def submit_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        if request.method == 'POST':
            order_data = {
                'user_id': session['user_id'],
                'order_number': request.form.get('order_number'),
                'customer_name': request.form.get('customer_name'),
                'address': request.form.get('address'),
                'date': dt.now().strftime("%Y.%m.%d"),
                'arrival_time': request.form.get('arrival_time'),
                'end_time': request.form.get('end_time'),
                'meter_number': request.form.get('meter_number'),
                'ert_number': request.form.get('ert_number'),
                'read': request.form.get('read'),
                'notes': request.form.get('notes')
            }

            # Check if all values in the dictionary are present (not empty)
            if not all(order_data.values()):
                flash("Please fill out all required fields.", "order_error")
                return render_template('submit_order.html', form_data=order_data)

            connection, cursor = db.connect_db()
            db.submit_order(connection, cursor, order_data)
            db.close_connections(connection)

            return redirect(url_for('display_orders'))

        else:
            return render_template('submit_order.html')

    except sqlite3.IntegrityError as e:

        flash(f'Database error: {e}', 'order_error')

        # Pass order_data back so the form fields stay filled

        return render_template('submit_order.html', form_data=order_data)


@app.route('/cancel')
def cancel_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return redirect(url_for('display_orders'))


# User Settings screen.
@app.route('/user')
def settings():
    pass  # TODO Let's user change pin or submit help tickets. NOT NEEDED JUST EXTRA CREDIT!


if __name__ == "__main__":
    app.run(debug=True)
