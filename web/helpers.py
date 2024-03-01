import magic
from cs50 import SQL

db = SQL("sqlite:///gallery.db")

#check if a file is an image
def check_image(image):
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(image.read())
    return file_mime_type.startswith('image/')

#get current image rating
def get_image_rating(id):
    rating = db.execute("SELECT upvotes FROM images WHERE image_id = ?", id)
    value = None  # Default value if no rating is found
    for row in rating:
        value = row['upvotes']  # Get the rating from the first column of the row
        break  # Stop looping after the first row
    return value
