""" Field Order Completion System
    Coded by TechGYQ
    www.mythosworks.com
    OC:2026.03.28-1300 | Web App: 2026.04.27-2000
"""
import os

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

        if result[0]:  # TODO Order's page needs fixed for this to be tested.
            db.close_connections(connection)
            session['user_id'] = result[1][0]
            session['name'] = result[1][1]
            return redirect(url_for('display_orders'))
        else:
            db.close_connections(connection)
            flash("Invalid credentials, please try again.")

    db.close_connections(connection)
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


# Default orders page shows all the techs orders for the day.
@app.route('/orders')
def display_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection, cursor = db.connect_db()
    orders_data = db.fetch_orders(cursor, session['user_id'])
    print(orders_data)
    db.close_connections(connection)
    return render_template('orders.html', orders=orders_data)


# Submit order screen.
@app.route('/submit', methods=['GET', 'POST'])
def submit_order():
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

        connection, cursor = db.connect_db()
        db.submit_order(connection, cursor, order_data)
        db.close_connections(connection)

        return redirect(url_for('display_orders'))

    return render_template('submit_order.html')


@app.route('/cancel')
def cancel_order():
    return redirect(url_for('display_orders'))


# User Settings screen.
@app.route('/user')
def settings():
    pass  # TODO Let's user change pin or submit help tickets. NOT NEEDED JUST EXTRA CREDIT!


if __name__ == "__main__":
    app.run(debug=True)
