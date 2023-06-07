from dotenv import load_dotenv
import os
from flask import *
import sqlite3 as sql
from db import *
from models import *
import db
import bcrypt


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
    return render_template('dashboard.html')

# Logout
@app.route('/logout') 
def logout():
    """cleart de sessie van de gebruiker, redirect naar index"""
    session.clear()
    return redirect('/')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        company = request.form.get('company')
        birth_date = request.form.get('birth_date')
        role = request.form.get('role')

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        user = User(first_name=first_name, last_name=last_name, username=email, hashed_password=hashed_pw, 
                    company=company, date_of_birth=birth_date, role=role)
        created = user.create()

        if created:
            flash(created)

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')

        user = User(username=username, hashed_password=password)
        find = user.find()
        
        if user.check_password(password.encode('utf8')):
            session['username'] = username
            return 'ingelogd'
    return(render_template('login.html'))


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
