import os
import shutil
from pymongo import MongoClient
from mutagen.easyid3 import EasyID3
import librosa
import numpy as np

# === SETTINGS ===
LOCAL_SONGS_DIR = r"C:\Users\saksh\OneDrive\Desktop\Melodymate\static\music"   # your folder with songs
LOCAL_COVERS_DIR = r"C:\Users\saksh\OneDrive\Desktop\Melodymate\static\covers" # your folder with covers
PROJECT_MUSIC_DIR = os.path.join("static", "music")
PROJECT_COVERS_DIR = os.path.join("static", "covers")

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "melodymate"

# === SETUP DB ===
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
songs_coll = db["songs"]

os.makedirs(PROJECT_MUSIC_DIR, exist_ok=True)
os.makedirs(PROJECT_COVERS_DIR, exist_ok=True)

def song_exists(file_path):
    return songs_coll.find_one({"filePath": file_path}) is not None

def detect_genre_mood(file_path):
    try:
        # Load only first 60s (faster)
        y, sr = librosa.load(file_path, duration=60)
        
        # Features
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        energy = np.mean(np.abs(y))

        # Simple classification rules
        if tempo > 140 and zcr > 0.1:
            genre, mood = "EDM / Dance", "Energetic"
        elif tempo > 100 and spectral_centroid > 2000:
            genre, mood = "Pop", "Happy"
        elif energy < 0.02 and spectral_centroid < 1500:
            genre, mood = "Classical / Acoustic", "Calm"
        else:
            genre, mood = "Indie / Lo-fi", "Chill"

        return genre, mood

    except Exception as e:
        print(f"⚠️ Could not analyze {file_path}: {e}")
        return "Unknown", "Unknown"

for fname in os.listdir(LOCAL_SONGS_DIR):
    if not fname.lower().endswith(".mp3"):
        continue

    base_name = os.path.splitext(fname)[0].replace(" ", "_")
    song_src = os.path.join(LOCAL_SONGS_DIR, fname)
    song_dst = os.path.join(PROJECT_MUSIC_DIR, base_name + ".mp3")

    if not os.path.exists(song_dst):
        shutil.copy(song_src, song_dst)
        print(f"Copied: {fname}")

    file_path = f"/static/music/{base_name}.mp3"
    if song_exists(file_path):
        print(f"Skipping Mongo insert (exists): {base_name}")
        continue

    # --- Metadata ---
    title = base_name
    try:
        audio = EasyID3(song_src)
        title = audio.get("title", [title])[0]
    
    except:
        pass

    # --- Genre & Mood ---
    genre, mood = detect_genre_mood(song_src)

    # --- Cover ---
    cover_file = None
    for ext in [".jpg", ".jpeg", ".png"]:
        cover_candidate = os.path.join(LOCAL_COVERS_DIR, base_name + ext)
        if os.path.exists(cover_candidate):
            cover_dst = os.path.join(PROJECT_COVERS_DIR, base_name + ext)
            if not os.path.exists(cover_dst):
                shutil.copy(cover_candidate, cover_dst)
            cover_file = f"/static/covers/{base_name + ext}"
            break

    if not cover_file:
        cover_file = "/static/covers/default.jpg"

    # --- Insert into Mongo ---
    doc = {
        "title": title,
        
        "filePath": file_path,
        "coverImage": cover_file,
        "genre": genre,
        "mood": mood
    }
    songs_coll.insert_one(doc)
    print(f"✅ Added: {title} ({genre}, {mood}) with cover {cover_file}")

print("🎵 Done uploading all songs with covers!")
