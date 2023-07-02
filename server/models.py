from db import Database

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email

class RegistrationForm(FlaskForm):
    firstname = StringField('Voornaam', validators=[DataRequired()], render_kw={"placeholder": "Voornaam"})
    lastname = StringField('Achternaam', validators=[DataRequired()], render_kw={"placeholder": "Achternaam"})
    username = StringField('Gebruikersnaam', validators=[DataRequired()], render_kw={"placeholder": "Gebruikersnaam"})
    email = StringField("E-mail:", validators=[Email()], render_kw={"placeholder": "E-mail"})
    password = PasswordField('Wachtwoord', validators=[DataRequired(), EqualTo('pass_confirm', message='Wachtwoorden dienen overeen te komen')], render_kw={"placeholder": "Wachtwoord"})
    pass_confirm = PasswordField('Bevestig wachtwoord', validators=[DataRequired()], render_kw={"placeholder": "Bevestig wachtwoord"})
    submit = SubmitField('Registreer')

class User():
    def __init__():
        pass

class DailyAverage():
    def __init__(self, id_ = 0, mlx_avg = 0, sht_avg = 0, date = 0, day = 0):
        self.id_ = id_
        self.mlx_avg = mlx_avg
        self.sht_avg = sht_avg
        self.date = date
        self.day = day
    
    def find(self, column, value):
        return Database().find('DailyAverage', column, value)
    
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
    def __init__(self, id_ = 0, air_quality = "", eco2 = 0.0, tvoc = 0.0, created_at = ""):
        self.id_ = id_
        self.air_quality = air_quality
        self.eco2 = eco2
        self.tvoc = tvoc
        self.created_at = created_at
    
    def find(self, column, value):
        return Database().find("Feedback", column, value)

    def create(self):
        query = 'INSERT INTO ShtData (air_quality, eco2, tvoc) values (?, ?, ?)'
        data = (self.air_quality, self.eco2, self.tvoc)
        Database().create(query, data)
        return self

class Feedback():
    def __init__(self, id_ = 0, room = 0, feedback_slider = 0, feedback_text = "", created_at = ""):
        self.id_ = id_
        self.room = room
        self.feedback_slider = feedback_slider
        self.feedback_text = feedback_text
        self.created_at = created_at

    def find(self, column, value):
        return Database().find("Feedback", column, value)

    def create(self):
        query = 'INSERT INTO Feedback (room, feedback_slider, feedback_text) values (?, ?, ?)'
        data = (self.room, self.feedback_slider, self.feedback_text)
        Database().create(query, data)
        return self
