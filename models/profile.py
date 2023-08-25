from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from flask import session

bcrypt = Bcrypt()


class Profile:
    def __init__(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.nickname = data['nickname']
        self.city = data['city']
        self.home_bar = data['home_bar']
        self.team_name = data['team_name']
        self.profile_pic = data.get('profile_pic')
    
    @staticmethod
    def validate_profile(data):
        errors = []

        if not data['first_name']:
            errors.append('First name is required.')
        
        if not data['last_name']:
            errors.append('Last name is required.')
        
        if not data['city']:
            errors.append('City is required.')
            
        if not data['home_bar']:
            errors.append('Home bar is required.')
        
        if not data['team_name']:
            errors.append('Team Name is required.')
        
        return errors
        
    @classmethod
    def get_profile(cls, profile_id):
        query = "SELECT * FROM profiles WHERE profile_id = %(profile_id)s;"
        result = connectToMySQL('billiards_board').query_db(query,{'profile_id': profile_id})
        print(result)
    
        if result:
            profile = cls(result[0])
            profile.profile_id = profile_id
            return profile
    
        return None
    
    @classmethod
    def get_by_user_id(cls, user_id):
        query = "SELECT * FROM profiles WHERE user_id = %(user_id)s;"
        results = connectToMySQL('billiards_board').query_db(query, {'user_id': user_id})
        
        if results:
            profile = results[0]
            return profile
        
        return None 
        
    @classmethod
    def create_profile(cls, data):
        user_id = session.get('user_id')
        data['user_id'] = user_id
        if 'profile_pic' in data:
            query = """INSERT INTO profiles (first_name, last_name, nickname, city, home_bar, team_name, user_id, profile_pic) 
            VALUES (%(first_name)s, %(last_name)s, %(nickname)s, %(city)s, %(home_bar)s, %(team_name)s, %(user_id)s, %(profile_pic)s);"""
        else:
            query = """INSERT INTO profiles (first_name, last_name, nickname, city, home_bar, team_name, user_id) 
            VALUES (%(first_name)s, %(last_name)s, %(nickname)s, %(city)s, %(home_bar)s, %(team_name)s, %(user_id)s);"""
        profile_id = connectToMySQL('billiards_board').query_db(query, data)

        print("profile ID:", profile_id)
        if profile_id:
            profile = cls(data)
            profile.profile_id = profile_id
            print("profile object:", profile)
            return profile

        return None
    
    @classmethod
    def upload_profile_pic(cls, data):
        query = "UPDATE profiles SET profile_pic = %(profile_pic)s WHERE profile_id = %(profile_id)s;"
        connectToMySQL('billiards_board').query_db(query, data)
    
    @classmethod
    def update(cls, data):
        query = """
                UPDATE profiles 
                SET first_name=%(first_name)s, last_name=%(last_name)s, nickname=%(nickname)s, city=%(city)s, home_bar=%(home_bar)s, team_name=%(team_name)s
                WHERE profile_id = %(profile_id)s;
                """
        profile_id = connectToMySQL('billiards_board').query_db(query, data)
        
        if profile_id:
            profile = cls(data)
            profile.profile_id = profile_id
            return profile

        return None
    
    @classmethod
    def delete(cls,profile_id):
        data = {"profile_id": profile_id}
        query  = "DELETE FROM profiles WHERE profile_id = %(profile_id)s;"
        profile_id = connectToMySQL('billiards_board').query_db(query,data)

        