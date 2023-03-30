from dotenv import load_dotenv
import os
from flask import *
import sqlite3 as sql
from db import *
import requests

# Used to get environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

##### Login page #####
# Render home/login page
@app.route('/')
def index():
    return render_template('index.html')

# Logout
@app.route('/logout') 
def logout():
    """cleart de sessie van de gebruiker, redirect naar index"""
    session.clear()
    return redirect('/')

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    """Checkt of een gebruiker een actieve login sessie heeft. Nee? Laat login pagina zien. Ja? Laat index zien"""
    #maak db connectie
    con = Database().get_connection()
    cur = Database().get_cursor(con)
    if 'loggedin' in session.keys() and session['loggedin']: #omslachtige dubbele check om een undefined keys foutmelding te voorkomen
        return redirect('/') #als er al een actieve login sessie is -> ga naar index
    else:
        if request.method == 'POST': #als er een inlog request is gedaan
            username = request.form.get('username')
            password = request.form.get('password')

            cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            #kan hier geen db class gebruiken: meerdere parameters
            row = cur.fetchone()

            if row: #als een account matcht aan de logingegevens
                session['loggedin'] = True
                session['username'] = row['username']
                session['id'] = row['rowid']
                return render_template('dashboard.html', message='Succesvol ingelogt!\n')#index + succes melding na geslaagde inlogpoging
            session['loggedin'] = False
            return render_template('login.html', error = 'Incorrecte inloggegevens. \n')#standaard render + foutmelding na foutieve inlogpoging
        return(render_template('login.html'))#standaard render voor post


##### Dashboard page #####
# Render dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/mlxData', methods=['GET'])
def get_mlx_data():
    """Gets the data of the MLX90640 camera sensor"""
    pass

@app.route('/shtData', methods=['GET'])
def get_sht_data():
    """Gets the data of the SHT21 sensor"""
    pass


##### Main #####
if __name__ == '__main__':
    app.run(debug=True)