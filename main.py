import os
from database import DatabaseHandler
from ocr_handler import OCRHandler

#make all comments english

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

        # a: Extract raw text from the image
        raw_text = ocr.extract_text(full_path)
        
        # b: Convert the text to separate lines
        lines = ocr.process_text_to_lines(raw_text)
        
        print(f"Found {len(lines)} lines of text.")

        # c: Save each line to the database
        for line in lines:
            # The add_raw_track function itself checks for duplicates and prints messages
            db.add_raw_track(line)

    # 5. Close the database
    db.close()
    print("\nProcessing complete.")

if __name__ == "__main__":
    main()
