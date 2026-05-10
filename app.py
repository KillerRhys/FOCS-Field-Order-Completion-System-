""" Field Order Completion System
    Coded by TechGYQ
    www.mythosworks.com
    OC:2026.03.28-1300 | Web App: 2026.04.27-2000
"""
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import db
from datetime import datetime as dt, timezone


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Initial setup if fresh run.
db_path = "data/FOCS.db"

if not os.path.exists(db_path):
    db.initial_setup()
else:
    db.create_tables()


# Default login page for technician / user with validation.
@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        pin = request.form.get('pin')

        if not user_id or not pin:
            flash("Please enter both ID and PIN.", 'auth')
            return render_template('login.html')

        try:
            is_valid, user_data = db.validate_user({'user_id': user_id, 'pin': pin})

            if is_valid:
                session.clear()
                session['user_id'] = user_data['user_id']
                session['name'] = user_data['name']

                time_str = dt.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                db.last_login({'last_login': time_str, 'user_id': user_data['user_id']})

                return redirect(url_for('display_orders'))

            flash("Invalid credentials, please try again.", 'auth')

        except db.DatabaseError:
            flash(f"Failed login attempt, please try again!", 'auth')

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


# Default orders page shows all the current tech's orders for the day.
@app.route('/orders')
def display_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search_query = request.args.get('search', '').strip()

    if search_query:
        orders = db.fetch_orders(session['user_id'], search=search_query)
    else:
        orders = db.fetch_orders(session['user_id'])

    return render_template('orders.html', orders=orders, search_query=search_query)


# Order details page.
@app.route('/details/<order_number>')
def order_details(order_number):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    order = db.get_order_by_number(order_number, session['user_id'])

    if not order:
        flash("Order not found or access denied.", "order_error")
        return redirect(url_for('display_orders'))

    return render_template('details.html', order=order)


# Edit order route. TODO flesh out.
@app.route('/edit/<order_num>', methods=['GET', 'POST'])
def edit_order(order_num):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    update_data = None
    current_order = db.get_order_by_number(order_num, session['user_id'])
    if not current_order:
        flash("Unable to locate order.", "order_error")
        return redirect(url_for('display_orders'))

    if request.method == 'POST':
        try:
            update_data = {
                'customer_name': request.form.get('customer_name'),
                'address': request.form.get('address'),
                'arrival_time': request.form.get('arrival_time'),
                'end_time': request.form.get('end_time'),
                'meter_number': request.form.get('meter_number'),
                'ert_number': request.form.get('ert_number'),
                'read': request.form.get('read'),
                'notes': request.form.get('notes'),
                'has_updated': 1,
                'update_timestamp': dt.now().strftime("%Y.%m.%d %H:%M:%S"),
            }

            required_fields = ['customer_name', 'address', 'arrival_time', 'end_time',
                               'meter_number', 'ert_number', 'read', 'notes']

            if not all(update_data[k] for k in required_fields):
                flash("Please fill out all required fields.", "order_error")
                return render_template('edits.html', form_data=update_data)

            if update_data['end_time'] < update_data['arrival_time']:
                flash("End time cannot be earlier than arrival time.", "order_error")
                return render_template('edits.html', form_data=update_data)

            db.update_record('work_orders', current_order['id'], update_data)

            flash("Order successfully updated!", "order_success")
            return redirect(url_for('display_orders'))

        except db.IntegrityError as e:
            flash(f'Database error (likely duplicate order number)', 'order_error')
            return render_template('edits.html', form_data=update_data)

    return render_template('edits.html', form_data=current_order)


# Submit order screen.
@app.route('/submit', methods=['GET', 'POST'])
def submit_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    order_data = {}

    if request.method == 'POST':
        try:
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
                'notes': request.form.get('notes'),
                'has_updated': 0,
                'update_timestamp': None
            }

            required_fields = ['order_number', 'customer_name', 'address', 'arrival_time', 'end_time',
                               'meter_number', 'ert_number', 'read', 'notes']

            if not all(order_data[k] for k in required_fields):
                flash("Please fill out all required fields.", "order_error")
                return render_template('submit_order.html', form_data=order_data)

            if order_data['end_time'] < order_data['arrival_time']:
                flash("End time cannot be earlier than arrival time.", "order_error")
                return render_template('submit_order.html', form_data=order_data)

            db.submit_order(order_data)

            flash("Order added successfully!", "order_success")
            return redirect(url_for('display_orders'))

        except db.IntegrityError as e:
            flash(f'Database error (likely duplicate order number): {e}', 'order_error')
            return render_template('submit_order.html', form_data=order_data)

    return render_template('submit_order.html')


# Cancels new order form and returns to display orders.
@app.route('/cancel')
def cancel_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return redirect(url_for('display_orders'))


# User Settings screen.
@app.route('/user', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_pin = request.form.get('current_pin')
        new_pin = request.form.get('new_pin')
        verify_pin = request.form.get('verify_pin')

        # Validation Step 1: Matching
        if new_pin != verify_pin:
            flash("New PINs do not match!", "error")
            return render_template('settings.html')

        # Validation Step 2: Complexity (Optional but recommended)
        if len(new_pin) < 4:
            flash("PIN must be at least 4 digits.", "error")
            return render_template('settings.html')

        # Attempt the update
        success, message = db.update_user_pin(session['user_id'], current_pin, new_pin)

        if success:
            flash(message, "order_success")  # Using your existing CSS class
            return redirect(url_for('display_orders'))
        else:
            flash(message, "order_error")

    return render_template('settings.html')


if __name__ == "__main__":
    app.run(debug=True)
