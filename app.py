from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import time

app = Flask(__name__)

@app.route('/')
@app.route('/start')
def index():
    return render_template('index.html')

def init_db():
    with sqlite3.connect('datahouse.db') as conn:
        conn.execute(
            'CREATE TABLE IF NOT EXISTS PARTICIPANTS (name TEXT, email TEXT, password TEXT, confirm_password TEXT)'
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
            return render_template("logsucc.html")  # Redirect to logsucc.html on success
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
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        with sqlite3.connect("datahouse.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO PARTICIPANTS (name, email, password, confirm_password) VALUES (?, ?, ?, ?)",
                           (name, email, password, confirm_password))
            conn.commit()
        return render_template("index.html")
    return render_template("join.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        reason = request.form.get('reason')
        timestamp = time.time()
        with sqlite3.connect('datahouse.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO REASONS (reason, timestamp) VALUES (?, ?)", (reason, timestamp))
            conn.commit()
        return redirect(url_for('comp'))
    return render_template('home.html')

@app.route('/comp', methods=['GET', 'POST'])
def comp():
    options = [f"Option {i}" for i in range(1, 9)]
    now = time.time()
    cutoff = now - 24*3600  # 24 hours ago

    # Remove expired bookings (optional, for cleanup)
    with sqlite3.connect("datahouse.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DESKTOPS WHERE timestamp < ?", (cutoff,))
        conn.commit()

    # Get currently taken options (not expired)
    with sqlite3.connect("datahouse.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT option FROM DESKTOPS WHERE timestamp >= ?", (cutoff,))
        taken = set(row[0] for row in cursor.fetchall())

    success = None
    if request.method == 'POST':
        selected = request.form.get('desktop')
        user = "user"  # Replace with actual user info if available
        if selected and selected not in taken:
            with sqlite3.connect("datahouse.db") as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO DESKTOPS (option, user, timestamp) VALUES (?, ?, ?)",
                        (selected, user, now)
                    )
                    conn.commit()
                    success = True
                    taken.add(selected)
                except sqlite3.IntegrityError:
                    success = False
        else:
            success = False

    return render_template('comp.html', options=options, taken=taken, success=success)

if __name__ == '__main__':
    app.run(debug=False)