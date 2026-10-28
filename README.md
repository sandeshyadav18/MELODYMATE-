MelodyMate – Your Musical Bestfriend
MelodyMate is a web-based Music Playlist Manager developed as an academic project for the B.Sc. Computer Science programme. It provides users with a simple and interactive way to manage playlists and play their favourite songs.
Project Overview
The application brings together a frontend interface, a Flask backend, and a MongoDB database. Users can register and log in, manage playlists, organize songs, and use basic music playback controls.
Features
- User registration and login
- Personalized user dashboard
- Create, edit, and delete playlists
- Add and remove songs from playlists
- Organize songs according to user preferences
- Music playback controls such as play, pause, next/skip, shuffle, and repeat (as supported by the implementation)
- User profile management
- Responsive interface for desktop, laptop, and mobile browsers
- Store and retrieve user, playlist, and song information using MongoDB
Technology Stack
Component	Technology	Purpose
Frontend	HTML5, CSS3, JavaScript	Page structure, styling, and interactive controls
UI styling	Tailwind CSS	Responsive and modern interface
Backend	Python, Flask	Routes, application logic, and user requests
Database	MongoDB	User details, playlists, and song metadata
Development	Visual Studio Code	Writing and managing project code
Testing	Browser Developer Tools, Postman	Debugging and API testing


Main Modules
1. Authentication Module – Registration, login, credential checking, and session handling.
2. Playlist Management Module – Create and manage playlists and add or remove songs.
3. Music Playback Module – Control supported playback actions through the web interface.
4. User Profile Module – View or update user profile information.
5. Database Module – Store and retrieve application data from MongoDB.
System Requirements
- Python 3
- Flask and the Python packages used by the project
- MongoDB server or a configured MongoDB connection
- A modern web browser
- A code editor such as Visual Studio Code (recommended)
Setup and Run
Note: The report identifies Flask and MongoDB, but does not specify the exact repository structure, dependency list, environment-variable names, or startup command. Adjust these steps to match the actual source code.

1. Get the project files
   - Download or clone the project repository, or place the source files in a local project folder.
2. Open the project folder
   - Open the folder in Visual Studio Code or a terminal.
3. Create and activate a virtual environment (recommended)
   Windows:
   python -m venv venv
   venv\Scripts\activate
   macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
4. Install dependencies
   - If the project contains a requirements.txt file, run:
   pip install -r requirements.txt
   - If it does not, install the packages listed/imported by your actual Flask application. Do not assume the dependency list from this README.
5. Configure MongoDB
   - Start MongoDB locally or use your configured MongoDB service.
   - Set the database connection string in the configuration expected by the application. Do not commit passwords, secret keys, or other credentials to GitHub.
6. Run the Flask application
   - Use the startup command specified by your project. Common Flask projects may use:
   flask --app app run --debug
   - Replace app with the actual Python module or application entry point. If your project has its own run instructions, follow those instead.
7. Open the application
   - Open the local URL shown in the terminal (commonly http://127.0.0.1:5000) in your browser.
Basic Usage
1. Register a user account or log in.
2. Open the dashboard.
3. Create a playlist.
4. Add songs and manage the playlist.
5. Select a song and use the available playback controls.
6. Update profile details when required.
Testing
The project report describes testing for the following workflows:
- Login with valid credentials
- Login with invalid credentials
- Playlist creation
- Adding a song to a playlist
- Music playback
- Deleting a playlist
- Updating profile information
The report records these test cases as passed. Re-run them against the current source code after making changes.
Known Limitations
- The web application depends on internet or network availability as described in the report.
- The current version does not include a song recommendation system.
- Playlist sharing and collaborative playlists are not available.
- Song management relies on manually uploaded songs rather than external music-library integrations.
- Offline playback and some advanced player features are not included.
- Additional performance and scaling work may be needed for large numbers of concurrent users.
Future Improvements
- Offline playback support
- Personalized song recommendations
- Playlist sharing and collaboration
- Integration with external music APIs
- Lyrics, equalizer, and other advanced playback options
- Android/iOS application
- Cloud deployment and scalability improvements
- Two-factor authentication and additional security improvements
Academic Project
- Project: MelodyMate – Your Musical Bestfriend (Music Playlist Manager)
- Submitted by: Sandesh Rajvant Yadav
- Programme: T.Y. B.Sc. Computer Science, Semester V
- Institution: Sanpada College of Commerce and Technology
- Academic Year: 2026–2027
- Project Guide: Prof. Jyoti Yadav
References
- Flask Documentation
- MongoDB Documentation
- Tailwind CSS Documentation
- W3Schools
- GeeksforGeeks
