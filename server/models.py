from db import Database
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email
from datetime import date

class User():
    def __init__(self, first_name, last_name, username, hashed_password, 
                 company, date_of_birth, role):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.hashed_password = hashed_password
        self.company = company
        self.date_of_birth = date_of_birth
        self.role = role
        
    def create(self):
        conn = sqlite3.connect('acs.db')  # Connect to database
        cursor = conn.cursor()
        first_name = self.first_name
        last_name = self.last_name
        user = self.username
        password = self.hashed_password
        company = self.company
        date_of_birth = self.date_of_birth
        role = self.role
        account_type = 0
        created_at = date.today()

        # Check if the user exists
        cursor.execute("SELECT COUNT(*) FROM User WHERE email = ?", (user,))
        count = cursor.fetchone()[0]
        if count > 0:
            return 'Failed to create user, User exists!'
        else:
            cursor.execute("INSERT INTO User (first_name, last_name, email, password, role, company, date_of_birth, account_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                           (first_name, last_name, user, password, role, company, date_of_birth, account_type, created_at))
            conn.commit()
            return 'User created successfully!'
        
    def find(self):
        conn = sqlite3.connect('acs.db')  # Connect to database
        cursor = conn.cursor()
        user = self.username

        # Check if the user exists
        cursor.execute("SELECT COUNT(*), password FROM User WHERE email = ?", (user,))
        count = cursor.fetchone()[0]
        passw = cursor.fetchone()[1]
        
        if count > 0:
            return passw
        else:
            return 'User not found or invalid username and password'
    
    def check_password(self, other_pw):
        return User.bcrypt.checkpw(other_pw, self.hashed_password)

class MlxData():
    def __init__(self, id_ = 0, min_temp = 0, max_temp = 0, avg_temp = 0, created_at = ""):
        self.id_ = id_
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.avg_temp = avg_temp
        self.created_at = created_at
    
    def find(self, column, value):
        return Database().find("MlxData", column, value)

    def create(self):
        query = 'INSERT INTO MlxData (min_temp, max_temp, avg_temp) values (?, ?, ?)'
        data = (self.min_temp, self.max_temp, self.avg_temp)
        Database().create(query, data)
    
    def delete_by_id(self, id_):
        Database().delete_by_id("MlxData", id_)

class ShtData():
    def __init__():
        pass
