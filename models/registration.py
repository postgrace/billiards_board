from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from flask import session

bcrypt = Bcrypt()

class Registration:
    def __init__(self, data):
        self.registration_id = data['registration_id']
        self.user_id = data['user_id']
        self.event_id = data['event_id']
    
    @staticmethod
    def register_player(event_id, user_id):

        query = "SELECT max_players, players_registered FROM events WHERE event_id = %(event_id)s"
        data = {'event_id': event_id}
        result = connectToMySQL('billiards_board').query_db(query, data)
        if not result or result[0]['max_players'] <= result[0]['players_registered']:

            return False

        query = "UPDATE events SET players_registered = players_registered + 1 WHERE event_id = %(event_id)s"
        connectToMySQL('billiards_board').query_db(query, data)

        query = "INSERT INTO registrations (event_id, user_id) VALUES (%(event_id)s, %(user_id)s)"
        data['user_id'] = user_id
        connectToMySQL('billiards_board').query_db(query, data)
        
        return True
    
    @staticmethod
    def is_already_registered(event_id, user_id):
        check_query = "SELECT * FROM registrations WHERE event_id = %(event_id)s AND user_id = %(user_id)s"
        data = {'event_id': event_id, 'user_id': user_id}
        check_result = connectToMySQL('billiards_board').query_db(check_query, data)
        return bool(check_result)



