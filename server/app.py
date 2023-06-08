from dotenv import load_dotenv
import os
from flask import *
import sqlite3 as sql
from db import *
from models import *
import db
from datetime import date

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
    return render_template('login.html')

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
    query = f"SELECT * FROM MlxData WHERE created_at > {date.today()}"
    rows = cur.execute(query).fetchall()
    cur.close()
    con.close()

    mlx_data = rows[len(rows) - 1]
    # mlx_data = MlxData().find("id", 100)
    daily_avg = DailyAverage().find("id", 1)

    return render_template('dashboard.html', data={"dailyAvg": dailyAvg['mlx_avg'], "minTemp": mlx_data['min_temp'], "maxTemp": mlx_data['max_temp'], "avgTemp": mlx_data['avg_temp']})


##### Sensor data #####
@app.route('/mlxData', methods=['POST'])
def get_mlx_data():
    """Receive and send data of the MLX90640 sensor"""
    if request.method == "POST":
        content_type = request.headers.get('Content-Type')
        csv_string = request.data.decode('utf-8')  # Assuming the CSV string is sent as the request payload
        csv_data = csv_string.strip().split(',')
        csv_data = [value for value in csv_data if value != 'nan']

        # Convert the temperature values to integers
        temperature_values = [float(value) for value in csv_data]

        # Calculate minimum, maximum, and average temperatures
        min_temperature = min(temperature_values)
        max_temperature = max(temperature_values)
        avg_temperature = sum(temperature_values) / len(temperature_values)
        avg_temperature = round(avg_temperature, 2)

        mlx_data_obj = MlxData(min_temperature, max_temperature, avg_temperature)
        mlx_data_obj.create()

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
    app.run(port=5000, debug=True)