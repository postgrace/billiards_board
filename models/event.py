from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from flask import session, request
from datetime import datetime

bcrypt = Bcrypt()


class Event:
    def __init__(self, data):
        self.event_id = data['event_id']
        self.title = data['title']
        self.game = data['game']
        self.city = data['city']
        self.location = data['location']
        self.datetime = data['datetime']
        self.format = data['format']
        self.max_players = data['max_players']
        self.players_registered = data['players_registered']
        self.user_id = data['user_id']
    
    @staticmethod
    def validate_event(data):
        errors = []
        
        if not data['title']:
            errors.append('Title is required.')
        else: 
            if len(data.get('title', '')) < 3:
                errors.append('Title must be at least 2 characters.')
        
        if not data['city']:
            errors.append('City is required.')
            
        if not data['location']:
            errors.append('Location is required.')
            
        if not data['datetime']:
            errors.append('Date and time must be provided')
        
        if not data['format']:
            errors.append('Format is required.')
        
        if not data['max_players']:
            errors.append('Maximum number of players is required.')
            
        elif int(data['max_players']) > 20:
            errors.append('Max players cannot exceed 20.')
        
        print(errors)
        return errors
    
    @staticmethod
    def get_filtered_events(filter_by_type, filter_by_city):
        query = "SELECT * FROM events WHERE game = %(type)s AND city = %(city)s"
        data = {'type': filter_by_type, 'city': filter_by_city}
        filtered_events = connectToMySQL('billiards_board').query_db(query, data)
        return filtered_events
    
    @staticmethod
    def get_events_by_type(filter_by_type):
        query = "SELECT * FROM events WHERE game = %(type)s"
        data = {'type': filter_by_type}
        events = connectToMySQL('billiards_board').query_db(query, data)
        return events
    
    @staticmethod
    def get_all_cities():
        query = "SELECT city FROM events"
        result = connectToMySQL('billiards_board').query_db(query)
        cities = [row['city'] for row in result]
        print(cities)
        return cities
    
    @staticmethod
    def get_events_by_city(filter_by_city):
        query = "SELECT * FROM events WHERE city = %(city)s"
        data = {'city': filter_by_city}
        events = connectToMySQL('billiards_board').query_db(query, data)
        return events
        
    @classmethod
    def get_event(cls, event_id):
        query = "SELECT * FROM events WHERE event_id = %(event_id)s;"
        result = connectToMySQL('billiards_board').query_db(query,{'event_id': event_id})
        print(result)
    
        if result:
            event = result  
            return cls(event[0])
    
        return None  
    
    @classmethod
    def get_all_events(cls):
        query = "SELECT * FROM events;"
        results = connectToMySQL('billiards_board').query_db(query)
        events = []
        for r in results:
            events.append( cls(r) )
        return events
    
    @classmethod
    def get_registered_events(cls, user_id):
        query = "SELECT events.* FROM events JOIN registrations ON events.event_id=registrations.event_id WHERE registrations.user_id=%(user_id)s;"
        data = {'user_id' : user_id}
        results = connectToMySQL('billiards_board').query_db(query, data)
        events = []
        for r in results:
            events.append(cls(r))
        return events
        
    @classmethod
    def create_event(cls, data):
        user_id = session.get('user_id')
        data['user_id'] = user_id
        query = "INSERT INTO events (title, game, city, location, datetime, format, max_players, user_id) VALUES (%(title)s, %(game)s, %(city)s, %(location)s, %(datetime)s, %(format)s, %(max_players)s, %(user_id)s);"
        event_id = connectToMySQL('billiards_board').query_db(query, data)
        print("event ID:", event_id)
        if event_id:
            event = cls(data)
            event.id = event_id
            print("event object:", event)
            return event

        return None 
    
    @classmethod
    def update(cls, data):
        query = """UPDATE events 
                SET title=%(title)s,game=%(game)s,city=%(city)s,location=%(location)s, datetime=%(datetime)s, format=%(format)s, max_players=%(max_players)s
                WHERE event_id = %(event_id)s;"""
        event_id = connectToMySQL('billiards_board').query_db(query, data)
        print("event ID:", event_id)
        if event_id:
            event = cls(data)
            event.id = event_id
            print("event object:", event)
            return event

        return None
    
    @classmethod
    def delete(cls, event_id):
        data = {"event_id": event_id}
        registration_query = "DELETE FROM registrations WHERE event_id = %(event_id)s;"
        events_query = "DELETE FROM events WHERE event_id = %(event_id)s;"
        connectToMySQL('billiards_board').query_db(registration_query, data)
        connectToMySQL('billiards_board').query_db(events_query, data)


        