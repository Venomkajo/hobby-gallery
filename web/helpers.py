import magic
from cs50 import SQL

def check_image(image):
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(image.read())
    return file_mime_type.startswith('image/')

def get_image_rating(id):
    db = SQL("sqlite:///gallery.db")
    rating = db.execute("SELECT rating FROM reviews WHERE image_id = ?", id)
    value = None  # Default value if no rating is found
    for row in rating:
        value = row[0]  # Get the rating from the first column of the row
        break  # Stop looping after the first row
    return value

