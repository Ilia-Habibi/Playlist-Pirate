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
        # album: Album name (to be filled later)
        # yt_id: YouTube ID for the track (to be filled later)
        # cover_url: URL of the cover image (to be filled later)
        # duration: Duration of the track (to be filled later)
        # status: Track status (e.g., pending, cleaned, downloaded)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_text TEXT UNIQUE,
                song_name TEXT,
                artist_name TEXT,
                album TEXT,
                yt_id TEXT,
                cover_url TEXT,
                duration TEXT,
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
            print(f"Added raw track: {raw_text}")
            return True
        except sqlite3.IntegrityError:
            # print(f"Duplicate skipped: {raw_text}") # Too noisy
            return False

    def get_pending_tracks(self):
        """
        List of tracks that have not been searched yet (status pending).
        """
        self.cursor.execute("SELECT id, raw_text FROM tracks WHERE status = 'pending'")
        return self.cursor.fetchall()

    def update_track_info(self, track_id, info):
        """
        Updates track information after finding it in the API.
        Also checks for duplicate tracks (duplicate yt_id).
        If a duplicate is found, this row is deleted.
        """
        yt_id = info['yt_id']

        # 1. Check for duplicate yt_id in other rows
        # We are looking for a row that has the same yt_id but a different id than the current track_id
        self.cursor.execute("SELECT id FROM tracks WHERE yt_id = ? AND id != ?", (yt_id, track_id))
        duplicate = self.cursor.fetchone()

        if duplicate:
            # If a duplicate is found, it means we have already found this song with another OCR.
            # So we delete this new version (weaker or duplicate).
            print(f"Duplicate song found for ID {track_id} (matches existing ID {duplicate[0]}). Deleting duplicate entry.")
            self.cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
            self.conn.commit()
            return False # Indicates that the update was not performed (deleted)
        
        # 2. If not a duplicate, update
        self.cursor.execute("""
            UPDATE tracks 
            SET song_name = ?, 
                artist_name = ?, 
                album = ?, 
                yt_id = ?, 
                cover_url = ?, 
                duration = ?, 
                status = 'found'
            WHERE id = ?
        """, (
            info['title'], 
            info['artist'], 
            info['album'], 
            yt_id, 
            info['cover_url'], 
            info['duration'], 
            track_id
        ))
        self.conn.commit()
        print(f"Updated track {track_id}: {info['title']} - {yt_id}")
        return True

    def mark_track_not_found(self, track_id):
        """
        If not found in the API, change the status so it won't be searched again.
        """
        self.cursor.execute("UPDATE tracks SET status = 'not_found' WHERE id = ?", (track_id,))
        self.conn.commit()

    def is_image_processed(self, filename):
        """
        Checks if this image has been processed before.
        """
        self.cursor.execute("SELECT id FROM images_log WHERE filename = ?", (filename,))
        return self.cursor.fetchone() is not None

    def close(self):
        self.conn.close()
