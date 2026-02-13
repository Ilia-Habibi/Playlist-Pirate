"""
Main Application Entry Point.

This script coordinates the entire pipeline:
1. Scans the 'input_images' directory for new screenshots.
2. Invokes the OCR module to extract raw text (artist - song).
3. Logs processed images to the database to prevent re-processing.
4. Searches for metadata on YouTube Music using the Music API module.
5. Downloads the highest quality audio available using the Downloader module.
"""

from database import DatabaseHandler
from downloader import Downloader
from music_api import MusicFinder
from ocr_handler import OCRHandler
import os
import time

def main():
    # 1. Define paths
    images_dir = "input_images" 
    
    # 2. Initialize classes
    db = DatabaseHandler()
    ocr = OCRHandler() 
    finder = MusicFinder() 
    downloader = Downloader()

    # --- Part 1: Image Processing (OCR) ---
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Directory '{images_dir}' created. Please put your screenshots inside it.")
        return

    files = os.listdir(images_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    print(f"Found {len(image_files)} images.")

    for image_file in image_files:
        # Check if the image has already been processed
        if db.is_image_processed(image_file):
            print(f"Skipping {image_file} (Already processed).")
            continue

        full_path = os.path.join(images_dir, image_file)
        print(f"\nScanning new image: {image_file}")

        try:
            grouped_lines, raw_text_full = ocr.extract_clean_tracks(full_path)
            
            # Save the full image text to the log table so we don't process it again
            # This is crucial for avoiding duplicate work if the script is restarted
            db.add_image_log(image_file, raw_text_full)
            
            print(f"Found {len(grouped_lines)} potential tracks.")

            for line in grouped_lines:
                clean_line = line.strip()
                # Only add to the database if the cleaned line has more than 3 characters (to avoid very short or empty entries)
                # Short entries are often noise from the OCR process
                if len(clean_line) > 3: 
                    db.add_raw_track(clean_line)
                    
        except Exception as e:
            print(f"Error processing {image_file}: {e}")

    # --- Part 2: Music Search (YouTube Music API) ---
    print("\n--- Starting Music Search ---")
    
    # Get tracks that are still in 'pending' status
    pending_tracks = db.get_pending_tracks()
    
    if not pending_tracks:
        print("No pending tracks to search.")
    else:
        print(f"Found {len(pending_tracks)} pending tracks to search on YouTube Music.")

    for track_id, raw_text in pending_tracks:
        print(f"Searching for: {raw_text} ...")
        
        # Search using the API
        result = finder.find_best_match(raw_text)
        
        if result:
            # Update the database with the result and remove duplicates if any
            saved = db.update_track_info(track_id, result)
            if saved:
                print(f" -> MATCH: {result['title']} by {result['artist']}")
            else:
                print(f" -> DUPLICATE: Removed.")
        else:
            print(" -> NOT FOUND")
            db.mark_track_not_found(track_id)
        
        # Short delay to prevent hitting rate limits
        time.sleep(1)

    # --- Part 3: Download & Tagging ---
    print("\n--- Starting Downloads ---")

    # Get tracks ready for download
    found_tracks = db.get_tracks_to_download()

    if not found_tracks:
        print("No tracks ready for download.")
    else:
        print(f"Found {len(found_tracks)} tracks to download.")

    for track_id, song_name, artist_name, album, yt_id, cover_url in found_tracks:
        print(f"\nProcessing: {song_name} - {artist_name}")

        # 1. Check file size
        file_size = downloader.get_file_info(yt_id)
        size_mb = file_size / (1024 * 1024) if file_size else 0
        
        if size_mb > 30:
            user_input = input(f"Warning: File size is large ({size_mb:.2f} MB). Download? (y/n): ")
            if user_input.lower() != 'y':
                print("Skipped by user.")
                continue

        # 2. Download
        # Filename: Artist - Song.mp3
        # Remove illegal characters from filename
        safe_filename = f"{artist_name} - {song_name}".replace("/", "-").replace("\\", "-").replace(":", "-").replace("?", "").replace("*", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")
        
        file_path = downloader.download_audio(yt_id, safe_filename)

        if file_path:
            print("Download successful. Adding metadata...")
            
            # 3. Add Metadata
            downloader.add_metadata(file_path, song_name, artist_name, album, cover_url)
            
            # 4. Update Database
            db.mark_track_downloaded(track_id)
            print("Done.")
        else:
            print("Download failed.")

    db.close()
    print("\nAll tasks complete.")

if __name__ == "__main__":
    main()
