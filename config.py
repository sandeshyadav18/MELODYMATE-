import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    MONGO_URI = 'mongodb://localhost:27017/melodymate'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/music')
