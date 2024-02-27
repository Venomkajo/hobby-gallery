from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import os
import uuid
from cs50 import SQL
import magic
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import check_image
app = Flask(__name__)

db = SQL("sqlite:///gallery.db")
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS images (image_id INTEGER PRIMARY KEY, user_id INTEGER, image TEXT, title TEXT, description TEXT, gender TEXT, FOREIGN KEY (user_id) REFERENCES users(id))")

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gallery')
def get_gallery():
    picture_files = os.listdir('static/pictures')
    return render_template('gallery.html', picture_files=picture_files)

@app.route('/upload', methods=["GET", "POST"])
def upload():

    if session.get("user_id") is None:
        text = "please login"
        return redirect("/login")

    if request.method == ("POST"):
        if 'image' not in request.files:
            return 'form error'
        
        image = request.files['image']

        if image.filename == "":
            return 'no image submitted'
        
        if check_image(image) == False:
            return 'not an image'
        
        name = request.form['name']
        description = request.form['description']
        gender = request.form['gender']

        unique_filename = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        image.save(file_path)

        if not (name and description and gender):
            return 'please fill out all fields'
        
        db.execute('INSERT INTO images (user_id, image, title, description, gender) VALUES (?, ?, ?, ?, ?)', session["user_id"], unique_filename, name, description, gender)

        return redirect('/')

    return render_template('upload.html')

@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":

        session.clear()

        username = request.form['username']
        password = request.form['password']

        if not username:
            return 'Please enter a username'
        elif not password:
            return 'Please enter a password'
        
        hashed_password = generate_password_hash(password)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        
        if not rows or not check_password_hash(rows[0]["password"], password):
                return "invalid username and/or password"
        
        session["user_id"] = rows[0]["id"]
        return redirect('/')

    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method =="POST":

        session.clear()

        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if not username:
            return 'Please enter a username'
        elif not password:
            return 'Please enter a password'
        elif not confirm:
            return 'Please confirm the password'
        elif len(password) < 8:
            return 'Password must be at least 8 characters long'
        elif password != confirm:
            return 'Passwords do not match'
        elif db.execute("SELECT username FROM users WHERE username = ?", username):
            return 'Username is taken'

        hashed_password = generate_password_hash(password)
        
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, hashed_password)

        return redirect("/login")

    return render_template('register.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)