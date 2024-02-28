from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
import os
import uuid
from cs50 import SQL
import magic
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import check_image, get_image_rating
app = Flask(__name__)

#connect to database
db = SQL("sqlite:///gallery.db")
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS images (image_id INTEGER PRIMARY KEY, user_id INTEGER, image TEXT, title TEXT, description TEXT, gender TEXT, upvotes INTEGER DEFAULT 0, FOREIGN KEY (user_id) REFERENCES users(id))")
db.execute("CREATE TABLE IF NOT EXISTS reviews (review_id INTEGER PRIMARY KEY, image_id INTEGER, user_id INTEGER, rating INTEGER DEFAULT 0, comment TEXT, FOREIGN KEY (image_id) REFERENCES images(image_id), FOREIGN KEY (user_id) REFERENCES users(id))")
db.execute("CREATE TABLE IF NOT EXISTS upvotes (user_id INTEGER, image_id INTEGER, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (image_id) REFERENCES images(image_id))")

#make cookies
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Set upload folder
app.config['UPLOAD_FOLDER'] = 'static'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

#main page
@app.route('/')
def index():
    return render_template('index.html')

#gallery page
@app.route('/gallery')
def gallery():
    files = db.execute("SELECT * FROM images JOIN users ON users.id = images.user_id ORDER BY images.image_id DESC")
    reviews = db.execute("SELECT * FROM reviews ORDER BY image_id DESC")

    return render_template('gallery.html', files=files, image_exist=image_exist, reviews=reviews, get_image_rating=get_image_rating)

#handle uploading file
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

        #generate a filename
        unique_filename = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
        #go to top of file
        image.stream.seek(0)

        if not (name and description and gender):
            return 'please fill out all fields'

        #save file in /static/
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        image.save(file_path)

        db.execute('INSERT INTO images (user_id, image, title, description, gender) VALUES (?, ?, ?, ?, ?)', session["user_id"], unique_filename, name, description, gender)

        return redirect('/')

    return render_template('upload.html')

#login
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
        
        #generate secure password
        hashed_password = generate_password_hash(password)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        
        #check if password is correct and user exists
        if not rows or not check_password_hash(rows[0]["password"], password):
                return "invalid username and/or password"
        
        session["user_id"] = rows[0]["id"]
        return redirect('/')

    return render_template('login.html')

#handle register
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

#clear cookies
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

#contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

#upvote a post
@app.route('/upvote', methods=['POST'])
def upvote():
    if request.method == 'POST':
        # Get the file ID from the request data
        try:
            data = request.get_json()
            file_id = data['fileId']

            # Update the SQL table
            db.execute("UPDATE images SET upvotes = upvotes + 1 WHERE image_id = ?", file_id)

            updated_rating = get_image_rating(file_id)

            # Respond with JSON indicating success
            return jsonify({'rating': updated_rating}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        

#check if image exists
def image_exist(image):
    return os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], image))

#run app as debug
if __name__ == "__main__":
    app.run(debug=True)