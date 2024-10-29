import yt_dlp
import os
from urllib.parse import urlparse
import random

class MediaDownloader:
    def __init__(self):
        self.download_dir = '/tmp/downloads'
        os.makedirs(self.download_dir, exist_ok=True)
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]

    def get_random_user_agent(self):
        return random.choice(self.user_agents)

    def process_download(self, download_info):
        try:
            url = download_info['url']
            platform = self.get_platform(url)

            # Basic options that work on Render
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Simplified format
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'extract_flat': True,  # Don't download, just get info
                'skip_download': True,  # Skip actual download on Render
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Just get video info
                    info = ydl.extract_info(url, download=False)
                    
                    if not info:
                        raise Exception("Could not extract video information")

                    # Return video info without downloading
                    formats = info.get('formats', [])
                    best_format = None
                    
                    # Find best MP4 format
                    for f in formats:
                        if f.get('ext') == 'mp4':
                            if not best_format or f.get('height', 0) > best_format.get('height', 0):
                                best_format = f

                    return {
                        'status': 'success',
                        'title': info.get('title', 'Unknown Title'),
                        'platform': platform,
                        'url': url,
                        'download_url': best_format.get('url') if best_format else None,
                        'thumbnail': info.get('thumbnail'),
                        'duration': info.get('duration'),
                        'description': info.get('description')
                    }

                except Exception as e:
                    print(f"Error: {str(e)}")
                    raise

        except Exception as e:
            print(f"Download error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'platform': platform,
                'url': url
            }

    def get_platform(self, url):
        domain = urlparse(url).netloc.lower()
        if 'youtube' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'instagram' in domain:
            return 'instagram'
        elif 'facebook' in domain:
            return 'facebook'
        elif 'tiktok' in domain:
            return 'tiktok'
        return 'unknown'
