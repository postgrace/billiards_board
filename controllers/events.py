from flask import render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_app import app
from datetime import datetime

from flask_app.models.user import User
from flask_app.models.event import Event
from flask_app.models.registration import Registration
from flask_app.models.profile import Profile

bcrypt = Bcrypt()

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('register'))

    user_id = session['user_id']
    user = User.get_by_id(user_id)
    profile = Profile.get_by_user_id(user_id)
    
    cities = [str(city) for city in Event.get_all_cities()]
    print(cities)

    filter_by_type = request.args.get('filter_by_type')
    filter_by_city = request.args.get('filter_by_city')

    if filter_by_type and filter_by_city:
        events = Event.get_filtered_events(filter_by_type, filter_by_city)
    elif filter_by_type:
        events = Event.get_events_by_type(filter_by_type)
    elif filter_by_city:
        events = Event.get_events_by_city(filter_by_city)
    else:
        events = Event.get_all_events()

    registered_events = Event.get_registered_events(user_id)
    
    events = sorted(events, key=lambda event: event.datetime if isinstance(event, Event) else event['datetime'])
    registered_events = sorted(registered_events, key=lambda event: event.datetime if isinstance(event, Event) else event['datetime'])
    

    return render_template('dashboard.html', user=user, events=events, cities=cities, registered_events=registered_events, get_by_id=User.get_by_id, profile=profile)


@app.route('/events/new', methods=['GET'])
def add_event():
    return render_template("add_event.html")

@app.route('/new_event', methods=['POST'])
def new_event():
    if 'email' not in session:
        return redirect(url_for('register'))

    errors = []
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    datetime_obj = None
    
    if not date_str or not time_str:
        errors.append('Date and time are required.')
    else:
        datetime_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        if datetime_obj and datetime_obj <= datetime.now():
            errors.append('Event date and time must be later than the current date and time.')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template('add_event.html', errors=errors)
            
    data = {
        'event_id': request.form.get('event_id'),
        'title': request.form.get('title'),
        'game': request.form.get('game'),
        'city': request.form.get('city'),
        'location': request.form.get('location'),
        'datetime': datetime_obj,  
        'format': request.form.get('format'),
        'players_registered': request.form.get('players_registered'),
        'max_players': request.form.get('max_players')
    }

    errors = Event.validate_event(data)
    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template('add_event.html', errors=errors)

    Event.create_event(data)
    return redirect('/dashboard')


@app.route('/events/<int:event_id>')
def show_event(event_id):
    filter_by_type = request.args.get('filter_by_type')
    filter_by_city = request.args.get('filter_by_city')
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    
    events = []
    if filter_by_type and filter_by_city:
        events = Event.get_filtered_events(filter_by_type, filter_by_city)
    elif filter_by_type:
        events = Event.get_events_by_type(filter_by_type)
    elif filter_by_city:
        events = Event.get_events_by_city(filter_by_city)
    else:
        events = Event.get_all_events()
    
    event = Event.get_event(event_id)
    is_registered = Registration.is_already_registered(event_id, user_id)
    print(is_registered)
    
    return render_template("event.html", user=user, event=event, is_registered=is_registered, get_by_id=User.get_by_id, events=events)


@app.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'email' not in session:
        return redirect(url_for('register'))
    event = Event.get_event(event_id)
    print(event.event_id)
    event_date = event.datetime.strftime("%Y-%m-%d")
    event_time = event.datetime.strftime("%H:%M")
    return render_template("edit_event.html", event=event, event_date=event_date, event_time=event_time)


@app.route('/update_event',methods=['POST'])
def update_event():
    if 'email' not in session:
        return redirect(url_for('register'))

    errors = []
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    datetime_obj = None

    if not date_str or not time_str:
        errors.append('Date and time are required.')
    else:
        datetime_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        if datetime_obj <= datetime.now():
            errors.append('Event date and time must be later than the current date and time.')

    if errors:
        for error in errors:
            flash(error, 'error')
        return render_template('edit_event.html', event=request.form, errors=errors)

    data = {
        'event_id': request.form.get('event_id'),
        'title': request.form.get('title'),
        'game': request.form.get('game'),
        'city': request.form.get('city'),
        'location': request.form.get('location'),
        'datetime': datetime_obj,  
        'format': request.form.get('format'),
        'max_players': request.form.get('max_players'),
    }
    
    errors = Event.validate_event(data)
    if errors:
        for error in errors:
            flash(error, 'error')
        Event.update(data)
        return render_template('edit_event.html', event=data, errors=errors)
    
    Event.update(data)
    return redirect('/dashboard')


@app.route('/delete_event/<int:event_id>', methods=['GET', 'POST'])
def delete_event(event_id):
    Event.delete(event_id)
    return redirect('/dashboard')






