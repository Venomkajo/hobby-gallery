import magic

def check_image(image):
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(image.read())
    return file_mime_type.startswith('image/')
