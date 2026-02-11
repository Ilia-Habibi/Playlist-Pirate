from ytmusicapi import YTMusic

class MusicFinder:
    def __init__(self):
        # Create an instance of the YTMusic class
        # No login is required for general search
        self.yt = YTMusic()

    def find_best_match(self, query):
        """
        Search YouTube Music and find the best match.
        It checks both official songs and videos
        to also find remixes and unofficial covers.
        """
        try:
            # General search (no filters to get everything)
            results = self.yt.search(query)
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            return None

        if not results:
            return None

        # Return the first result that is a song or video
        for item in results:
            if item['resultType'] in ['song', 'video']:
                
                # Extract artist information
                artists = []
                if 'artists' in item:
                    artists = [a['name'] for a in item['artists']]
                artist_text = ", ".join(artists)

                # Extract album name (videos usually don't have an album)
                album = "Single"
                if 'album' in item and item['album']:
                    album = item['album']['name']

                # Extract the best quality cover image
                cover = ""
                if 'thumbnails' in item:
                    # The last item is usually the highest quality
                    cover = item['thumbnails'][-1]['url']

                return {
                    'yt_id': item['videoId'],
                    'title': item['title'],
                    'artist': artist_text,
                    'album': album,
                    'cover_url': cover,
                    'duration': item.get('duration', ''),
                    'type': item['resultType'] # To know if it's official or a video
                }
        
        return None

# Test section
if __name__ == "__main__":
    finder = MusicFinder()
    
    # Test with a query that likely has a remix
    print("Testing search...")
    test_query = "man delam nemikhast shayea" # Test example
    result = finder.find_best_match(test_query)
    
    if result:
        print("Found:")
        print(f"Title: {result['title']}")
        print(f"Artist: {result['artist']}")
        print(f"Type: {result['type'].upper()}") # Song or Video
        print(f"ID: {result['yt_id']}")
    else:
        print("Nothing found.")