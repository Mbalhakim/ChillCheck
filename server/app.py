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
        return redirect(url_for('user.login'))
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
@app.route('/dashboard', methods=['GET'])
def dashboard():
    # fetch mlx data from database
    if request.method == 'GET' and 'loggedin' in session.keys() and session['loggedin']:
        con = Database().get_connection()
        cur = Database().get_cursor(con)
        mlx_query = f"SELECT * FROM MlxData WHERE date(created_at) >= date('2023-06-08')"
        daily_average_query = f"SELECT * FROM DailyAverage WHERE date(date) >= date('2023-06-08')"
        mlx_data_rows = cur.execute(mlx_query).fetchall()
        daily_average_rows = cur.execute(daily_average_query).fetchall()
        cur.close()
        con.close()
        
        # get the most recent mlx data row and daily average row
        mlx_latest_data = mlx_data_rows[len(mlx_data_rows) - 1]
        daily_latest_avg = daily_average_rows[len(daily_average_rows) - 1]

        # get min, max, and avg temp of the most recent 7 mlx data rows
        mlx_week_data = mlx_data_rows[len(mlx_data_rows) - 7:]
        mlx_week_min = [x['min_temp'] for x in mlx_week_data]
        mlx_week_max = [x['max_temp'] for x in mlx_week_data]
        mlx_week_avg = [x['avg_temp'] for x in mlx_week_data]
        
        # create json objects for min, max, and avg temp of mlx data to pass to the dashboard
        min_obj = {"min01": mlx_week_min[0], "min02": mlx_week_min[1], "min03": mlx_week_min[2], "min04": mlx_week_min[3], "min05": mlx_week_min[4], "min06": mlx_week_min[5], "min07": mlx_week_min[6]}
        max_obj = {"max01": mlx_week_max[0], "max02": mlx_week_max[1], "max03": mlx_week_max[2], "max04": mlx_week_max[3], "max05": mlx_week_max[4], "max06": mlx_week_max[5], "max07": mlx_week_max[6]}
        avg_obj = {"avg01": mlx_week_avg[0], "avg02": mlx_week_avg[1], "avg03": mlx_week_avg[2], "avg04": mlx_week_avg[3], "avg05": mlx_week_avg[4], "avg06": mlx_week_avg[5], "avg07": mlx_week_avg[6]}
        
        return render_template('dashboard.html', data={"min_graph": min_obj, "max_graph": max_obj, "avg_graph": avg_obj, "dailyAvg": daily_latest_avg['mlx_avg'], "minTemp": mlx_latest_data['min_temp'], "maxTemp": mlx_latest_data['max_temp'], "avgTemp": mlx_latest_data['avg_temp']})
    else:
        return redirect("/login")

# Render Feedback pagina
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST' and 'loggedin' in session.keys() and session['loggedin']:
        feedback_slider_value = int(request.form.get('feedback-slider'))
        feedback_text = request.form.get('feedback-text')
        
        if feedback_slider_value < -48 and feedback_slider_value > -51:
            fb = Feedback(room=1, feedback_slider=1, feedback_text=feedback_text).create()
        elif feedback_slider_value < -30:
            fb = Feedback(room=1, feedback_slider=2, feedback_text=feedback_text).create()
        elif feedback_slider_value < -15:
            fb = Feedback(room=1, feedback_slider=3, feedback_text=feedback_text).create()
        elif feedback_slider_value < 15:
            fb = Feedback(room=1, feedback_slider=4, feedback_text=feedback_text).create()
        elif feedback_slider_value < 30:
            fb = Feedback(room=1, feedback_slider=5, feedback_text=feedback_text).create()
        elif feedback_slider_value < 48:
            fb = Feedback(room=1, feedback_slider=6, feedback_text=feedback_text).create()
        elif feedback_slider_value < 51:
            fb = Feedback(room=1, feedback_slider=7, feedback_text=feedback_text).create()
        
        if fb:
            flash("Feedback is verzonden")
            return redirect("/dashboard")
        
        return render_template("feedback.html")
    elif request.method == 'GET' and 'loggedin' in session.keys() and session['loggedin']:
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

        con = Database().get_connection()
        cur = Database().get_cursor(con)

        # Insert the temperature statistics into the database
        query = 'INSERT INTO MlxData (min_temp, max_temp, avg_temp) VALUES (?, ?, ?)'
        data = (min_temperature, max_temperature, avg_temperature)
        cur.execute(query, data)
        con.commit()

        cur.close()
        con.close()

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