from flask import redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_app import app

from flask_app.models.registration import Registration
from flask_app.models.event import Event

bcrypt = Bcrypt()

@app.route('/register/<int:event_id>',methods=['GET','POST'])
def register_event(event_id):
    if 'email' not in session:
        return redirect(url_for('register'))
    
    user_id = session['user_id']
    
    successful_registration = Registration.register_event(event_id, user_id)
    
    if successful_registration:
        flash('Registration succesful!')
    
    return redirect(url_for('dashboard'))

@app.route('/register_player/<int:event_id>/', methods=['POST'])
def register_player(event_id):
    if 'email' not in session:
        return redirect(url_for('register'))
    
    user_id = session.get('user_id', None)
    if user_id is None:
        return redirect(url_for('register'))
    
    successful_registration = Registration.register_player(event_id, user_id)
    
    if successful_registration:
        flash ("Player registered for event successfully")
    
    return redirect(url_for('dashboard'))








