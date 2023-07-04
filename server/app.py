from dotenv import load_dotenv
import os
from flask import *
import sqlite3
from db import *
from models import *
from datetime import date

import bcrypt
import hashlib
import requests
import json
import re

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
@app.route('/register', methods=['GET', 'POST'])
def register():
    if session['is_admin'] != 1:
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
        account_type = 2
        created_at = date.today()

        hashed_pw = hash_password(password)
        
        def verify_email(emaill):
            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            match = re.match(pattern, emaill)    
            if match:
                return True
            else:
                return False
        
        if verify_email(email) == False:
            flash("De ingevoerde email is niet geldig!")
            return render_template('register.html')
        
        cursor.execute("SELECT * FROM User WHERE email=?", (email,))
        if cursor.fetchone() is not None:
            flash("De ingevoerde email is al in gebruik!")
            return render_template('register.html')
        else:
            cursor.execute("INSERT INTO User (first_name, last_name, email, password, role, company, date_of_birth, account_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                           (first_name, last_name, email, hashed_pw, role, company, birth_date, account_type, created_at))
            conn.commit()
            flash("Gebruiker is toevoegd!")
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
@app.route('/dashboard', methods=['GET'])
def dashboard():
    # fetch mlx data from database
    if request.method == 'GET' and 'user_id' in session:
        con = Database().get_connection()
        cur = Database().get_cursor(con)

        mlx_query = f"SELECT * FROM MlxData WHERE date(created_at) >= date('2023-06-08')"
        daily_average_query = f"SELECT * FROM DailyAverage WHERE date(date) >= date('2023-06-08')"
        mlx_data_rows = cur.execute(mlx_query).fetchall()
        daily_average_rows = cur.execute(daily_average_query).fetchall()
        
        # get the most recent mlx data row and daily average row
        mlx_latest_data = mlx_data_rows[len(mlx_data_rows) - 1]
        daily_latest_avg = daily_average_rows[len(daily_average_rows) - 1]

        # TODO: use DailyAverage table for mlx graph
        # get min, max, and avg temp of the most recent 7 mlx data rows
        mlx_week_data = mlx_data_rows[len(mlx_data_rows) - 7:]
        mlx_week_min = [x['min_temp'] for x in mlx_week_data]
        mlx_week_max = [x['max_temp'] for x in mlx_week_data]
        mlx_week_avg = [x['avg_temp'] for x in mlx_week_data]
        
        # create json objects for min, max, and avg temp of mlx data to pass to the dashboard
        min_obj = {}
        max_obj = {}
        avg_obj = {}
        if len(mlx_data_rows) > 6:
            min_obj = {
                "min01": mlx_week_min[0],
                "min02": mlx_week_min[1],
                "min03": mlx_week_min[2],
                "min04": mlx_week_min[3],
                "min05": mlx_week_min[4],
                "min06": mlx_week_min[5],
                "min07": mlx_week_min[6]
            }

            max_obj = {
                "max01": mlx_week_max[0],
                "max02": mlx_week_max[1],
                "max03": mlx_week_max[2],
                "max04": mlx_week_max[3],
                "max05": mlx_week_max[4],
                "max06": mlx_week_max[5],
                "max07": mlx_week_max[6]
            }

            avg_obj = {
                "avg01": mlx_week_avg[0],
                "avg02": mlx_week_avg[1],
                "avg03": mlx_week_avg[2],
                "avg04": mlx_week_avg[3],
                "avg05": mlx_week_avg[4],
                "avg06": mlx_week_avg[5],
                "avg07": mlx_week_avg[6]
            }
        
        # Get the latest air quality
        sht_query = f"SELECT * FROM ShtData WHERE date(created_at) >= date('2023-06-08')"
        sht_data_rows = cur.execute(sht_query).fetchall()
        sht_week_data = sht_data_rows[len(sht_data_rows) - 7:]
        sht_week_eco2 = [x['eco2'] for x in sht_week_data]
        sht_week_tvoc = [x['tvoc'] for x in sht_week_data]
        sht_latest_data = sht_data_rows[len(sht_data_rows) - 1]

        # TODO: use DailyAverage table for sht graph
        # Create json objects for eco2, and tvoc of sht data to pass to the dashboard
        eco2_obj = {}
        tvoc_obj = {}
        if len(sht_data_rows) > 6:
            eco2_obj = {
                "eco2_01": sht_week_eco2[0],
                "eco2_02": sht_week_eco2[1],
                "eco2_03": sht_week_eco2[2],
                "eco2_04": sht_week_eco2[3],
                "eco2_05": sht_week_eco2[4],
                "eco2_06": sht_week_eco2[5],
                "eco2_07": sht_week_eco2[6]
            }

            tvoc_obj = {
                "tvoc_01": sht_week_tvoc[0],
                "tvoc_02": sht_week_tvoc[1],
                "tvoc_03": sht_week_tvoc[2],
                "tvoc_04": sht_week_tvoc[3],
                "tvoc_05": sht_week_tvoc[4],
                "tvoc_06": sht_week_tvoc[5],
                "tvoc_07": sht_week_tvoc[6],
            }

        #advies
        avg_temp = mlx_latest_data['avg_temp']
        koud = 16.5
        warm = 19
        if avg_temp <= koud:
            #zet temp hoger
            advies = 0
        elif avg_temp >= warm:
            #zet temp lager (bespaar energie)
            advies = 1
        elif avg_temp > koud and avg_temp < warm:
            #ok
            advies = 2

        # Close database con and cur
        cur.close()
        con.close()

        mlx_graph_data = {"min": min_obj, "max": max_obj, "avg": avg_obj}
        sht_graph_data = {"eco2": eco2_obj, "tvoc": tvoc_obj}
        cards_data = {"minTemp": mlx_latest_data['min_temp'],"maxTemp": mlx_latest_data['max_temp'], "avgTemp": mlx_latest_data['avg_temp'], "airQuality": sht_latest_data["air_quality"], "eco2": sht_latest_data["eco2"], "tvoc": sht_latest_data["tvoc"]}

        return render_template('dashboard.html', advies=advies, data={"mlxGraph": mlx_graph_data, "shtGraph": sht_graph_data, "cards": cards_data})
    else:
        return redirect("/login")

# Render Feedback pagina
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST' and 'user_id' in session:
        feedback_slider_value = int(request.form.get('feedback-slider'))
        feedback_text = request.form.get('feedback-text')
        feedback_room = request.form.get('feedback-room')
        
        
        if feedback_slider_value < -48 and feedback_slider_value > -51:
            Feedback(room=feedback_room, feedback_slider=1, feedback_text=feedback_text).create()
            flash("Feedback is verzonden")
            return redirect("/feedback")
        elif feedback_slider_value < -30:
            Feedback(room=feedback_room, feedback_slider=2, feedback_text=feedback_text).create()
            flash("Feedback is verzonden")
            return redirect("/feedback")
        elif feedback_slider_value < -15:
            Feedback(room=feedback_room, feedback_slider=3, feedback_text=feedback_text).create()
            flash("Feedback is verzonden")
            return redirect("/feedback")
        elif feedback_slider_value < 15:
            Feedback(room=feedback_room, feedback_slider=4, feedback_text=feedback_text).create()
            flash("Feedback is verzonden")
            return redirect("/feedback")
        elif feedback_slider_value < 30:
            Feedback(room=feedback_room, feedback_slider=5, feedback_text=feedback_text).create()
            flash("Feedback is verzonden")
            return redirect("/feedback")
        elif feedback_slider_value < 48:
            Feedback(room=feedback_room, feedback_slider=6, feedback_text=feedback_text).create()
            flash("Feedback is verzonden")
            return redirect("/feedback")
        elif feedback_slider_value < 51:
            Feedback(room=feedback_room, feedback_slider=7, feedback_text=feedback_text).create()
            flash("Feedback is verzonden")
            return redirect("/feedback")
        
        return render_template("feedback.html")
    elif request.method == 'GET' and 'user_id' in session:
        return render_template("feedback.html")
    else:
        return redirect("/login")

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

        # Add new MlxData table row
        mlx_data = MlxData(min_temp=min_temperature, max_temp=max_temperature, avg_temp=avg_temperature).create()
        
        return "Data received successfully"

@app.route('/shtData', methods=['POST'])
def get_sht_data():
    if request.method == 'POST':
        data = request.get_json()  # Retrieve JSON data from the request

        # Process the received data as needed
        air_quality_level = data.get('airQualityLevel')
        eco2 = data.get('eCO2')
        tvoc = data.get('TVOC')
    
        # Add new ShtData table row
        sht_data = ShtData(air_quality=air_quality_level, eco2=eco2, tvoc=tvoc).create()

        # Additional logic to handle the received data
        print("Received data:")
        print("Air Quality Level:", air_quality_level)
        print("eco2:", eco2)
        print("tvoc:", tvoc)

        return "Data received successfully"  # Send a response back if desired


##### Main #####
if __name__ == '__main__':
    app.run(port=5000, debug=True)