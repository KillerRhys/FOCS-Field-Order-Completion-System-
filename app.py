""" Field Order Completion System
    Coded by TechGYQ
    www.mythosworks.com
    OC:2026.03.28-1300 | Web App: 2026.04.27-2000
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import db


app = Flask(__name__)
app.secret_key = "0adeflakjr0983uakjlkjadf9u"


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
            return redirect(url_for('/orders'))
        else:
            flash("Invalid credentials, please try again.")

    return render_template('login.html')


# Default orders page shows all the techs orders for the day.
@app.route('/orders')
def orders_screen():
    pass  # TODO make this tomorrow first thing so we can finalize login testing.


# Submit order screen.
@app.route('/submit')
def submit_order():
    pass  # TODO make this as well tomorrow hopefully though I expect orders page to take quite awhile.


# User Settings screen.
@app.route('/user')
def settings():
    pass  # TODO Let's user change pin or submit help tickets. NOT NEEDED JUST EXTRA CREDIT!


if __name__ == "__main__":
    app.run(debug=True)
