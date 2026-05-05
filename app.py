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
db.create_tables()


# Default login page for technician.
@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        # 1. Grab data first
        user_id = request.form.get('user_id')
        pin = request.form.get('pin')

        if not user_id or not pin:
            flash("Please enter both ID and PIN.", 'auth')
            return render_template('login.html')

        try:
            # 2. Validate User
            # Suggestion: return a dictionary or a specific User object if possible
            is_valid, user_data = db.validate_user({'user_id': user_id, 'pin': pin})

            if is_valid:
                # 3. Secure the session
                session.clear()
                session['user_id'] = user_data['user_id']
                session['name'] = user_data['name']

                # 4. Log the time
                # Using timezone.utc here as we discussed!
                time_str = dt.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                db.last_login({'last_login': time_str, 'user_id': user_data[0]})

                return redirect(url_for('display_orders'))

            flash("Invalid credentials, please try again.", 'auth')

        except db.DatabaseError:
            # Good to catch general DB errors here too
            flash(f"Failed login attempt, please try again!", 'auth')

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

    return render_template('details.html', order=order)


# Add this to app.py
@app.route('/edit/<order_num>')
def edit_order(order_num):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return f"Future Edit Page for Order: {order_num}"


# Submit order screen.
@app.route('/submit', methods=['GET', 'POST'])
def submit_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    order_data = {}

    if request.method == 'POST':
        connection = None  # <--- Setting this to None fixes the warning!
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
                'notes': request.form.get('notes')
            }

            if not all(order_data.values()):
                flash("Please fill out all required fields.", "order_error")
                return render_template('submit_order.html', form_data=order_data)

            if order_data['end_time'] < order_data['arrival_time']:
                flash("End time cannot be earlier than arrival time.", "order_error")
                return render_template('submit_order.html', form_data=order_data)

            connection, cursor = db.connect_db()
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
@app.route('/user')
def settings():
    pass  # TODO Let's user change pin or submit help tickets. NOT NEEDED JUST EXTRA CREDIT!


if __name__ == "__main__":
    app.run(debug=True)
