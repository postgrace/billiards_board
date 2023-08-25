from flask_app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from flask import session

bcrypt = Bcrypt()

import re


class User:
    def __init__(self, data):
        self.id = data['user_id']
        self.username = data['username']
        self.email = data['email']
        self.password = data['password']
        
    @staticmethod
    def validate_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email)
    
    @staticmethod
    def validate_user(data):
        errors = []

        if not data['username']:
            errors.append('Username is required.')
            
        if not data['email']:
            errors.append('Email is required.')
        else:
            if not User.validate_email(data['email']): 
                errors.append('Invalid email format')
                
        if not data['password']:
            errors.append('Password is required.')
        else:
            if len(data.get('password', '')) < 8:
                errors.append('Password must be at least 8 characters.')
            
        if not data['password'] == data['confirm_password']:
            errors.append('Passwords do not match')
        

        if 'email' in data:
            email = data['email']
            query = "SELECT id FROM users WHERE email = %(email)s;"
            result = connectToMySQL('billiards_board').query_db(query, {'email': email})
            if result:
                errors.append('Email already exists.')
        
        if 'username' in data:
            username = data['username']
            query = "SELECT id FROM users WHERE username = %(username)s;"
            result = connectToMySQL('billiards_board').query_db(query, {'username': username})
            if result:
                errors.append('Username is taken.')
                

        if len(data.get('username', '')) < 2:
            errors.append('Username must be at least 2 characters.')

        return errors
    
    @staticmethod
    def validate_login(data):
        errors = []

        if not data['email']:
            errors.append('Email is required.')
        else:
            email = data['email']
            query = "SELECT password FROM users WHERE email = %(email)s;"
            result = connectToMySQL('billiards_board').query_db(query, {'email': email})
            if not result:
                errors.append('Email not found.') 
            else:
                hashed_password = result[0]['password']
                entered_password = data['password']
                
                if not bcrypt.check_password_hash(hashed_password, entered_password):
                    errors.append('Invalid password.')

        return errors
        
    @classmethod
    def get_by_id(cls, user_id):
        query = "SELECT * FROM users WHERE user_id = %(user_id)s;"
        results = connectToMySQL('billiards_board').query_db(query, {'user_id': user_id})
        
        if results:
            user = results[0]
            return user
        
        return None    
    
    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL('billiards_board').query_db(query, {'email': email})
        
        if results:
            user_data = results[0]
            user = cls({
                'user_id': user_data['user_id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'password': user_data['password']
            })
            print(user)
            return user
            
        
        return None
        
    @classmethod
    def create_user(cls, data):
        query = "INSERT INTO users (username, email, password) VALUES (%(username)s, %(email)s, %(password)s);"
        return connectToMySQL('billiards_board').query_db(query, data)

        