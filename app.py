from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

def init_db():
    with sqlite3.connect('datahouse.db') as conn:
        conn.execute(
            'CREATE TABLE IF NOT EXISTS PARTICIPANTS (name TEXT, \
            email TEXT, password TEXT, confirm_password TEXT)'
        )

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        with sqlite3.connect("datahouse.db") as users:
            cursor = users.cursor()
            cursor.execute("INSERT INTO PARTICIPANTS \
            (name,email,password,confirm_password) VALUES (?,?,?,?)",
                           (name, email, password, confirm_password))
            users.commit()
        return render_template("index.html")
    else:
        return render_template('login.html')


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
        # Handle form data here (e.g., save to database)
        # Example:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        # Add your database logic here if needed
        return render_template("index.html")  # Or a success page
    return render_template("join.html")


if __name__ == '__main__':
    app.run(debug=False)