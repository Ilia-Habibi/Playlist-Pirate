# PlaylistPirate 🏴‍☠️🎧

**PlaylistPirate** is an automated tool designed to digitize and migrate music libraries using Optical Character Recognition (OCR). It scans screenshots of song lists (e.g., from old music players or streaming apps), extracts the track information, finds the best match on YouTube Music, and attempts to download the high-quality audio with full metadata tagging.

This project demonstrates a full pipeline of:
1.  **Computer Vision**: Pre-processing images for optimal text extraction (handling dark mode/low contrast).
2.  **Database Management**: Preventing duplicates and tracking processed files using SQLite.
3.  **API Integration**: interfacing with YouTube Music to find official audio or high-quality video matches.
4.  **Automation**: Managing the download, conversion, and metadata tagging workflow.

---

## 🚀 Key Features

*   **Smart OCR Engine**: Uses `Tesseract` and `OpenCV` with **Adaptive Thresholding** to accurately read text from both light and dark mode screenshots.
*   **Intelligent Deduplication**:
    *   Prevents re-scanning the same image twice.
    *   Checks the database for existing tracks to avoid duplicates.
    *   Automatically removes inferior duplicate entries found via the API.
*   **Music Discovery**: levereges `ytmusicapi` to find the exact song, artist, and album metadata.
*   **Metadata Tagging**: Automatically embeds Cover Art, Artist, Album, and Title into the downloaded MP3 files using `mutagen`.

---

## 🛠 Tech Stack

*   **Language**: Python 3.10+
*   **Computer Vision**: `opencv-python`, `pytesseract`
*   **APIs**: `ytmusicapi` (YouTube Music)
*   **Data Storage**: `sqlite3`
*   **Network & Download**: `yt-dlp`, `requests`, `ffmpeg` (via subprocess)
*   **File Handling**: `mutagen` (ID3 Tags)

---

## ⚙️ Installation & Setup

### Prerequisites

1.  **Python 3.10+** installed.
2.  **Tesseract-OCR**:
    *   Download and install [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki).
    *   Ensure the path in `ocr_handler.py` matches your installation (Default: `C:\Program Files\Tesseract-OCR\tesseract.exe`).
3.  **FFmpeg**:
    *   Download and install [FFmpeg](https://ffmpeg.org/download.html).
    *   Add FFmpeg to your system's PATH environment variable.

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Ilia-Habibi/Playlist-Pirate.git
    cd PlaylistPirate
    ```

2.  Install python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## 📖 Usage

1.  **Prepare Images**: Place your screenshots (PNG, JPG) inside the `input_images/` folder.
2.  **Run the Script**:
    ```bash
    python main.py
    ```
3.  **Process Flow**:
    *   The script scans `input_images/` for new files.
    *   It extracts text and saves potential tracks to the database (`pending` status).
    *   It searches YouTube Music for pending tracks.
    *   If a match is found, it attempts to download the audio and apply tags.
    *   Downloaded files are saved in the `downloads/` folder.

---

## ⚠️ Known Limitations

*   **YouTube Anti-Bot Measures**: The download functionality relies on `yt-dlp` and YouTube's public endpoints. Due to frequent changes in YouTube's anti-bot detection and throttling, the download feature may occasionally fail or require updated cookies/headers.
    *   *Workaround*: The project is set up to focus on the **Metadata Gathering** and **Database curation** aspects, which remain stable.
*   **OCR Accuracy**: While optimized for dark mode, extremely low-resolution or blurry screenshots may still yield errors.

---

## 📂 Project Structure

```
PlaylistPirate/
├── main.py              # Entry point: Orchestrates OCR, Search, and Download
├── database.py          # SQLite handler for tracks and image logs
├── ocr_handler.py       # Image pre-processing and Text Extraction
├── music_api.py         # YouTube Music API wrapper
├── downloader.py        # Handles audio download and tagging
├── requirements.txt     # Python dependencies
└── input_images/        # Drop screenshots here
```

---

## 📝 License

This project is for educational purposes only. Please respect copyright laws and YouTube's Terms of Service.
