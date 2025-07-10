# music-organizer

## Overview

**music-organizer** is a Python utility that automatically organizes music files by reading their metadata and moving them into folders by artist and album. It watches a specified input directory for changes and processes files as they are added or modified.

- Supported formats: MP3, M4A, WMA
- Invalid or corrupted files are moved to dedicated "Invalid Files" or "Corrupt Files" folders.
- Filenames are sanitized and optionally prefixed with track numbers.
- Automatically removes empty directories after organizing.

## Usage

### Requirements

- Python 3.11+
- The following Python packages (see `requirements.txt`):
  - `mutagen`
  - `watchdog`
- (Optional) Docker

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
  3. Sanitizes the data to avoid illegal filename characters.
  4. Moves the file into the structure: `/output/Artist/Album/Track Title.ext`
  5. Files with missing or unreadable metadata are either skipped or moved to a "Corrupt Files" folder.
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
