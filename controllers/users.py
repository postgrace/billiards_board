from flask import render_template, request, redirect, url_for, flash, get_flashed_messages, session
from flask_bcrypt import Bcrypt
from flask_app import app

from flask_app.models.user import User

bcrypt = Bcrypt()

@app.route('/')
def index():
    registration_errors = get_flashed_messages(category_filter='registration-error')
    login_errors = get_flashed_messages(category_filter='login-error')
    return render_template('login_and_registration.html', registration_errors=registration_errors, login_errors=login_errors)

@app.route('/register',methods=['GET','POST'])
def register_user():
    data = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'password': request.form.get('password'),
        'confirm_password': request.form.get('confirm_password')
    }
    
    errors = User.validate_user(data)
    if errors:
        for error in errors:
            flash(error, 'registration-error')
        return redirect('/')
    

    hashed_password = bcrypt.generate_password_hash(data['password'].encode('utf-8'))


    data['password'] = hashed_password.decode('utf-8')
    User.create_user(data)
    
    user = User.get_by_email(data['email'])
    if user:
        session['username'] = user.username
        session['email'] = user.email
        session['user_id'] = user.id
        return redirect(url_for('create_profile'))
    
    return "Registration successful!"
    
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = {
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        
        errors = User.validate_login(data)
        if errors:
            for error in errors:
                flash(error, 'login-error')
            return redirect(url_for('index'))
        
        user = User.get_by_email(data['email'])
        if user:
            session['username'] = user.username
            session['email'] = user.email
            session['user_id'] = user.id
            print(session.get('email'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'login-error')
    
    return redirect(url_for('index'))



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')





