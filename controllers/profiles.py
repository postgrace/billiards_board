from flask import render_template, request, redirect, url_for, flash, session
import os
from flask_bcrypt import Bcrypt
from flask_app import app

from flask_app.models.user import User
from flask_app.models.profile import Profile

bcrypt = Bcrypt()

@app.route('/profiles/create', methods=['GET'])
def create_profile():
    profile_pic = session.get('profile_pic')
    return render_template("create_profile.html", profile_pic=profile_pic, profile_error=session.get('profile_error'))

@app.route('/new_profile', methods=['POST'])
def new_profile():
    if 'email' not in session:
        return redirect(url_for('register'))

    data = {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'nickname': request.form.get('nickname'),
        'city': request.form.get('city'),
        'home_bar': request.form.get('home_bar'),
        'team_name': request.form.get('team_name')
    }


    if 'temp-profile-pic' in session:

        data['profile_pic'] = session['temp-profile-pic']
    
    print(data)

    errors = Profile.validate_profile(data)
    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template('create_profile.html', errors=errors)

    profile = Profile.create_profile(data)
    if profile:
        session['profile_id'] = profile.profile_id
        

        session.pop('temp-profile-pic', None)

        return redirect(url_for('show_profile', profile_id=session['profile_id']))

    return redirect(url_for('create_profile'))

@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        flash('No file part', 'profile_error')
        return redirect(request.url)

    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file', 'profile_error')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        profile_id = None
        if 'profile_id' in session:
            profile_id = session['profile_id']
        

        if request.referrer.endswith(url_for('create_profile')):

            session['temp-profile-pic'] = filename
            return redirect(url_for('create_profile'))

        elif 'profile_id' in session:

            profile_id = session['profile_id']
            data = {'profile_pic': filename, 'profile_id': profile_id}
            Profile.upload_profile_pic(data)

        return redirect(url_for('edit_profile', profile_id=profile_id))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/profiles/<int:profile_id>', methods=['GET'])
def show_profile(profile_id):
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    profile = Profile.get_profile(profile_id)
    return render_template("profile.html", user=user, profile=profile, get_by_id=User.get_by_id, profile_id=profile_id)

@app.route('/profiles/edit/<int:profile_id>', methods=['GET', 'POST'])
def edit_profile(profile_id):
    if 'email' not in session:
        return redirect(url_for('register'))
    session['profile_id'] = profile_id
    profile = Profile.get_profile(profile_id)
    
    print(profile.profile_pic)
    
    return render_template("edit_profile.html", profile=profile, profile_id=profile.profile_id)

@app.route('/update_profile',methods=['POST'])
def update_profile():
    if 'email' not in session:
        return redirect(url_for('register'))
    data = {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'nickname': request.form.get('nickname'),
        'city': request.form.get('city'),
        'home_bar': request.form.get('home_bar'),
        'team_name': request.form.get('team_name'),
        'profile_id': request.form.get('profile_id')
    }
    
    profile_id = data['profile_id']
    errors = Profile.validate_profile(data)
    
    if errors:
        for error in errors:
            flash(error, 'error')

        current_profile = Profile.get_profile(profile_id)
        data.update(profile_pic=current_profile.profile_pic)
        return render_template('edit_profile.html', profile=data, errors=errors)


    current_profile = Profile.get_profile(profile_id)
    data.update(profile_pic=current_profile.profile_pic)
    
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename == '' or not allowed_file(file.filename):
            flash('Invalid file', 'profile_error')

        else:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            data['profile_pic'] = filename  

    Profile.update(data)
    session['profile_id'] = profile_id
    return redirect(url_for('show_profile', profile_id=profile_id))







