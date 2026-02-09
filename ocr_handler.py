import pytesseract
from PIL import Image
import os

class OCRHandler:
    def __init__(self, tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        """
        This class is responsible for interacting with the Tesseract engine.
        """
        # Set the path to the Tesseract executable
        # If the user has installed it in a different location, they can change it
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            print(f"Warning: Tesseract functionality might fail. File not found at: {tesseract_path}")
            print("Please ensure Tesseract-OCR is installed and the path is correct.")

    def extract_text(self, image_path):
        """
        Takes an image and returns all the text within it.
        """
        try:
            # 1. Open the image using the Pillow library
            img = Image.open(image_path)
            
            # 2. Convert the image to a text string using pytesseract
            # lang='eng' specifies the English language.
            # config='--psm 6' assumes the text is a single uniform block (good for lists)
            text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')
            
            return text
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return ""

    def process_text_to_lines(self, raw_text):
        """
        Takes raw text and cleans it line by line.
        Returns a list of non-empty lines.
        """
        lines = []
        # Split the text into lines
        raw_lines = raw_text.split('\n')
        
        for line in raw_lines:
            clean_line = line.strip()
            # Keep only lines that have at least 3 characters (to remove noise)
            if len(clean_line) > 3:
                lines.append(clean_line)
        
        return lines
