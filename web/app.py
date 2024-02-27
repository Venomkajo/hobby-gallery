from flask import Flask, render_template, request
app = Flask(__name__)
import os
import cs50
import magic
from helpers import check_image

db = cs50.SQL("sqlite:///gallery.db")
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS images (image_id INTEGER PRIMARY KEY, user_id INTEGER, image BLOB, FOREIGN KEY (user_id) REFERENCES users(id))")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gallery')
def get_gallery():
    picture_files = os.listdir('static/pictures')
    return render_template('gallery.html', picture_files=picture_files)

@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == ("POST"):
        if 'image' not in request.files:
            return 'form error'
        
        image = request.files['image']

        if image.filename == "":
            return 'no image submitted'
        
        if check_image(image) == False:
            return 'not an image'


    return render_template('upload.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run()