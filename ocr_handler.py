import cv2
import numpy as np
import os
import pytesseract

class OCRHandler:
    def __init__(self, tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        """
        Initializes the OCR handler and sets the Tesseract executable path.
        Make sure to update the path if Tesseract is installed in a different location.
        """
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            print(f"Warning: Tesseract functionality might fail. File not found at: {tesseract_path}")
            print("Please ensure Tesseract-OCR is installed and the path is correct.")

    def preprocess_image(self, image_path):
        """
        Preprocesses the image to improve OCR accuracy:
        1. Cropping to remove irrelevant parts (like phone status bar and navigation bar)
        2. Converting to grayscale
        3. Applying thresholding to increase contrast
        """
        # Read the image with OpenCV
        img = cv2.imread(image_path)
        if img is None:
            return None

        h, w, _ = img.shape

        # Crop the image
        # Assuming the relevant content is roughly in the middle of the image, we can crop out the top, bottom, and sides.
        top_crop = int(w * 0.25)
        bottom_crop = int(h - (w * 0.1))
        left_crop = int(w * 0.15)
        right_crop = int(w - (w * 0.15))
        
        # [start_y:end_y, start_x:end_x]
        cropped_img = img[top_crop:bottom_crop, left_crop:right_crop]

        # Convert to grayscale
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

        # Check for dark mode (dark background)
        # If the mean pixel intensity is low, it's likely a dark background with light text.
        # Tesseract works best with dark text on light background, so we invert.
        if np.mean(gray) < 127:
            gray = cv2.bitwise_not(gray)

        # Apply thresholding
        # Using Adaptive Thresholding instead of Otsu because it handles low contrast (gray on black/white) better.
        # It calculates the threshold locally, so even if the text is light gray on white, it can separate it.
        binary = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            31, 15 # blockSize=31 (covers text height), C=15 (aggressive filtering of background)
        )

        return binary

    def extract_text_data(self, image_path):
        """
        Instead of plain text, returns full data (line coordinates).
        This helps us understand which lines are related.
        """
        processed_img = self.preprocess_image(image_path)
        if processed_img is None:
            return []

        # Get detailed OCR data, including line positions and text
        # Includes left, top, width, height, text
        data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT)
        
        return data

    def extract_clean_tracks(self, image_path):
        """
        Extracts text data and tries to group nearby lines together (song name + artist).
        Returns a list of grouped lines and the full raw text for logging.
        """
        data = self.extract_text_data(image_path)
        if not data:
            return [], "" # Empty list and empty text

        n_boxes = len(data['text'])
        grouped_lines = []
        current_group = []
        last_top = 0
        last_height = 0
        
        full_raw_text = "" # For logging

        for i in range(n_boxes):
            # If the text is not empty (ignore spaces)
            text = data['text'][i].strip()
            if not text:
                continue

            full_raw_text += text + " "

            top = data['top'][i]
            height = data['height'][i]
            
            # Grouping logic:
            # If the vertical distance between this word and the previous word is small, they belong to the same group (e.g., continuation of the song name or artist name below it)
            # Reasonable distance: less than 1.5 times the font height
            if last_top == 0 or (top - last_top) < (last_height * 2.5): 
                current_group.append(text)
            else:
                # Too far from the last line, start a new group
                if current_group:
                    grouped_lines.append(" ".join(current_group))
                current_group = [text]

            last_top = top
            last_height = height

        # Add the last group
        if current_group:
            grouped_lines.append(" ".join(current_group))

        return grouped_lines, full_raw_text

    

