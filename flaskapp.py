from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Absolute path to the directory containing flaskapp.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt'}

# Absolute path to the database file
DATABASE = os.path.join(BASE_DIR, 'users.db')

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the database and create the users table if it doesn't exist
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    email TEXT NOT NULL,
                    filename TEXT,
                    word_count INTEGER
                )''')
    conn.commit()
    conn.close()

init_db()

# Route for the registration page
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

        # Handle file upload
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']
        word_count = 0

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{username}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Count words in the file
            with open(file_path, 'r') as f:
                contents = f.read()
                word_count = len(contents.split())
        else:
            return "Invalid file"

        # Save user data to the database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""INSERT INTO users (username, password, firstname, lastname, email, filename, word_count)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (username, password, firstname, lastname, email, filename, word_count))
        conn.commit()
        conn.close()

        return redirect(url_for('profile', username=username))
    else:
        return render_template('register.html')

# Route for the user profile page
@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    return render_template('profile.html', user=user)

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get login credentials
        username = request.form['username']
        password = request.form['password']

        # Check credentials against the database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid credentials"
    else:
        return render_template('login.html')

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()
