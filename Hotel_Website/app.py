from flask import Flask, render_template, request, redirect, url_for, flash, session
import MySQLdb as sql
from flask_mysqldb import MySQL
from wtforms import Form, StringField, SelectField, TextAreaField, PasswordField, validators
from wtforms.fields.html5 import DateField
from passlib.hash import sha256_crypt
from flask_session import Session
from functools import wraps
from datetime import datetime
import os


app = Flask(__name__)


app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
Session(app)

# Config MySQL
app.config['MYSQL_HOST'] = '140.122.184.121'
app.config['MYSQL_USER'] = 'team13'
app.config['MYSQL_PASSWORD'] = 'Q1H1Fe'
app.config['MYSQL_DB'] = 'team13'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        _SQL = """SELECT * 
                  FROM customer
                  WHERE email = %s"""
        result = cur.execute(_SQL, [email])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email
                session['customer_id'] = data['customer_id']

                flash('You are now logged in', 'success')
                return redirect(url_for('member'))
            else:
                error = 'Invalid login'
                flash('Invalid login', 'danger')
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            flash('Username not found', 'danger')
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    phone_num = StringField('Phone Number', [validators.Length(min=6, max=50)])
    payment = StringField('Payment', [validators.Length(min=6, max=50)])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        phone_num = form.phone_num.data
        payment = form.payment.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        _SQL = """INSERT INTO customer
                  (name, email, password, phone_num, payment)
                  VALUES(%s, %s, %s, %s, %s)"""
        cur.execute(_SQL, (name, email, password, phone_num, payment))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('register'))
    return render_template('Register.html', form = form)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/room')
def room():
    return render_template('Room.html')

@app.route('/spa')
def spa():
	return render_template('spa.html')

@app.route('/meal')
def meal():
	return render_template('meal.html')

@app.route('/member')
@is_logged_in
def member():
	return render_template('member_home.html')

# Room Form Class
class RoomForm(Form):
    r_type = SelectField('Room type', choices=[('r001', 'Fairmont Gold Room'), ('r002', 'Samurai Room'), ('r003', 'Otaku Single Room')])
    start_time = DateField('Check-in')
    end_time = DateField('Check-out')

@app.route('/member_room', methods=['GET', 'POST'])
@is_logged_in
def member_room():
    form = RoomForm(request.form)
    if request.method == 'POST' and form.validate():
        customer_id = session['customer_id']
        r_id = form.r_type.data
        start_time = form.start_time.data
        end_time = form.end_time.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        _SQL = """INSERT INTO stay
                  (customer_id, r_id, start_time, end_time)
                  VALUES(%s, %s, %s, %s)"""
        cur.execute(_SQL, (customer_id, r_id, start_time, end_time))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You\'ve booked a room.', 'success')

        return redirect(url_for('member_room'))
    return render_template('member_room.html', form = form)

@app.route('/member_order')
@is_logged_in
def member_order():
    customer_id = session['customer_id']
    
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute query
    _SQL = """SELECT so_id, r_type, start_time, end_time 
              FROM customer NATURAL JOIN stay NATURAL JOIN room
              WHERE customer_id = %s"""
    result = cur.execute(_SQL, [customer_id])
    rooms = cur.fetchall()

    _SQL = """SELECT eo_id, m_type, e_time, section 
              FROM customer NATURAL JOIN eats NATURAL JOIN meal
              WHERE customer_id = %s;"""
    result = cur.execute(_SQL, [customer_id])
    meals = cur.fetchall()

    _SQL = """SELECT uo_id, s_type, u_time, section
              FROM customer NATURAL JOIN uses NATURAL JOIN spa
              WHERE customer_id = %s;"""
    result = cur.execute(_SQL, [customer_id])
    spas = cur.fetchall()

    rt_title = ("Room Type", "Check-in", "Check-out")
    mt_title = ("Meal Type", "Date", "Section")
    st_title = ("Spa Type", "Date", "Section")


    #print(rt_title)
    #print(rt_data)
    #print(mt_title)
    #print(mt_data)
    #print(st_title)
    #print(st_data)

    # Close connection
    cur.close()
    return render_template('member_order.html',
                            rt_title = rt_title,
                            rooms = rooms,
                            mt_title = mt_title,
                            meals = meals,
                            st_title = st_title,
                            spas = spas)

@app.route('/delete_room/<string:so_id>')
@is_logged_in
def delete_room(so_id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute query
    _SQL = """DELETE FROM stay
              WHERE so_id = %s"""
    cur.execute(_SQL, [so_id])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('You\'ve deleted your order.', 'success')

    return redirect(url_for('member_order'))

@app.route('/delete_meal/<string:eo_id>')
@is_logged_in
def delete_meal(eo_id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute query
    _SQL = """DELETE FROM eats
              WHERE eo_id = %s"""
    cur.execute(_SQL, [eo_id])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('You\'ve deleted your order.', 'success')

    return redirect(url_for('member_order'))

@app.route('/delete_spa/<string:so_id>')
@is_logged_in
def delete_spa(so_id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute query
    _SQL = """DELETE FROM uses
              WHERE uo_id = %s"""
    cur.execute(_SQL, [so_id])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('You\'ve deleted your order.', 'success')

    return redirect(url_for('member_order'))

# Spa Form Class
class SpaForm(Form):
    s_type = SelectField('Spa type', choices=[('s001', 'Private Massage $500'), ('s002', 'Luxury Massage $200'), ('s003', 'Korean Style Spa $100')])
    u_time = DateField('Time')
    section = SelectField('Section', choices=[('17:00~19:00'), ('19:00~21:00')])

@app.route('/member_spa', methods=['GET', 'POST'])
@is_logged_in
def member_spa():
    form = SpaForm(request.form)
    if request.method == 'POST' and form.validate():
        customer_id = session['customer_id']
        s_id = form.s_type.data
        u_time = form.u_time.data
        section = form.section.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        _SQL = """INSERT INTO uses
                  (customer_id, s_id, u_time, section)
                  VALUES(%s, %s, %s, %s)"""
        cur.execute(_SQL, (customer_id, s_id, u_time, section))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You\'ve booked a spa.', 'success')

        return redirect(url_for('member_spa'))
    return render_template('member_spa.html', form = form)

# Meal Form Class
class MealForm(Form):
    m_type = SelectField('Meal type', choices=[('m001', 'Western Style $500'), ('m002', 'Chinese Style $400'), ('m003', 'Japanese Style $700')])
    e_time = DateField('Time')
    section = SelectField('Section', choices=[('11:00~13:00'), ('17:00~19:00')])

@app.route('/member_meal', methods=['GET', 'POST'])
@is_logged_in
def member_meal():
    form = MealForm(request.form)
    if request.method == 'POST' and form.validate():
        customer_id = session['customer_id']
        m_id = form.m_type.data
        e_time = form.e_time.data
        section = form.section.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        _SQL = """INSERT INTO eats
                  (customer_id, m_id, e_time, section)
                  VALUES(%s, %s, %s, %s)"""
        cur.execute(_SQL, (customer_id, m_id, e_time, section))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You\'ve booked a meal.', 'success')

        return redirect(url_for('member_meal'))
    return render_template('member_meal.html', form = form)


# Opinion Form Class
class OpinionForm(Form):
    content = TextAreaField('Opinion')

@app.route('/member_opinion', methods=['GET', 'POST'])
@is_logged_in
def member_opinion():
    form = OpinionForm(request.form)
    if request.method == 'POST' and form.validate():
        customer_id = session['customer_id']
        content = form.content.data
        

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        _SQL = """INSERT INTO opinion
                  (customer_id, content)
                  VALUES(%s, %s)"""
        cur.execute(_SQL, (customer_id, content))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You\'ve sent an opinion.', 'success')

        return redirect(url_for('member_opinion'))
    return render_template('member_opinion.html', form = form)

# Account Form Class
class AccountForm(Form):
    email = StringField('Change Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Change Password', [validators.EqualTo('confirm', message='Passwords do not match')])
    phone_num = StringField('Change Phone Number', [validators.Length(min=6, max=50)])
    payment = StringField('Change Payment', [validators.Length(min=6, max=50)])
    confirm = PasswordField('Confirm Password')

@app.route('/member_account', methods=['GET', 'POST'])
@is_logged_in
def member_account():
    form = AccountForm(request.form)
    if request.method == 'POST':
        customer_id = session['customer_id']
        email = form.email.data
        phone_num = form.phone_num.data
        payment = form.payment.data
        password = form.password.data
        

        if email:
            # Create cursor
            cur = mysql.connection.cursor()
            # Execute query
            _SQL = """UPDATE customer
                      SET email = %s
                      WHERE customer_id = %s"""
            cur.execute(_SQL, (email, customer_id))
            # Commit to DB
            mysql.connection.commit()
            # Close connection
            cur.close()

        if phone_num:
            # Create cursor
            cur = mysql.connection.cursor()
            # Execute query
            _SQL = """UPDATE customer
                      SET phone_num = %s
                      WHERE customer_id = %s"""
            cur.execute(_SQL, (phone_num, customer_id))
            # Commit to DB
            mysql.connection.commit()
            # Close connection
            cur.close()

        if payment:
            # Create cursor
            cur = mysql.connection.cursor()
            # Execute query
            _SQL = """UPDATE customer
                      SET payment = %s
                      WHERE customer_id = %s"""
            cur.execute(_SQL, (payment, customer_id))
            # Commit to DB
            mysql.connection.commit()
            # Close connection
            cur.close()

        if password:
            password = sha256_crypt.encrypt(str(password))
            # Create cursor
            cur = mysql.connection.cursor()
            # Execute query
            _SQL = """UPDATE customer
                      SET password = %s
                      WHERE customer_id = %s"""
            cur.execute(_SQL, (password, customer_id))
            # Commit to DB
            mysql.connection.commit()
            # Close connection
            cur.close()


        flash('You\'ve modified your account.', 'success')

        return redirect(url_for('member_account'))
    return render_template('member_account.html', form = form)

@app.route('/delete_account')
@is_logged_in
def delete_account():
    customer_id = session['customer_id']

    # Create cursor
    cur = mysql.connection.cursor()

    # Execute query
    _SQL = """DELETE FROM stay
              WHERE customer_id = %s"""
    cur.execute(_SQL, [customer_id])

    # Execute query
    _SQL = """DELETE FROM eats
              WHERE customer_id = %s"""
    cur.execute(_SQL, [customer_id])

    # Execute query
    _SQL = """DELETE FROM uses
              WHERE customer_id = %s"""
    cur.execute(_SQL, [customer_id])

    # Execute query
    _SQL = """DELETE FROM customer
              WHERE customer_id = %s"""
    cur.execute(_SQL, [customer_id])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash('You\'ve deleted your account.', 'danger')

    return redirect(url_for('login'))



if __name__ == '__main__':
	app.secrect_key = 'secrect123'

	app.run(debug = True)
