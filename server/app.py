from dotenv import load_dotenv
import os
from flask import *
import sqlite3 as sql
from db import *
import cv2
import numpy as np
import json
# import requests


# Used to get environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

##### Login page #####
# Render home/login page
@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

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
                return redirect('dashboard')#index + succes melding na geslaagde inlogpoging
            session['loggedin'] = False
            return render_template('login.html', error = 'Incorrecte inloggegevens. \n')#standaard render + foutmelding na foutieve inlogpoging
        return(render_template('login.html'))#standaard render voor post


##### Dashboard page #####
# Render dashboard
@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('dashboard.html')


##### Sensor data #####
mlxdata = None  # create a global variable to store the data
camerMlxdata = None  # create a global variable to store the data

import csv

@app.route('/mlxData', methods=['GET', 'POST'])
def get_mlx_data():
    global mlxdata
    global camerMlxdata

    if request.method == 'GET':
        if mlxdata is not None:
            return  jsonify({'success': False, 'message': 'No data available', 'data':mlxdata})
        else:
            return jsonify({'success': False, 'message': 'No data available'})

    if request.method == 'POST':
        try:
            # Receive data from the MLX sensor and store it in the global variable
            data = request.data.decode('utf-8')
            reader = csv.reader(data.split('\n'), delimiter=',')
            mlxdata = [list(map(float, row)) for row in reader if row]
            camerMlxdata = [list(map(float, row)) for row in reader if row]
            return jsonify({'success': True, 'message': 'Data received successfully','data':mlxdata})
        except:
            return jsonify({'success': False, 'message': 'Data not received'})


@app.route('/camera')
def visualize():
    global camerMlxdata
    if camerMlxdata is None:
        return "No data available"

    # Create a new numpy array to hold the temperature values and scale them to the range [0, 255]
  
    temp_array = np.array(cameraray, dtype=np.float32)
    temp_array -= temp_array.min()
    temp_array /= temp_array.max() / 255.0
    temp_array = temp_array.astype(np.uint8)

    # Create a new canvas
    height, width = temp_array.shape
    canvas = np.zeros((height, width, 3), dtype=np.uint8)

    # Draw the temperature readings as pixels on the canvas
    for y in range(height):
        for x in range(width):
            temperature = temp_array[y, x]
            color = cv2.applyColorMap(np.array([temperature], dtype=np.float32), cv2.COLORMAP_JET)[0, 0]
            canvas[y, x] = color

    # Encode the canvas as a JPEG and return it as a Flask response
    ret, jpeg = cv2.imencode('.jpg', canvas)
    return Response(jpeg.tobytes(), mimetype='image/jpeg')




# Error handler for 404 not found
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="The requested URL was not found on the server."), 404

# Error handler for 500 internal server error
@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message="The server encountered an internal error and was unable to complete your request."), 500

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
    app.run( debug=True)
