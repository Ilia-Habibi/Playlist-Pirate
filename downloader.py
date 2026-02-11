from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import os
import requests
import yt_dlp

class Downloader:
    def __init__(self, download_folder="downloads"):
        self.download_folder = download_folder
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

    def download_audio(self, yt_id, filename):
        """
        Download audio file from YouTube using yt-dlp.
        The output format will be mp3.
        """
        # Set the output file path (without extension, yt-dlp will add it)
        out_template = os.path.join(self.download_folder, filename)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{out_template}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={yt_id}'])
            
            # The final file is mp3
            return f"{out_template}.mp3"
        except Exception as e:
            print(f"Error downloading {yt_id}: {e}")
            return None

    def add_metadata(self, filepath, title, artist, album, cover_url):
        """
        Add cover and ID3 tags to the MP3 file.
        """
        try:
            # 1. Add simple text tags (title, artist, album)
            try:
                audio = EasyID3(filepath)
            except:
                audio = EasyID3()
                audio.save(filepath)
            
            audio['title'] = title
            audio['artist'] = artist
            audio['album'] = album
            audio.save()

            # 2. Download and add cover image
            if cover_url:
                response = requests.get(cover_url)
                if response.status_code == 200:
                    # Determine the MIME type of the image from the response headers
                    mime_type = response.headers.get('Content-Type', 'image/jpeg') 
                    
                    audio = ID3(filepath)
                    audio.add(APIC(
                        encoding=3, # 3 is for utf-8
                        mime=mime_type, 
                        type=3, # 3 is for the cover image
                        desc=u'Cover',
                        data=response.content
                    ))
                    audio.save()
            
            print(f"Metadata added to {filepath}")
            return True

        except Exception as e:
            print(f"Error tagging {filepath}: {e}")
            return False
