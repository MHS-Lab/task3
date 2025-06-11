from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

@app.route('/')
@app.route('/start')
def index():
    return render_template('index.html')

def init_db():
    with sqlite3.connect('datahouse.db') as conn:
        conn.execute(
            'CREATE TABLE IF NOT EXISTS PARTICIPANTS ('
            'name TEXT, '
            'email TEXT UNIQUE, '  # Make email unique
            'password TEXT, '
            'confirm_password TEXT)'
        )
        conn.execute(
            'CREATE TABLE IF NOT EXISTS DESKTOPS ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'option TEXT UNIQUE, '
            'user TEXT, '
            'timestamp REAL)'
        )
        conn.execute(
            'CREATE TABLE IF NOT EXISTS REASONS (id INTEGER PRIMARY KEY AUTOINCREMENT, reason TEXT, timestamp REAL)'
        )

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        with sqlite3.connect("datahouse.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PARTICIPANTS WHERE name=? AND password=?", (name, password))
            user = cursor.fetchone()
        if user:
            session['user'] = name  # Store user in session
            return render_template("logsucc.html")
        else:
            error = "Invalid name or password"
    return render_template('login.html', error=error)


@app.route('/participants')
def participants():
    with sqlite3.connect('datahouse.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM PARTICIPANTS')
        data = cursor.fetchall()
    return render_template("participants.html", data=data)

@app.route('/join', methods=['GET', 'POST'])
def join():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            error = "Passwords do not match."
            return render_template("join.html", error=error)
        with sqlite3.connect("datahouse.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PARTICIPANTS WHERE email=?", (email,))
            if cursor.fetchone():
                error = "Email already registered."
                return render_template("join.html", error=error)
            cursor.execute(
                "INSERT INTO PARTICIPANTS (name, email, password, confirm_password) VALUES (?, ?, ?, ?)",
                (name, email, password, confirm_password)
            )
            conn.commit()
        return render_template("index.html")
    return render_template("join.html", error=error)

@app.route('/home', methods=['GET', 'POST'])
def home():
    error = None
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))  # Force login if not logged in

    now = time.time()
    cutoff = now - 24*3600

    # Check if user has booked in the last 24 hours
    with sqlite3.connect('datahouse.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DESKTOPS WHERE user=? AND timestamp >= ?", (user, cutoff))
        if cursor.fetchone():
            error = "You can only book once per day."
            return render_template('home.html', error=error)

    if request.method == 'POST':
        reason = request.form.get('reason')
        timestamp = time.time()
        with sqlite3.connect('datahouse.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO REASONS (reason, timestamp) VALUES (?, ?)", (reason, timestamp))
            conn.commit()
        return redirect(url_for('comp'))
    return render_template('home.html', error=error)

@app.route('/comp', methods=['GET', 'POST'])
def comp():
    options = [f"Option {i}" for i in range(1, 9)]
    now = time.time()
    cutoff = now - 24*3600
    success = None

    with sqlite3.connect("datahouse.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DESKTOPS WHERE timestamp < ?", (cutoff,))
        conn.commit()
        cursor.execute("SELECT option FROM DESKTOPS WHERE timestamp >= ?", (cutoff,))
        taken = set(row[0] for row in cursor.fetchall())

        if request.method == 'POST':
            selected = request.form.get('desktop')
            user = "user"
            now = time.time()
            if selected:
                try:
                    cursor.execute(
                        "INSERT INTO DESKTOPS (option, user, timestamp) VALUES (?, ?, ?)",
                        (selected, user, now)
                    )
                    conn.commit()
                    # Redirect to thankyo.html after successful reservation
                    return redirect(url_for('thankyo'))
                except sqlite3.IntegrityError:
                    success = False
            else:
                success = False

    return render_template('comp.html', options=options, taken=taken, success=success)

@app.route('/thankyo')
def thankyo():
    return render_template('thankyo.html')

if __name__ == '__main__':
    app.run(debug=False)