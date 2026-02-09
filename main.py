import os
from database import DatabaseHandler
from ocr_handler import OCRHandler

def main():
    # 1. Define paths
    # Folder where images are located
    images_dir = "input_images" 
    
    # 2. Initialize classes (Database and OCR)
    db = DatabaseHandler()
    ocr = OCRHandler() # Assumes Tesseract is installed in the default path

    # Check if the images folder exists
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Directory '{images_dir}' created. Please put your screenshots inside it.")
        return

    # 3. Find image files
    # List all files in the folder
    files = os.listdir(images_dir)
    # Filter only image files (with extensions jpg or png)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print("No '.jpg' or '.png' images found in 'input_images'.")
        return

    print(f"Found {len(image_files)} images to process...")

    # 4. Process each image
    for image_file in image_files:
        full_path = os.path.join(images_dir, image_file)
        print(f"\nScanning: {image_file}")

        # a: Extract text and group lines (song + artist) using the new method
        try:
            # Extract grouped lines and the full raw text for logging
            grouped_lines, raw_text_full = ocr.extract_clean_tracks(full_path)
            
            # b: Log the image and its full raw text in the database
            db.add_image_log(image_file, raw_text_full)
            
            print(f"Found {len(grouped_lines)} potential tracks.")

            # c: Save each group (song + artist) in the database
            for line in grouped_lines:
                clean_line = line.strip()
                # Only add to the database if the cleaned line has more than 3 characters (to avoid very short or empty entries)
                if len(clean_line) > 3: 
                    db.add_raw_track(clean_line)
                    
        except Exception as e:
            print(f"Error processing {image_file}: {e}")

    # 5. Close the database
    db.close()
    print("\nProcessing complete.")

if __name__ == "__main__":
    main()
