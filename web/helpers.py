import magic
from cs50 import SQL

db = SQL("sqlite:///gallery.db")

#check if a file is an image, uses magic library
def check_image(image):
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(image.read())
    return file_mime_type.startswith('image/')


#get current image rating
def get_image_rating(id):
    rating = db.execute("SELECT upvotes FROM images WHERE image_id = ?", id)
    value = None
    #get only one result
    for row in rating:
        value = row['upvotes']
        break
    return value
