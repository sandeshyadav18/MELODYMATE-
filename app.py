import os 
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from bson import ObjectId
from werkzeug.utils import secure_filename
from config import Config
from models import hash_password, check_password
from flask import send_file, abort
# ---------------- App Setup ----------------
app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)

app.secret_key = "supersecretkey"
UPLOAD_FOLDER = os.path.join("static", "music")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ---------------- User Class ----------------
class User(UserMixin):
    def __init__(self, data):
        self.id = str(data['_id'])
        self.username = data['username']
        self.email = data['email']

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    return User(user) if user else None


# ---------------- Auth ----------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})
        if user and check_password(user['password'], password):
            login_user(User(user))
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if mongo.db.users.find_one({'email': email}):
            flash('Email already exists!')
        else:
            hashed = hash_password(password)
            mongo.db.users.insert_one({
                'username': username,
                'email': email,
                'password': hashed,
                'playlists': []
            })
            flash('Account created! Login now.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------------- Dashboard ----------------
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    # Create new playlist
    if request.method == "POST" and "playlist_name" in request.form:
        playlist_name = request.form["playlist_name"]
        mongo.db.playlists.insert_one({
            "name": playlist_name,
            "songs": [],
            "userId": ObjectId(current_user.id)
        })
        return redirect(url_for("dashboard"))

    # Fetch all songs
    songs = list(mongo.db.songs.find())

    # Fetch playlists and resolve songs
    playlists = []
    for pl in mongo.db.playlists.find({"userId": ObjectId(current_user.id)}):
        resolved_songs = list(mongo.db.songs.find({"_id": {"$in": pl.get("songs", [])}}))
        playlists.append({
            "_id": pl["_id"],
            "name": pl["name"],
            "songs": resolved_songs
        })

    return render_template("dashboard.html", songs=songs, playlists=playlists)

# ---------------- Playlist ----------------
@app.route("/add_to_playlist", methods=["POST"])
@login_required
def add_to_playlist():
    playlist_id = request.form["playlist_id"]
    song_id = request.form["song_id"]

    mongo.db.playlists.update_one(
        {"_id": ObjectId(playlist_id), "userId": ObjectId(current_user.id)},
        {"$addToSet": {"songs": ObjectId(song_id)}}
    )
    flash("Song added to playlist!")
    return redirect(url_for("dashboard"))

# ---------------- API for fetching playlist songs ----------------
@app.route("/playlist/<playlist_id>/songs")
@login_required
def get_playlist_songs(playlist_id):
    playlist = mongo.db.playlists.find_one({"_id": ObjectId(playlist_id), "userId": current_user.id})
    if not playlist:
        return jsonify([])
    song_ids = playlist.get("songs", [])
    songs = list(mongo.db.songs.find({"_id": {"$in": song_ids}}))
    return jsonify([{
        "_id": str(s["_id"]),
        "title": s["title"],
        
        "filePath": s["filePath"],
        "coverImage": s.get("coverImage", "/static/music/default_cover.jpg")
    } for s in songs])

# ---------------- Add Single Song ----------------
@app.route('/upload_song', methods=['POST'])
@login_required
def upload_song():
    title = request.form['title']
    
    genre = request.form.get('genre', 'Unknown')
    mood = request.form.get('mood', 'Unknown')

    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    mongo.db.songs.insert_one({
        'title': title,
        
        'filePath': f'/static/music/{filename}',
        'coverImage': '/static/music/default_cover.jpg',
        'genre': genre,
        'mood': mood
    })
    return redirect(url_for('dashboard'))

@app.route("/download/<song_id>")
@login_required
def download_song(song_id):
    # Find the song in DB
    song = mongo.db.songs.find_one({"_id": ObjectId(song_id)})
    if not song:
        abort(404)

    # song["filePath"] looks like "/static/music/filename.mp3"
    file_path = song.get("filePath")
    if not file_path:
        abort(404)

    # Convert relative path to actual system path
    abs_path = os.path.join(app.root_path, file_path.lstrip("/"))

    if not os.path.exists(abs_path):
        abort(404)

    return send_file(abs_path, as_attachment=True)


@app.route("/my_playlist", methods=["GET"])
@login_required
def my_playlist():
    playlists = list(mongo.db.playlists.find({"userId": ObjectId(current_user.id)}))

    for playlist in playlists:
        song_ids = [s for s in playlist.get("songs", [])]
        songs = list(mongo.db.songs.find({"_id": {"$in": song_ids}}))
        playlist["songs"] = songs  # attach songs to playlist

    return render_template("my_playlist.html", playlists=playlists)



# Rename playlist (accepts form or JSON)
@app.route("/rename_playlist", methods=["POST"])
@login_required
def rename_playlist():
    # Accept JSON (AJAX) or form submit
    if request.is_json:
        data = request.get_json()
        playlist_id = data.get("playlist_id")
        new_name = data.get("new_name", "").strip()
    else:
        playlist_id = request.form.get("playlist_id")
        new_name = request.form.get("new_name", "").strip()

    if not playlist_id or not new_name:
        if request.is_json:
            return jsonify({"success": False, "error": "Missing data"}), 400
        flash("Please provide a new name for the playlist.")
        return redirect(url_for("my_playlist"))

    result = mongo.db.playlists.update_one(
        {"_id": ObjectId(playlist_id), "userId": ObjectId(current_user.id)},
        {"$set": {"name": new_name}}
    )

    if request.is_json:
        if result.modified_count:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Not found or no change"}), 404

    flash("Playlist renamed successfully!")
    return redirect(url_for("my_playlist"))


# Delete playlist (accepts form or JSON)
@app.route("/delete_playlist", methods=["POST"])
@login_required
def delete_playlist():
    if request.is_json:
        data = request.get_json()
        playlist_id = data.get("playlist_id")
    else:
        playlist_id = request.form.get("playlist_id")

    if not playlist_id:
        if request.is_json:
            return jsonify({"success": False, "error": "Missing playlist_id"}), 400
        flash("Invalid request.")
        return redirect(url_for("my_playlist"))

    result = mongo.db.playlists.delete_one(
        {"_id": ObjectId(playlist_id), "userId": ObjectId(current_user.id)}
    )

    if request.is_json:
        if result.deleted_count:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Not found"}), 404

    flash("Playlist deleted.")
    return redirect(url_for("my_playlist"))

@app.route("/remove_from_playlist", methods=["POST"])
@login_required
def remove_from_playlist():
    playlist_id = request.form.get("playlist_id")
    song_id = request.form.get("song_id")

    mongo.db.playlists.update_one(
        {"_id": ObjectId(playlist_id), "userId": ObjectId(current_user.id)},
        {"$pull": {"songs": ObjectId(song_id)}}
    )

    flash("Song removed from playlist", "success")
    return redirect(url_for("my_playlist"))


# ---------------- Profile ----------------
@app.route("/profile", methods=["GET"])
@login_required
def profile():
    playlists = list(mongo.db.playlists.find({"userId": ObjectId(current_user.id)}))

    # Attach full song info to each playlist
    for playlist in playlists:
        song_ids = playlist.get("songs", [])
        if song_ids:
            playlist["songs"] = list(
                mongo.db.songs.find({"_id": {"$in": song_ids}})
            )
        else:
            playlist["songs"] = []

    return render_template("profile.html", current_user=current_user, playlists=playlists)


@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    new_username = request.form.get("username")
    

    # Update in MongoDB
    mongo.db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"username": new_username}}
    )

    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile"))

# ---------------- Admin Bulk Upload ----------------
@app.route("/admin/upload", methods=["GET", "POST"])
@login_required
def admin_upload():
    if request.method == "POST":
        files = request.files.getlist("songs")
        for file in files:
            if file and file.filename.endswith(".mp3"):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                mongo.db.songs.insert_one({
                    'title': os.path.splitext(filename)[0],
                    
                    'filePath': f"/static/music/{filename}",
                    'coverImage': '/static/music/default_cover.jpg',
                    'genre': "Unknown",
                    'mood': "Unknown"
                })
        flash("Songs uploaded successfully!")
        return redirect(url_for("dashboard"))
    return render_template("admin_upload.html")

# ---------------- Search API ----------------
@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    results = list(mongo.db.songs.find({"title": {"$regex": query, "$options": "i"}}))
    return jsonify([{"title": s["title"], "filePath": s["filePath"]} for s in results])

# ---------------- Run ----------------
if __name__=='__main__':
    app.run(debug=True)
