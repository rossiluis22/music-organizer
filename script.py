#!/usr/bin/env python3
import os
import sys
import shutil
from mutagen import File as MutagenFile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

ILLEGAL_CHARS = ['/', '?', '\\', ':', '*', '"', '<', '>', '|']
VALID_EXTENSIONS = ["mp3", "m4a", "wma"]

def sanitize(text):
    for char in ILLEGAL_CHARS:
        text = text.replace(char, '')
    return text.strip()

def process_songs(input_dir, output_dir):
    errors = []

    def remove_empty_dirs(path, stop_at):
        while True:
            if path == stop_at:
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
        self.last_run = 0
        self.interval = 120  # segundos

    def on_any_event(self, event):
        now = time.time()
        if now - self.last_run >= self.interval:
            print("\nChange detected, processing...")
            process_songs(self.input_dir, self.output_dir)
            self.last_run = now

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
    for input_dir, output_dir in pairs:
        # Procesa los ficheros existentes antes de empezar el watcher
        process_songs(input_dir, output_dir)

        event_handler = WatcherHandler(input_dir, output_dir)
        observer = Observer()
        observer.schedule(event_handler, path=input_dir, recursive=True)
        observer.start()
        observers.append(observer)
        print(f"Monitoring folder: {input_dir} ...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()

