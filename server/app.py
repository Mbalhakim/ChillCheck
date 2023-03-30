from flask import *
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = 'ftygfuhijo123498joif1~!'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout') 
def logout():
    """cleart de sessie van de gebruiker, redirect naar index"""
    session.clear()
    return redirect('/')

@app.route('/login', methods=['GET','POST'])
def login():
    """Checkt of een gebruiker een actieve login sessie heeft. Nee? Laat login pagina zien. Ja? Laat index zien"""

    #maak db connectie + cursor (vervang later door db class)
    con = sql.connect('ACS.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    if 'loggedin' in session.keys() and session['loggedin']: #omslachtige dubbele check om een undefined keys foutmelding te voorkomen
        return redirect('/') #als er al een actieve login sessie is -> ga naar index
    else:
        if request.method == 'POST': #als er een inlog request is gedaan
            username = request.form.get('username')
            password = request.form.get('password')

            cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            row = cur.fetchone()

            if row: #als een account matcht aan de logingegevens
                session['loggedin'] = True
                session['username'] = row['username']
                session['id'] = row['id']
                return render_template('index.html', message='Succesvol ingelogt!\n')#index + succes melding na geslaagde inlogpoging
            session['loggedin'] = False
            return render_template('login.html', error = 'Incorrecte inloggegevens. \n')#standaard render + foutmelding na foutieve inlogpoging
        return(render_template('login.html'))#standaard render voor post





app.run(debug=True)