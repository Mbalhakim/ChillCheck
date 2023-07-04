from dotenv import load_dotenv
import os
from flask import *
import sqlite3 as sql
from db import *
from models import *
import db
import bcrypt
import hashlib

import requests
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
    
    return render_template('login.html')

# Logout
@app.route('/logout') 
def logout():
    """cleart de sessie van de gebruiker, redirect naar index"""
    session.clear()
    return redirect('/')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('dashboard')
    
    conn = sqlite3.connect("acs.db")
    cursor = conn.cursor()
    
    def hash_password(password):
        # Hash the password using SHA-256
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        company = request.form.get('company')
        birth_date = request.form.get('birth_date')
        role = request.form.get('role')
        account_type = 0
        created_at = date.today()

        hashed_pw = hash_password(password)
        
        cursor.execute("SELECT * FROM User WHERE email=?", (email,))
        if cursor.fetchone() is not None:
            flash("De ingevoerde email is al in gebruik!")
            return render_template('register.html')
        else:
            cursor.execute("INSERT INTO User (first_name, last_name, email, password, role, company, date_of_birth, account_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                           (first_name, last_name, email, hashed_pw, role, company, birth_date, account_type, created_at))
            conn.commit()
            flash("Bedankt voor de registratie. Er kan nu ingelogd worden!")
            return render_template('register.html')

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect('dashboard')
    conn = sqlite3.connect("acs.db")
    cursor = conn.cursor()
    
    def hash_password(password):
        # Hash the password using SHA-256
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = hash_password(password)

        # Retrieve the user from the database
        cursor.execute("SELECT * FROM User WHERE email=? AND password=?", (email, hashed_password))
        user = cursor.fetchone()
        if user is not None:
            session['user_id'] = user[0]
            session['is_admin'] = user[8]
            return redirect('dashboard')
        else:
            flash("Ongeldige gebruikersnaam of wachtwoord.")
            return render_template('login.html')
    return render_template('login.html')


##### Dashboard page #####
# Render dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
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
