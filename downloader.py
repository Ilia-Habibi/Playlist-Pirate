"""
Audio Downloader & Metadata Tagging Module.

Handles the retrieval of audio streams and file post-processing.
- Uses yt-dlp to extract stream URLs.
- Uses FFmpeg for robust audio conversion (stream -> mp3).
- Applies ID3 tags and Album Art using Mutagen.

Note: Includes error handling for common stream extraction failures.
"""

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import os
import requests
import subprocess
import yt_dlp

class Downloader:
    def __init__(self, download_folder="downloads"):
        self.download_folder = download_folder
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

    def get_file_info(self, yt_id):
        """
        Get file information (such as size) before downloading.
        Returns the size of the BEST AUDIO format available.
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'https://www.youtube.com/watch?v={yt_id}', download=False)
                
                # Check if 'formats' are available
                if 'formats' in info:
                    # Filter for audio-only formats (vcodec='none')
                    audio_formats = [f for f in info['formats'] if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
                    
                    if audio_formats:
                        # audio_formats are usually sorted by quality ascending in yt-dlp
                        # The last one is the 'best' audio
                        best_audio = audio_formats[-1]
                        return best_audio.get('filesize') or best_audio.get('filesize_approx') or 0
                
                # Fallback if formats not found (rare)
                return info.get('filesize') or info.get('filesize_approx') or 0
        except Exception:
            return 0

    def download_audio(self, yt_id, filename):
        """
        Download audio using the robust method: yt-dlp to get stream URL -> ffmpeg to download and convert.
        output: mp3
        """
        # Final output path
        final_mp3_path = os.path.join(self.download_folder, f"{filename}.mp3")
        video_url = f"https://www.youtube.com/watch?v={yt_id}"

        print(f"Resolving stream URL for {yt_id}...")

        # 1. Get direct stream URL using yt-dlp
        # cmd: yt-dlp -f bestaudio -g URL
        # We use strict arguments to ensure we get a URL
        cmd_get_url = ["yt-dlp", "-f", "bestaudio/best", "-g", video_url]

        try:
            # Run yt-dlp to get the URL
            # encoding='utf-8' handles any potential character issues
            process = subprocess.run(cmd_get_url, capture_output=True, text=True, check=True, encoding='utf-8')
            stream_url = process.stdout.strip()
            
            if not stream_url:
                print("Error: Could not retrieve stream URL (empty output).")
                return None

            print("Stream URL found. Starting download with FFmpeg...")

            # 2. Download and convert with ffmpeg
            # cmd: ffmpeg -y -i "URL" -vn -ar 44100 -ac 2 -b:a 192k -f mp3 "output.mp3"
            cmd_ffmpeg = [
                "ffmpeg", 
                "-y", # Overwrite output file
                "-i", stream_url,
                "-vn", # No video
                "-ar", "44100", # Audio sample rate
                "-ac", "2", # Stereo
                "-b:a", "192k", # Bitrate
                "-f", "mp3", # Format
                final_mp3_path
            ]
            
            # Run ffmpeg
            # We don't need capture_output if we want to see ffmpeg progress, but let's capture to keep it clean.
            # If user wants debug, we can print stderr.
            ffmpeg_process = subprocess.run(cmd_ffmpeg, capture_output=True, text=True)
            
            if ffmpeg_process.returncode != 0:
                print(f"FFmpeg Error: {ffmpeg_process.stderr}")
                return None
            
            # Verify result
            if os.path.exists(final_mp3_path) and os.path.getsize(final_mp3_path) > 10240: # > 10KB
                return final_mp3_path
            else:
                print("FFmpeg finished but file is missing or too small.")
                return None

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            if e.stderr:
                print(f"Details: {e.stderr}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
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
