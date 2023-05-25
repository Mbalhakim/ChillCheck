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
        Database().create("MlxData", (self.min_temp, self.max_temp, self.avg_temp))
    
    def delete_by_id(self, id_):
        Database().delete_by_id("MlxData", id_)

class ShtData():
    def __init__():
        pass
