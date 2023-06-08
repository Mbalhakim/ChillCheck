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
def csv_to_json(csv_string):
    rows = csv_string.split("\n")
    rows = [row.strip() for row in rows if row.strip()]
    headers = rows[0].split(",")
    temperature_data = []
    for row in rows[1:]:
        values = row.split(",")
        temperature_row = []
        for value in values:
            if value == "nan":
                temperature_row.append(None)
            else:
                temperature_row.append(float(value))
        temperature_data.append(dict(zip(headers, temperature_row)))
    json_data = json.dumps(temperature_data)
    return json_data

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
    if request.method == 'POST':
        
        content_type = request.headers.get('Content-Type')
        print(content_type)
        csv_string = request.data.decode('utf-8')  # Assuming the CSV string is sent as the request payload
        csv_data = csv_string.strip().split(',')
        json_data = json.dumps(csv_data)
        # print(json_data)
        temperature_values = json_data[0]  # Extract the nested list of temperatures

    # Convert the temperature values to floats
        temperature_values = [float(value) for value in temperature_values]
        
        


    # Calculate minimum, maximum, and average temperatures
        # min_temperature = min(temperature_values)
        # max_temperature = max(temperature_values)
        # avg_temperature = sum(temperature_values) / len(temperature_values)
        # print(min_temperature, max_temperature, avg_temperature)
        
        return temperature_values
    else:
        return 'Invalid request method.'

    

    """Receive and send data of the MLX90640 sensor"""
    
        # Receive data from the MLX sensor, calculate values, and store them in the database
    # data = request.get_json()
    # return data
        
        # if data is None:
        #     return jsonify({'success': False, 'message': 'Data not received'})
        # else:
        #     min_temp = min(data['data'])
        #     max_temp = max(data['data'])
        #     avg_temp = round(sum(data['data']) / len(data['data']), 1)
            
        #     mlx_data = MlxData(0, min_temp, max_temp, avg_temp, "")
        #     mlx_data.create()

        #     return jsonify({'success': True, 'message': 'Data received'})

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
    app.run(host='192.168.137.1', port=5000)