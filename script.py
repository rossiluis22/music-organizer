#!/usr/bin/env python3
import os
import sys
import shutil
from mutagen import File as MutagenFile
from mutagen.id3 import USLT
import lyricsgenius
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# --- CONFIGURATION ---
# Obtain a Genius API token by following the instructions at https://genius.com/api-clients
# and paste it here.
GENIUS_API_TOKEN = os.environ.get("GENIUS_API_TOKEN", "YOUR_API_TOKEN_HERE")

ILLEGAL_CHARS = ['/', '?', '\\', ':', '*', '"', '<', '>', '|']
VALID_EXTENSIONS = ["mp3", "m4a", "wma"]

def sanitize(text):
    for char in ILLEGAL_CHARS:
        text = text.replace(char, '')
    return text.strip()

def add_lyrics(song_path, title, artist, genius_instance):
    """
    Searches for lyrics and adds them to the song's metadata.
    """
    try:
        # Check if lyrics already exist
        audio = MutagenFile(song_path, easy=True)
        if 'lyrics' in audio or 'USLT::eng' in audio:
            print(f"Lyrics already exist for: {title}")
            return

        print(f"Searching lyrics for '{title}' by '{artist}'...")
        song = genius_instance.search_song(title, artist)
        if song:
            lyrics = song.lyrics.strip()

            # Remove the first line (e.g., "[Song Name] Lyrics")
            if "Lyrics" in lyrics.split('\n')[0]:
                lyrics = '\n'.join(lyrics.split('\n')[1:]).strip()

            # Add lyrics to the file
            audio = MutagenFile(song_path)
            if song_path.lower().endswith('.mp3'):
                audio["USLT::eng"] = USLT(encoding=3, lang='eng', desc='desc', text=lyrics)
            elif song_path.lower().endswith('.m4a'):
                audio['\xa9lyr'] = lyrics

            audio.save()
            print(f"✅ Lyrics added for: {title}")
        else:
            print(f"❌ Lyrics not found for: {title}")

    except Exception as e:
        print(f"Error adding lyrics to {song_path}: {str(e)}")

def process_songs(input_dir, output_dir):
    errors = []

    if GENIUS_API_TOKEN == "YOUR_API_TOKEN_HERE":
        print("WARNING: Genius API token is not set. Lyrics will not be downloaded.")
        genius = None
    else:
        genius = lyricsgenius.Genius(GENIUS_API_TOKEN, verbose=False, remove_section_headers=True, timeout=15)


    def remove_empty_dirs(path, stop_at):
        protected_folders = {"albums", "playlists", "songs", "youtube-dl", "zips"}

        while True:
            base = os.path.basename(path).lower()
            if path == stop_at or base in protected_folders:
                break
            try:
                os.rmdir(path)
                path = os.path.dirname(path)
            except OSError:
                break

    for root, _, files in os.walk(input_dir):
        for filename in files:
            ext = filename.lower().split('.')[-1]
            if ext not in VALID_EXTENSIONS:
                invalid_folder = os.path.join(output_dir, "Invalid Files")
                os.makedirs(invalid_folder, exist_ok=True)
                try:
                    shutil.move(os.path.join(root, filename), os.path.join(invalid_folder, filename))
                    print(f"Moved invalid file to: {os.path.join(invalid_folder, filename)}")
                except Exception as e:
                    errors.append(f"ERROR moving invalid file {filename}: {str(e)}")
                continue

            song_path = os.path.join(root, filename)
            print(f"Processing: {song_path}")

            try:
                audio = MutagenFile(song_path, easy=True)
                if audio is None:
                    errors.append(f"ERROR: Could not read metadata: {song_path}")
                    continue

                title = audio.get('title', [None])[0]
                artist = audio.get('artist', [None])[0]
                album = audio.get('album', [None])[0]
                track = audio.get('tracknumber', [None])[0]

                if None in (title, artist, album):
                    errors.append(f"ERROR: Missing metadata (title, artist or album) for: {song_path}")
                    continue

                title = sanitize(title).title()
                artist = sanitize(artist).title()
                album = sanitize(album).title()

                # Add lyrics if a genius instance is available
                if genius:
                    add_lyrics(song_path, title, artist, genius)

                track_number = ""
                if track:
                    track_raw = track.split('/')[0].strip()
                    if track_raw.isdigit():
                        track_number = "{:02}".format(int(track_raw))

                if track_number:
                    new_filename = f"{track_number} {title}.{ext}"
                else:
                    new_filename = f"{title}.{ext}"

                dest_folder = os.path.join(output_dir, artist, album)
                os.makedirs(dest_folder, exist_ok=True)

                dest_path = os.path.join(dest_folder, new_filename)

                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(song_path, dest_path)
                print(f"Moved to: {dest_path}")

                remove_empty_dirs(root, input_dir)

            except Exception as e:
                errors.append(f"ERROR processing {song_path}: {str(e)}")
                corrupt_dir = os.path.join(output_dir, "Corrupt Files")
                os.makedirs(corrupt_dir, exist_ok=True)
                dest_path = os.path.join(corrupt_dir, os.path.basename(song_path))
                try:
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    shutil.move(song_path, dest_path)
                    print(f"Moved corrupt file to: {dest_path}")
                except Exception as move_err:
                    print(f"Failed to move corrupt file: {song_path}. Error: {move_err}")

    if errors:
        print("\nSummary of errors:")
        for error in errors:
            print(error)
    else:
        print(f"\n✅ Finished successfully without errors.")

class WatcherHandler(FileSystemEventHandler):
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.last_event_time = None
        self.interval = 120  # segundos

    def on_any_event(self, event):
        self.last_event_time = time.time()

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) not in (2, 4):
        print(f"Usage: {sys.argv[0]} <input1> <output1> [<input2> <output2>]")
        sys.exit(1)

    pairs = []
    for i in range(0, len(args), 2):
        input_dir = args[i]
        output_dir = args[i+1]

        if not os.path.isdir(input_dir):
            print(f"Invalid input directory: {input_dir}")
            sys.exit(1)

        if not os.path.isdir(output_dir):
            print(f"Invalid output directory: {output_dir}")
            sys.exit(1)

        pairs.append((input_dir, output_dir))

    observers = []
    handlers = []
    for input_dir, output_dir in pairs:
        # Procesa los ficheros existentes antes de empezar el watcher
        process_songs(input_dir, output_dir)

        event_handler = WatcherHandler(input_dir, output_dir)
        observer = Observer()
        observer.schedule(event_handler, path=input_dir, recursive=True)
        observer.start()
        observers.append(observer)
        handlers.append(event_handler)
        print(f"Monitoring folder: {input_dir} ...")

    try:
        while True:
            now = time.time()
            for handler in handlers:
                if handler.last_event_time and (now - handler.last_event_time >= handler.interval):
                    print("\nChange detected and 2 minutes elapsed, processing...")
                    process_songs(handler.input_dir, handler.output_dir)
                    handler.last_event_time = None
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()

