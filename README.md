# music-organizer

## Overview

**music-organizer** is a Python utility that automatically organizes music files by reading their metadata and moving them into folders by artist and album. It watches a specified input directory for changes and processes files as they are added or modified.

### Key Features

- **Automatic Organization**: Sorts music into an `Artist/Album` folder structure.
- **Lyrics Fetching**: Automatically searches for and embeds lyrics into your music files (MP3, M4A) using the Genius API.
- **File Sanitization**: Cleans up filenames and removes illegal characters.
- **Directory Monitoring**: Watches a folder for new files and processes them on the fly.
- **Broad Format Support**: Works with MP3, M4A, and WMA files.
- **Error Handling**: Moves invalid or corrupt files to separate folders for review.

## Usage

### Requirements

- Python 3.11+
- The following Python packages (see `requirements.txt`):
  - `mutagen`
  - `watchdog`
  - `lyricsgenius`
- (Optional) Docker

### Lyrics Fetching (Optional)

To enable the automatic download of lyrics, you need a free API token from Genius.com.

1. **Get an API Token**:
   - Go to [https://genius.com/api-clients](https://genius.com/api-clients) and create a new API client.
   - Generate a "Client Access Token" for your client.

2. **Set the Token**:
   You can set the token in one of two ways:
   - **Environment Variable (Recommended)**: Set an environment variable named `GENIUS_API_TOKEN`.
     ```sh
     export GENIUS_API_TOKEN="YOUR_TOKEN_HERE"
     ```
   - **Directly in the Script**: Open `script.py` and replace `"YOUR_API_TOKEN_HERE"` with your actual token.

If no token is provided, the script will skip the lyrics functionality.

### Installation

#### 1. **Clone the repository:**
```sh
git clone https://github.com/rossiluis22/music-organizer.git
cd music-organizer
```

#### 2. **Install dependencies:**
```sh
pip install -r requirements.txt
```

### Running the Organizer

#### **Command Line (Python Script)**

```sh
python script.py <input_dir> <output_dir>
```

- `<input_dir>`: Path to the folder with your music files.
- `<output_dir>`: Path where organized music will be stored.

The script runs continuously, watching the input directory for new or modified files and organizing them automatically.

#### **Using Docker**

1. Build the Docker image:
   ```sh
   docker build -t music-organizer .
   ```
2. Run the Docker container:
   ```sh
   docker run -v /path/to/input:/input -v /path/to/output:/output music-organizer
   ```

Replace `/path/to/input` and `/path/to/output` with your actual directories.

## How It Works

- When a new file appears in the input directory (or a change is detected), the program:
  1. Checks if the file is a supported music format.
  2. Reads the metadata (title, artist, album, track number).
  3. **(Optional)** If a Genius API token is configured, it searches for and embeds lyrics into the file.
  4. Sanitizes the metadata to avoid illegal filename characters.
  5. Moves the file into the structure: `/output/Artist/Album/Track Title.ext`.
  6. Files with missing or unreadable metadata are either skipped or moved to a "Corrupt Files" folder.
  6. Unsupported formats go to "Invalid Files".
  7. Automatically removes any empty folders left in the input directory after files are moved.

## Example

Suppose `/input` contains:

- `song1.mp3` (artist: Queen, album: Greatest Hits, track: 01)
- `badfile.txt` (not a music file)

After running, output will look like:

```
/output/
└── Queen/
    └── Greatest Hits/
        └── 01 Bohemian Rhapsody.mp3
/output/
└── Invalid Files/
    └── badfile.txt
```

## Troubleshooting

- The script prints processing actions and errors to the console.
- If you see "Missing metadata" or "Could not read metadata," check if your files have ID3 or similar tags.

## License

MIT

## Author

[rossiluis22](https://github.com/rossiluis22)
