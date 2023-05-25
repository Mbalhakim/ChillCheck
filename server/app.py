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
    con = Database().get_connection()
    cur = Database().get_cursor(con)
    with open('dataExample.json') as f:
        data = json.load(f)

    minimum = min(data['data'])
    maximum = max(data['data'])
    avg = round(sum(data['data']) / len(data['data']), 2)
    # Database().create('MlxData', (0, minimum, maximum, avg, 0))
    cur.execute('INSERT INTO MlxData(min_temp, max_temp, avg_temp) values (?, ?, ?)', (minimum, maximum, avg))
    cur.execute('COMMIT')
    con.close()
    return render_template('dashboard.html', minimum=minimum, maximum=maximum, avg=avg)


##### Sensor data #####
@app.route('/mlxData', methods=['GET', 'POST'])
def get_mlx_data():
    """Receive and send data of the MLX90640 sensor"""
    if request.method == 'GET':
        mlx_data = MlxData().find(column, value)

        if mlx_data is not None:
            # Show the data when requested by the dashboard
            return jsonify({'success': True, 'data': mlx_data})
        else:
            # Return an error message if no data is available
            return jsonify({'success': False, 'message': 'No data available'})

    if request.method == 'POST':
        # Receive data from the MLX sensor and store it in the global variable
        data = request.data.decode('utf-8')
        mlxdata = [float(x) for x in data.split(',')]
        return jsonify({'success': True, 'message': 'Data received successfully'})

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
