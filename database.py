import sqlite3

class DatabaseHandler:
    def __init__(self, db_name="playlist.db"):
        # Connect to the database (if it doesn't exist, it will be created)
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # Create the table if it doesn't exist
        # id: Unique identifier for each row
        # raw_text: Raw text read from the image (must be unique)
        # song_name: Cleaned song name (to be filled later)
        # artist_name: Cleaned artist name (to be filled later)
        # status: Track status (e.g., pending, cleaned, downloaded)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_text TEXT UNIQUE,
                song_name TEXT,
                artist_name TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Create a table to log processed images and their full text
        # filename: Name of the image file (unique)
        # full_text: Full text extracted from the image before processing
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS images_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                full_text TEXT
            )
        """)
        self.conn.commit()

    def add_image_log(self, filename, full_text):
        """
        Logs the image and its full text.
        If the filename already exists, it will skip logging to avoid duplicates.
        """
        try:
            self.cursor.execute("INSERT INTO images_log (filename, full_text) VALUES (?, ?)", (filename, full_text))
            self.conn.commit()
            print(f"Image logged: {filename}")
        except sqlite3.IntegrityError:
            print(f"Image log already exists for: {filename}")

    def add_raw_track(self, raw_text):
        """
        Adds raw text to the database.
        Returns False if it is a duplicate.
        """
        try:
            self.cursor.execute("INSERT INTO tracks (raw_text) VALUES (?)", (raw_text,))
            self.conn.commit()
            print(f"Added: {raw_text}")
            return True
        except sqlite3.IntegrityError:
            print(f"Duplicate skipped: {raw_text}")
            return False

    def close(self):
        self.conn.close()
