from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
import os
import uuid
from cs50 import SQL
import magic
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import check_image, get_image_rating
app = Flask(__name__)

# connect to database
db = SQL("sqlite:///gallery.db")
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, banned BOOLEAN DEFAULT 0)")
db.execute("CREATE TABLE IF NOT EXISTS images (image_id INTEGER PRIMARY KEY, user_id INTEGER, image TEXT, title TEXT, description TEXT, gender TEXT, upvotes INTEGER DEFAULT 0, FOREIGN KEY (user_id) REFERENCES users(id))")
db.execute("CREATE TABLE IF NOT EXISTS reviews (review_id INTEGER PRIMARY KEY, image_id INTEGER, user_id INTEGER, comment TEXT, FOREIGN KEY (image_id) REFERENCES images(image_id) ON DELETE CASCADE, FOREIGN KEY (user_id) REFERENCES users(id))")
db.execute("CREATE TABLE IF NOT EXISTS upvotes (user_id INTEGER, image_id INTEGER, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (image_id) REFERENCES images(image_id) ON DELETE CASCADE)")

# make cookies
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# set upload folder
app.config['UPLOAD_FOLDER'] = 'static'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logged_in = False

# main page
@app.route('/')
def index():
    return render_template('index.html')


# gallery page
@app.route('/gallery', methods=["GET", "POST"])
def gallery():
    sort = 'newest'
    search = ''
    user_search = ''

    if request.method == "POST":
        
        if request.form['sort']:
            sort = request.form['sort']
        if request.form['search']:
            search = request.form['search']
        if request.form['user_search']:
            user_search = request.form['user_search']

    # check if logged in
    if session.get("user_id"):
        user_id = session['user_id']
    else:
        user_id = 0

    # sort or search gallery
    if search and user_search:
        formatted_search = '%{}%'.format(search)
        formatted_user_search = '%{}%'.format(user_search)
        files = db.execute("SELECT * FROM images JOIN users ON users.id = images.user_id WHERE title LIKE ? AND username LIKE ? ORDER BY images.image_id DESC", formatted_search, formatted_user_search)
    elif search:
        formatted_search = '%{}%'.format(search)
        files = db.execute("SELECT * FROM images JOIN users ON users.id = images.user_id WHERE title LIKE ? ORDER BY images.image_id DESC", formatted_search)
    elif user_search:
        formatted_user_search = '%{}%'.format(user_search)
        files = db.execute("SELECT * FROM images JOIN users ON users.id = images.user_id WHERE username LIKE ? ORDER BY images.image_id DESC", formatted_user_search)
    else:
        if sort == 'newest':
            files = db.execute("SELECT * FROM images JOIN users ON users.id = images.user_id ORDER BY images.image_id DESC")
        elif sort == 'oldest':
            files = db.execute("SELECT * FROM images JOIN users ON users.id = images.user_id ORDER BY images.image_id ASC")
        elif sort == 'upvoted':
            files = db.execute("SELECT * FROM images JOIN users ON users.id = images.user_id ORDER BY images.upvotes DESC")
        elif sort == 'random':
            files = db.execute("SELECT * FROM images JOIN users ON users.id = images.user_id ORDER BY RANDOM()")
        else:
            return render_template('error.html', text="sorting error")
    
    return render_template('gallery.html', files=files, image_exist=image_exist, get_image_rating=get_image_rating, vote_check=vote_check, user_id=user_id, get_comment=get_comment)


# handle uploading file
@app.route('/upload', methods=["GET", "POST"])
def upload():
    
    # check for login
    if session.get("user_id") is None:
        return redirect("/login")

    # make sure image exists
    if request.method == ("POST"):
        if 'image' not in request.files:
            return render_template('error.html', text="form error")
        
        image = request.files['image']

        if image.filename == "":
            return render_template('error.html', text="no image submitted")
        
        if check_image(image) == False:
            return render_template('error.html', text="not an image")
        
        name = request.form['name']
        description = request.form['description']
        gender = request.form['gender']

        # generate a filename
        unique_filename = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
        # go to top of file
        image.stream.seek(0)

        if not (name and description and gender):
            return render_template('error.html', text="not all fields filled out")

        # save file in /static/
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        image.save(file_path)

        db.execute('INSERT INTO images (user_id, image, title, description, gender) VALUES (?, ?, ?, ?, ?)', session["user_id"], unique_filename, name, description, gender)

        return redirect('/')

    return render_template('upload.html')


# login
@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":

        session.clear()

        username = request.form['username']
        password = request.form['password']

        if not username:
            return render_template('error.html', text="username not entered")
        elif not password:
            return render_template('error.html', text="password not entered")
        
        # generate secure password
        hashed_password = generate_password_hash(password)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        
        # check if password is correct and user exists
        if not rows or not check_password_hash(rows[0]["password"], password):
                return render_template('error.html', text="invalid username or password")
        
        session["user_id"] = rows[0]["id"]
        return redirect('/')

    return render_template('login.html')


# handle register
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method =="POST":

        # clear cookies
        session.clear()

        # get form
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        # check if empty
        if not username or not password or not confirm:
            return render_template('error.html', text="not all fields filled out")
        elif len(password) < 8:
            return render_template('error.html', text="password should be longer or equal to 8 characters")
        elif password != confirm:
            return render_template('error.html', text="passwords do not match")
        elif db.execute("SELECT username FROM users WHERE username = ?", username):
            return render_template('error.html', text="username is taken")

        hashed_password = generate_password_hash(password)
        
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, hashed_password)

        return redirect("/login")

    return render_template('register.html')


# clear cookies
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')


# upvote a post
@app.route('/upvote', methods=['POST'])
def upvote():
    if request.method == 'POST':
        try:
            # get data
            data = request.get_json()
            file_id = data['fileId']
            user_id = session["user_id"]
            test = db.execute("SELECT * FROM upvotes WHERE user_id = ? AND image_id = ?", user_id, file_id)

            # if test exists do nothing
            if test:
                pass
            else:
                db.execute("INSERT INTO upvotes(user_id, image_id) VALUES (?, ?)", user_id, file_id)

            db.execute("UPDATE images SET upvotes = upvotes + 1 WHERE image_id = ?", file_id)

            updated_rating = get_image_rating(file_id)
            value = {'rating': updated_rating}

            # respond with json
            return jsonify(value), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# add comment to image
@app.route("/comment", methods=["POST"])
def add_comment():
    # get form
    comment = request.form['comment']
    image_id = request.form['comment_id']

    # check if empty
    if not comment or not image_id or not session['user_id']:
        return render_template('error.html', text="comment is empty")
    
    # insert into reviews table
    db.execute("INSERT INTO reviews (image_id, user_id, comment) VALUES (?, ?, ?)", image_id, session['user_id'], comment)

    return redirect('/gallery')

# delete image, only for admins
@app.route("/delete", methods=["POST"])
def delete_image():
    del_id = request.form['delete_id']
    if db.execute("SELECT * FROM images WHERE image_id = ?", del_id):
        db.execute("DELETE FROM images WHERE image_id = ?", del_id)
    else:
        return render_template('error.html', text="image already deleted")
    return redirect("/")


@app.route("/ban_user", methods=['POST'])
def ban_user():

    username = request.form['ban_username']

    if username:
        confirm = db.execute("SELECT banned FROM users WHERE username = ?", username)
        for i in confirm:
            if i['banned'] == 0:
                db.execute("UPDATE users SET banned = 1 WHERE username = ?", username)
            else:
                return render_template('error.html', text="user already banned")
            return redirect("/")
        else:
            return "error"


@app.route("/ban")
def ban():
    return render_template('ban.html')


# check if image exists
def image_exist(image):
    return os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], image))


# check if user already upvoted an image
def vote_check(id):
    user_id = session["user_id"]
    query = db.execute("SELECT * FROM upvotes WHERE user_id = ? AND image_id = ?", user_id, id)
    if query:
        return False
    else:
        return True


# get comments from reviews table for image    
def get_comment(id):
    query = db.execute("SELECT * FROM reviews WHERE image_id = ?", id)
    if query:
        comments = []
        for answers in query:
            user_info = db.execute("SELECT username, banned FROM users WHERE id = ?", answers['user_id'])[0]
            if user_info and not user_info['banned']:
                dictionary = {'comment': answers['comment'], 'username': user_info['username']}
                comments.append(dictionary)
        return comments
    else:
        return False

   
def is_banned(user_id):
    confirm = db.execute("SELECT banned FROM users WHERE id = ?", user_id)
    for i in confirm:
        if i['banned'] == 1:
            return True
        else:
            return False

       
@app.before_request
def check_ban():
    if session.get("user_id"):
        user_id = session['user_id']
        if is_banned(user_id):
            if request.endpoint != 'ban':
                return redirect('/ban')


# define a context processor to inject variables into all templates
@app.context_processor
def inject_layout():
    if 'user_id' in session:
        logged_in = True
    else:
        logged_in = False
    return dict(logged_in=logged_in)


# run app as debug
if __name__ == "__main__":
    app.run(debug=True)