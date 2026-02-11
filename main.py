from database import DatabaseHandler
from music_api import MusicFinder
from ocr_handler import OCRHandler
import os
import time

def main():
    # 1. Define paths
    images_dir = "input_images" 
    
    # 2. Initialize classes
    db = DatabaseHandler()
    ocr = OCRHandler() # Assumes Tesseract is installed in the default location or the path is correctly set
    finder = MusicFinder() # Initialize the music finder

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
            db.add_image_log(image_file, raw_text_full)
            
            print(f"Found {len(grouped_lines)} potential tracks.")

            for line in grouped_lines:
                clean_line = line.strip()
                # Only add to the database if the cleaned line has more than 3 characters (to avoid very short or empty entries)
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

    db.close()
    print("\nAll tasks complete.")

if __name__ == "__main__":
    main()
