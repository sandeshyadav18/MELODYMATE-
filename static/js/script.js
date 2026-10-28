const audioPlayer = document.getElementById('bottom-audio');
let playlistSongs = [];
let currentIndex = 0;

// Play song from path (for search results & song cards)
function playSongFromPath(path, title, cover){
    audioPlayer.src = path;
    audioPlayer.play();
    currentIndex = 0;
    playlistSongs = [{filePath: path, title, coverImage: cover}];
    updatePlayerUI(title, cover);
}

function updatePlayerUI(title, cover){
    document.getElementById('player-title').innerText = title;
    
    const coverEl = document.getElementById('player-cover');
    coverEl.src = cover;
    coverEl.classList.remove('hidden');
}

// Next / Prev / Shuffle
function nextSong(){ currentIndex = (currentIndex +1)%playlistSongs.length; playSongFromPath(playlistSongs[currentIndex].filePath, playlistSongs[currentIndex].title, playlistSongs[currentIndex].artist, playlistSongs[currentIndex].coverImage);}
function prevSong(){ currentIndex = (currentIndex-1+playlistSongs.length)%playlistSongs.length; playSongFromPath(playlistSongs[currentIndex].filePath, playlistSongs[currentIndex].title, playlistSongs[currentIndex].artist, playlistSongs[currentIndex].coverImage);}
function shuffleSong(){ currentIndex = Math.floor(Math.random()*playlistSongs.length); playSongFromPath(playlistSongs[currentIndex].filePath, playlistSongs[currentIndex].title, playlistSongs[currentIndex].artist, playlistSongs[currentIndex].coverImage);}

// Search functionality

const searchInput = document.getElementById('search-input');
const genreFilter = document.getElementById('genre-filter');
const moodFilter = document.getElementById('mood-filter');
const resultsDiv = document.getElementById('search-results');

async function fetchSongs(){
    let q = searchInput.value;
    let genre = genreFilter.value;
    let mood = moodFilter.value;
    const res = await fetch(`/search?q=${q}&genre=${genre}&mood=${mood}`);
    const results = await res.json();
    resultsDiv.innerHTML='';
    results.forEach((song,i)=>{
        const div = document.createElement('div');
        div.className = 'bg-gray-800 rounded-lg overflow-hidden shadow hover:shadow-lg transition duration-300';
        div.innerHTML = `
            <img src="${song.coverImage}" class="w-full h-48 object-cover">
            <div class="p-4">
                <h3 class="font-bold text-lg">${song.title}</h3>
                
                <button onclick="playSongFromPath('${song.filePath}','${song.title}','${song.coverImage}')" class="mt-2 bg-indigo-600 px-3 py-1 rounded hover:bg-indigo-500">Play</button>
            </div>
        `;
        resultsDiv.appendChild(div);
    });
}

// Event listeners
searchInput.addEventListener('input', fetchSongs);
genreFilter.addEventListener('change', fetchSongs);
moodFilter.addEventListener('change', fetchSongs);

// Optional: Autocomplete (show top 5 matching titles)
searchInput.addEventListener('input', async ()=>{
    let q = searchInput.value;
    if(!q) return;
    const res = await fetch(`/search?q=${q}`);
    const results = await res.json();
    console.log('Autocomplete:', results.slice(0,5).map(s=>s.title)); // can implement dropdown
});


