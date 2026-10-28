# add_songs_to_mongo.py
import os
from pymongo import MongoClient

# Adjust if your config.py uses a different URI
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "melodymate"
MUSIC_DIR = os.path.join("static", "music")
DEFAULT_COVER = "/static/music/default_cover.jpg"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
songs_coll = db["songs"]

def already_exists(file_path):
    return songs_coll.find_one({"filePath": file_path}) is not None

for fname in os.listdir(MUSIC_DIR):
    if not fname.lower().endswith(".mp3"):
        continue
    file_path = f"/static/music/{fname}"
    if already_exists(file_path):
        print("Skipping exists:", fname)
        continue
    doc = {
        "title": os.path.splitext(fname)[0],
        
        "filePath": file_path,
        "coverImage": DEFAULT_COVER,
        "genre": "Unknown",
        "mood": "Unknown"
    }
    songs_coll.insert_one(doc)
    print("Inserted:", fname)
print("Done.")
