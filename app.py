from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email

app = Flask(__name__)
app.config["SECRET_KEY"] = "jhdjhadgawWFajhfbyf367212DEy"

class Login(FlaskForm):
    email = StringField(render_kw={"placeholder": "E-mail"}, validators=[Email()])
    password = PasswordField(render_kw={"placeholder": "Wachtwoord"})
    submit = SubmitField("Login")

@app.route('/')
def login():
    form = Login()
    return render_template('login.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)