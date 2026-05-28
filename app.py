# Path : a/

import os
import urllib.parse
from http.server import SimpleHTTPRequestHandler
import socketserver
import io
import json

from mutagen import File as MutagenFile
from PIL import Image

PORT = 1234

class CleanMusicServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        decoded_path = urllib.parse.unquote(parsed_url.path)
        
        # 1. ENDPOINT EMBEDDED ART
        if decoded_path == '/get_embedded_cover':
            params = urllib.parse.parse_qs(parsed_url.query)
            audio_file = params.get('file', [None])[0]
            
            if audio_file and os.path.exists(audio_file):
                try:
                    file_ext = os.path.splitext(audio_file)[1].lower()
                    audio = MutagenFile(audio_file)
                    image_data = None
                    
                    if file_ext == '.flac' and audio.pictures:
                        image_data = audio.pictures[0].data
                    elif file_ext == '.mp3':
                        for key in audio.keys():
                            if key.startswith('APIC'):
                                image_data = audio[key].data
                                break
                    elif hasattr(audio, 'pictures') and audio.pictures:
                        image_data = audio.pictures[0].data

                    if image_data:
                        img = Image.open(io.BytesIO(image_data))
                        img = img.convert('RGB')
                        
                        # --- FIX STRETCH: Center Crop ke 1:1 Square ---
                        width, height = img.size
                        min_dim = min(width, height)
                        left = (width - min_dim) / 2
                        top = (height - min_dim) / 2
                        right = (width + min_dim) / 2
                        bottom = (height + min_dim) / 2
                        
                        img = img.crop((left, top, right, bottom))
                        img.thumbnail((320, 320), Image.Resampling.LANCZOS)
                        # ---------------------------------------------
                        
                        output = io.BytesIO()
                        img.save(output, format='JPEG', quality=85)
                        final_data = output.getvalue()

                        self.send_response(200)
                        self.send_header("Content-type", "image/jpeg")
                        self.send_header("Content-Length", str(len(final_data)))
                        self.send_header("Cache-Control", "public, max-age=86400")
                        self.end_headers()
                        self.wfile.write(final_data)
                        return
                        
                except Exception as e:
                    print(f"Gagal memproses artwork: {e}")
            
            self.send_response(404)
            self.end_headers()
            return

        # 2. RENDER HALAMAN UTAMA
        if decoded_path == '/' or decoded_path == '/index.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            valid_extensions = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')
            all_files = os.listdir('.')
            music_files = [f for f in all_files if f.lower().endswith(valid_extensions)]
            music_files.sort()
            
            songs_json = []
            for f in music_files:
                clean_name = os.path.splitext(f)[0]
                parts = [p.strip() for p in clean_name.split('-')]
                fallback_artist = "Unknown Artist"
                fallback_title = clean_name
                fallback_album = "Unknown Album"
                
                if len(parts) >= 2:
                    fallback_artist = parts[0]
                    fallback_title = parts[1]
                    fallback_album = parts[1] + " (Single)"
                    if len(parts) >= 3:
                        fallback_album = parts[2]
                else:
                    fallback_title = clean_name.replace('_', ' ')

                artist = ""
                title = ""
                album = ""
                try:
                    audio = MutagenFile(f)
                    if audio:
                        if 'artist' in audio and audio['artist'][0].strip(): artist = audio['artist'][0].strip()
                        if 'title' in audio and audio['title'][0].strip(): title = audio['title'][0].strip()
                        if 'album' in audio and audio['album'][0].strip(): album = audio['album'][0].strip()
                except:
                    pass

                if not artist or artist == '0': artist = fallback_artist
                if not title or title == '0': title = fallback_title
                if not album or album == '0': album = fallback_album

                songs_json.append({
                    "file": f,
                    "title": title,
                    "artist": artist,
                    "album": album
                })
            
            json_data_string = json.dumps(songs_json)

            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
                <title>Faez Flaco</title>
                <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
                <script src="https://unpkg.com/lucide@latest"></script>
                <style>
                    /* FIX BACKGROUND STRETCH: Guna pseudo-element ::before */
                    body {{
                        position: relative;
                        background-color: #0f172a;
                    }}
                    body::before {{
                        content: "";
                        position: fixed;
                        top: 0; left: 0; right: 0; bottom: 0;
                        z-index: -1;
                        background-image: linear-gradient(rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.8)), url('img.jpg');
                        background-size: contain; /* Mengekalkan aspect ratio 736x974 tanpa stretch */
                        background-repeat: no-repeat;
                        background-position: center;
                        width: 100%;
                        height: 100%;
                    }}
                    .tab-active {{ color: #ffffff !important; border-bottom-color: #3b82f6 !important; background-color: rgba(255, 255, 255, 0.15) !important; }}
                    input[type="range"].seek-slider {{ -webkit-appearance: none; appearance: none; width: 100%; background: transparent; cursor: pointer; }}
                    input[type="range"].seek-slider:focus {{ outline: none; }}
                    input[type="range"].seek-slider::-webkit-slider-thumb {{ -webkit-appearance: none; appearance: none; height: 14px; width: 14px; border-radius: 50%; background: #3b82f6; margin-top: -5px; }}
                    input[type="range"].seek-slider::-webkit-slider-runnable-track {{ width: 100%; height: 4px; background: rgba(255, 255, 255, 0.2); border-radius: 2px; }}
                    .btn-active {{ color: #3b82f6 !important; }}
                </style>
            </head>
            <body class="text-slate-100 min-h-screen pb-44 bg-transparent select-none">

                <div class="sticky top-0 z-50 bg-slate-900/80 border-b border-slate-700/40 backdrop-blur-md">
                    <nav class="px-4 py-4 flex justify-between items-center">
                        <div class="flex items-center gap-2">
                            <i data-lucide="music" class="w-5 h-5 text-blue-500"></i>
                            <span class="font-bold tracking-tight text-lg text-white">Faez Flaco</span>
                        </div>
                    </nav>
                    <div class="px-4 pb-3">
                        <div class="relative flex items-center bg-slate-950/40 border border-slate-700/50 rounded-lg focus-within:border-blue-500">
                            <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3"></i>
                            <input type="text" id="search-input" placeholder="Search track, artist or album..." class="w-full bg-transparent pl-10 pr-4 py-2.5 text-sm outline-none">
                        </div>
                    </div>
                    <div class="flex border-t border-slate-800/60 text-sm font-medium">
                        <button onclick="switchTab('songs')" id="tab-songs" class="flex-1 py-3 text-center border-b-2 border-transparent">Songs</button>
                        <button onclick="switchTab('albums')" id="tab-albums" class="flex-1 py-3 text-center border-b-2 border-transparent">Albums</button>
                        <button onclick="switchTab('artists')" id="tab-artists" class="flex-1 py-3 text-center border-b-2 border-transparent">Artists</button>
                    </div>
                </div>

                <main class="max-w-xl mx-auto px-4 pt-6">
                    <div class="flex justify-between items-center border-b border-slate-700/30 pb-2 mb-4 bg-slate-900/20 p-2 rounded-t backdrop-blur-sm">
                        <h2 id="content-header-title" class="text-xs font-semibold uppercase tracking-wider text-slate-200 flex items-center gap-2"></h2>
                        <span id="total-tracks" class="text-xs font-mono text-slate-200 bg-slate-950/60 px-2 py-0.5 rounded">0 Items</span>
                    </div>
                    <div id="dynamic-view-container" class="space-y-2"></div>
                </main>

                <div class="fixed bottom-0 left-0 right-0 bg-slate-950/95 border-t border-slate-800/80 px-4 pt-4 pb-6 backdrop-blur-lg z-50">
                    <div class="max-w-xl mx-auto">
                        <div class="flex items-center gap-3 mb-3">
                            <div id="player-cover-container" class="w-12 h-12 aspect-square bg-slate-900 border border-slate-700/60 rounded-md flex items-center justify-center overflow-hidden flex-shrink-0">
                                <i data-lucide="disc" id="disc-icon" class="w-6 h-6 text-slate-400"></i>
                            </div>
                            <div class="flex-1 min-w-0">
                                <span id="player-title" class="text-sm font-semibold text-white truncate block">No Track Selected</span>
                                <span id="player-artist" class="text-xs text-slate-300 truncate block mt-0.5">iOS Media Engine</span>
                            </div>
                        </div>

                        <div class="flex items-center gap-3 mb-3">
                            <span id="time-current" class="text-[11px] font-mono text-slate-300 w-10 text-right">00:00</span>
                            <div class="flex-1 flex items-center"><input type="range" id="seek-slider" min="0" max="100" value="0" class="seek-slider w-full"></div>
                            <span id="time-total" class="text-[11px] font-mono text-slate-300 w-10">00:00</span>
                        </div>

                        <div class="flex items-center justify-between px-4 max-w-sm mx-auto">
                            <button id="btn-shuffle" class="p-2 text-slate-400 hover:text-slate-200 transition-colors">
                                <i data-lucide="shuffle" class="w-5 h-5"></i>
                            </button>
                            
                            <button id="btn-prev" class="p-2 text-slate-200"><i data-lucide="skip-back" class="w-6 h-6 fill-slate-200"></i></button>
                            
                            <button id="btn-play" class="w-14 h-14 bg-blue-500 text-white rounded-full flex items-center justify-center hover:bg-blue-600 shadow-md transform active:scale-95 transition-all">
                                <i data-lucide="play" class="w-6 h-6 fill-white ml-0.5" id="play-icon"></i>
                            </button>
                            
                            <button id="btn-next" class="p-2 text-slate-200"><i data-lucide="skip-forward" class="w-6 h-6 fill-slate-200"></i></button>
                            
                            <button id="btn-repeat" class="p-2 text-slate-400 hover:text-slate-200 transition-colors relative">
                                <i data-lucide="repeat" class="w-5 h-5" id="repeat-icon"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <audio id="audio-engine" crossorigin="anonymous"></audio>

                <script>
                    const songs = {json_data_string};
                    let originalSongsOrder = [...songs];
                    let currentTrackIndex = -1;
                    let isPlaying = false;
                    let activeTab = "songs";
                    
                    let repeatMode = 'normal'; 
                    let isShuffle = false;

                    const audioEngine = document.getElementById('audio-engine');
                    const viewContainer = document.getElementById('dynamic-view-container');
                    const searchInput = document.getElementById('search-input');
                    const totalTracksText = document.getElementById('total-tracks');
                    const contentHeaderTitle = document.getElementById('content-header-title');
                    
                    const playerTitle = document.getElementById('player-title');
                    const playerArtist = document.getElementById('player-artist');
                    const playerCoverContainer = document.getElementById('player-cover-container');
                    const playIcon = document.getElementById('play-icon');
                    const seekSlider = document.getElementById('seek-slider');
                    const timeCurrent = document.getElementById('time-current');
                    const timeTotal = document.getElementById('time-total');
                    
                    const btnShuffle = document.getElementById('btn-shuffle');
                    const btnRepeat = document.getElementById('btn-repeat');
                    const repeatIcon = document.getElementById('repeat-icon');

                    function initApp() {{
                        switchTab('songs');
                        setupEventListeners();
                        lucide.createIcons();
                    }}

                    function switchTab(tabName) {{
                        activeTab = tabName;
                        searchInput.value = "";
                        ['songs', 'albums', 'artists'].forEach(t => {{
                            document.getElementById('tab-' + t).classList.remove('tab-active');
                        }});
                        document.getElementById('tab-' + tabName).classList.add('tab-active');
                        renderCoreEngine();
                    }}

                    function renderCoreEngine() {{
                        viewContainer.innerHTML = '';
                        const query = searchInput.value.toLowerCase().trim();
                        let filtered = songs.filter(s => s.title.toLowerCase().includes(query) || s.artist.toLowerCase().includes(query) || s.album.toLowerCase().includes(query));

                        if(activeTab === 'songs') {{
                            contentHeaderTitle.innerHTML = '<i data-lucide="music-4" class="w-4 h-4"></i> Audio Tracks';
                            totalTracksText.innerText = filtered.length + " Tracks";

                            filtered.forEach((song) => {{
                                const originalIndex = songs.findIndex(s => s.file === song.file);
                                const isCurrentActive = (originalIndex === currentTrackIndex);
                                const rowIcon = (isCurrentActive && isPlaying) ? 'pause' : 'play';
                                const activeBg = isCurrentActive ? 'border-blue-500 bg-blue-950/30' : 'bg-slate-900/40 border-slate-700/30';

                                const div = document.createElement('div');
                                div.className = `flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-all ${{activeBg}}`;
                                div.innerHTML = `
                                    <div class="flex items-center gap-3 min-w-0 flex-1" onclick="handleRowClick(${{originalIndex}})">
                                        <div class="w-10 h-10 flex-shrink-0 rounded bg-slate-950/60 border border-slate-700/40 flex items-center justify-center">
                                            <i data-lucide="music" class="${{isCurrentActive ? 'text-blue-400' : 'text-slate-500'}} w-5 h-5"></i>
                                        </div>
                                        <div class="min-w-0 flex-1">
                                            <span class="font-semibold text-sm ${{isCurrentActive ? 'text-blue-400' : 'text-slate-100'}} block truncate">${{song.title}}</span>
                                            <span class="text-xs text-slate-400 block truncate mt-0.5">${{song.artist}}</span>
                                        </div>
                                        <div class="${{isCurrentActive ? 'text-blue-400' : 'text-slate-400'}} pl-2">
                                            <i data-lucide="${{rowIcon}}" class="w-5 h-5"></i>
                                        </div>
                                    </div>
                                `;
                                viewContainer.appendChild(div);
                            }});
                        }} 
                        else if(activeTab === 'albums' || activeTab === 'artists') {{
                            let groups = {{}};
                            filtered.forEach(s => {{
                                let key = (activeTab === 'albums') ? s.album : s.artist;
                                if(!groups[key]) groups[key] = [];
                                groups[key].push(s);
                            }});

                            contentHeaderTitle.innerHTML = activeTab === 'albums' ? '<i data-lucide="disc" class="w-4 h-4"></i> Albums' : '<i data-lucide="user" class="w-4 h-4"></i> Artists';
                            totalTracksText.innerText = Object.keys(groups).length + (activeTab === 'albums' ? " Albums" : " Artists");

                            Object.keys(groups).forEach((groupName) => {{
                                const firstSongInGroup = groups[groupName][0];
                                const firstSongIndex = songs.findIndex(s => s.file === firstSongInGroup.file);

                                const div = document.createElement('div');
                                div.className = "flex items-center gap-3 p-3 bg-slate-900/40 border border-slate-700/30 rounded-lg hover:border-slate-500 cursor-pointer transition-all";
                                div.onclick = () => {{ loadAndPlay(firstSongIndex); }};
                                div.innerHTML = `
                                    <div class="w-12 h-12 flex-shrink-0 rounded bg-slate-950/60 border border-slate-700/40 flex items-center justify-center">
                                        <i data-lucide="${{activeTab === 'albums' ? 'disc' : 'user'}}" class="w-5 h-5 text-slate-500"></i>
                                    </div>
                                    <div class="min-w-0 flex-1">
                                        <span class="text-sm font-semibold text-slate-100 block truncate">${{groupName}}</span>
                                        <span class="text-xs text-slate-400 block mt-0.5">${{groups[groupName].length}} Tracks</span>
                                    </div>
                                `;
                                viewContainer.appendChild(div);
                            }});
                        }}
                        lucide.createIcons();
                    }}

                    function handleRowClick(index) {{
                        if (currentTrackIndex === index) {{
                            isPlaying ? pauseAudio() : playAudio();
                        }} else {{
                            loadAndPlay(index);
                        }}
                    }}

                    function loadAndPlay(index) {{
                        if (index < 0 || index >= songs.length) return;
                        currentTrackIndex = index;
                        const track = songs[index];
                        
                        audioEngine.src = encodeURIComponent(track.file);
                        playerTitle.innerText = track.title;
                        playerArtist.innerText = track.artist + " — " + track.album;
                        playAudio();

                        playerCoverContainer.innerHTML = `
                            <img src="/get_embedded_cover?file=${{encodeURIComponent(track.file)}}" 
                                 class="w-full h-full aspect-square object-cover" 
                                 onerror="this.parentElement.innerHTML='<i data-lucide=\\'disc\\' class=\\'w-6 h-6 text-slate-400\\'></i>'; lucide.createIcons();">
                        `;
                        
                        renderCoreEngine();
                    }}

                    function playAudio() {{
                        audioEngine.play().then(() => {{
                            isPlaying = true;
                            playIcon.setAttribute('data-lucide', 'pause');
                            lucide.createIcons();
                            renderCoreEngine();
                        }}).catch(err => console.log("Playback error:", err));
                    }}

                    function pauseAudio() {{
                        audioEngine.pause();
                        isPlaying = false;
                        playIcon.setAttribute('data-lucide', 'play');
                        lucide.createIcons();
                        renderCoreEngine();
                    }}

                    function nextTrack() {{
                        /* FIX: Jika repeat-once aktif, fungsi ini tidak perlu ubah src, 
                           ia dikawal secara native oleh attribute loop */
                        if (repeatMode === 'repeat-once') {{
                            audioEngine.currentTime = 0;
                            playAudio();
                            return;
                        }}
                        
                        if (currentTrackIndex < songs.length - 1) {{
                            loadAndPlay(currentTrackIndex + 1);
                        }} else if (repeatMode === 'repeat-all') {{
                            loadAndPlay(0);
                        }} else {{
                            pauseAudio();
                        }}
                    }}

                    function prevTrack() {{
                        if (currentTrackIndex > 0) {{
                            loadAndPlay(currentTrackIndex - 1);
                        }} else if (repeatMode === 'repeat-all') {{
                            loadAndPlay(songs.length - 1);
                        }}
                    }}

                    function shuffleArray(array) {{
                        for (let i = array.length - 1; i > 0; i--) {{
                            const j = Math.floor(Math.random() * (i + 1));
                            [array[i], array[array[j]]] = [array[j], array[i]];
                        }}
                    }}

                    function setupEventListeners() {{
                        document.getElementById('btn-play').addEventListener('click', () => {{
                            if(currentTrackIndex !== -1) {{ isPlaying ? pauseAudio() : playAudio(); }}
                            else if(songs.length > 0) {{ loadAndPlay(0); }}
                        }});
                        
                        document.getElementById('btn-next').addEventListener('click', nextTrack);
                        document.getElementById('btn-prev').addEventListener('click', prevTrack);
                        
                        audioEngine.addEventListener('ended', nextTrack);

                        btnShuffle.addEventListener('click', () => {{
                            isShuffle = !isShuffle;
                            if (isShuffle) {{
                                btnShuffle.classList.add('btn-active');
                                const currentTrack = songs[currentTrackIndex];
                                shuffleArray(songs);
                                if (currentTrack) {{
                                    currentTrackIndex = songs.findIndex(s => s.file === currentTrack.file);
                                }}
                            }} else {{
                                btnShuffle.classList.remove('btn-active');
                                const currentTrack = songs[currentTrackIndex];
                                songs.length = 0;
                                songs.push(...originalSongsOrder);
                                if (currentTrack) {{
                                    currentTrackIndex = songs.findIndex(s => s.file === currentTrack.file);
                                }}
                            }}
                            renderCoreEngine();
                        }});

                        btnRepeat.addEventListener('click', () => {{
                            if (repeatMode === 'normal') {{
                                repeatMode = 'repeat-all';
                                audioEngine.loop = false; /* Pastikan native loop off */
                                btnRepeat.classList.add('btn-active');
                                repeatIcon.setAttribute('data-lucide', 'repeat');
                            }} else if (repeatMode === 'repeat-all') {{
                                repeatMode = 'repeat-once';
                                audioEngine.loop = true; /* FIX: Guna native loop supaya pelayar web tidak sekat auto-replay */
                                btnRepeat.classList.add('btn-active');
                                repeatIcon.setAttribute('data-lucide', 'repeat-1');
                            }} else {{
                                repeatMode = 'normal';
                                audioEngine.loop = false;
                                btnRepeat.classList.remove('btn-active');
                                repeatIcon.setAttribute('data-lucide', 'repeat');
                            }}
                            lucide.createIcons();
                        }});

                        audioEngine.addEventListener('timeupdate', () => {{
                            if (audioEngine.duration) {{
                                const pct = (audioEngine.currentTime / audioEngine.duration) * 100;
                                seekSlider.value = pct;
                                timeCurrent.innerText = formatTime(audioEngine.currentTime);
                                timeTotal.innerText = formatTime(audioEngine.duration);
                            }}
                        }});

                        seekSlider.addEventListener('input', () => {{
                            if(audioEngine.duration) {{
                                audioEngine.currentTime = (seekSlider.value / 100) * audioEngine.duration;
                            }}
                        }});

                        searchInput.addEventListener('input', renderCoreEngine);
                    }}

                    function formatTime(secs) {{
                        const m = Math.floor(secs / 60).toString().padStart(2, '0');
                        const s = Math.floor(secs % 60).toString().padStart(2, '0');
                        return `${{m}}:${{s}}`;
                    }}

                    window.onload = initApp;
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            return

        return SimpleHTTPRequestHandler.do_GET(self)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == '__main__':
    with ThreadedHTTPServer(("", PORT), CleanMusicServer) as httpd:
        print(f"Runon {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nBye Faez")
