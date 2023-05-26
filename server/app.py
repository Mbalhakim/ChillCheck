from dotenv import load_dotenv
import os
from flask import *
import sqlite3 as sql
from db import *
from models import *
import db

import json

# Used to get environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

##### Login page #####
# Render home/login page
@app.route('/')
def index():
    return render_template('dashboard.html')

# Logout
@app.route('/logout') 
def logout():
    """cleart de sessie van de gebruiker, redirect naar index"""
    session.clear()
    return redirect('/')

# Register
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Add to db
        user = User(firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    email=form.email.data,
                    username=form.username.data, 
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Bedankt voor de registratie. Er kan nu ingelogd worden!')
        return redirect(url_for('userr.login'))
    return render_template('register.html', form=form)

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
            username = request.form.get('email')
            password = request.form.get('password')

            cur.execute('SELECT * FROM User WHERE email = ? AND password = ?', (username, password))
            #kan hier geen db class gebruiken: meerdere parameters
            row = cur.fetchone()

            if row: #als een account matcht aan de logingegevens
                session['loggedin'] = True
                session['email'] = row['email']
                session['id'] = row['id']
                return redirect('dashboard')#index + succes melding na geslaagde inlogpoging
            session['loggedin'] = False
            return render_template('login.html', error = 'Incorrecte inloggegevens. \n')#standaard render + foutmelding na foutieve inlogpoging
        return(render_template('login.html'))#standaard render voor post


##### Dashboard page #####
# Render dashboard
@app.route('/dashboard')
def dashboard():
    mlx_data = MlxData().find("id", 5)

    return render_template('dashboard.html', data={"minTemp": mlx_data['min_temp'], "maxTemp": mlx_data['max_temp'], "avgTemp": mlx_data['avg_temp']})


##### Sensor data #####
@app.route('/mlxData', methods=['GET', 'POST'])
def get_mlx_data():
    """Receive and send data of the MLX90640 sensor"""
    if request.method == 'POST':
        # Receive data from the MLX sensor, calculate values, and store them in the database
        data = request.get_json()
        
        if data is None:
            return jsonify({'success': False, 'message': 'Data not received'})
        else:
            min_temp = min(data['data'])
            max_temp = max(data['data'])
            avg_temp = round(sum(data['data']) / len(data['data']), 1)
            
            mlx_data = MlxData(0, min_temp, max_temp, avg_temp, "")
            mlx_data.create()

            return jsonify({'success': True, 'message': 'Data received'})

@app.route('/shtData', methods=['GET', 'POST'])
def get_sht_data():
    """Receive and send data of the SHT21 sensor"""
    if request.method == 'GET':
        # Send SHT data when requested by the dashboard
        pass
    if request.method == 'POST':
        # Receive data from the SHT sensor and store it in the database
        pass


##### Main #####
if __name__ == '__main__':
    app.run(debug=True)
