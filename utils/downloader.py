import yt_dlp
import os
from urllib.parse import urlparse
import random

class MediaDownloader:
    def __init__(self):
        self.download_dir = 'downloads'
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
            quality = download_info.get('quality', 'best')
            platform = self.get_platform(url)

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'noplaylist': True,
                'nocheckcertificate': True,
                'prefer_insecure': True,
                'http_headers': {
                    'User-Agent': self.get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android'],
                        'player_skip': ['js', 'configs']
                    }
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    print(f"Attempting download: {url}")
                    # First try to get metadata
                    meta = ydl.extract_info(url, download=False)
                    if not meta:
                        raise Exception("Could not extract video information")

                    # If metadata extraction successful, try download
                    info = ydl.extract_info(url, download=True)
                    
                    return {
                        'status': 'success',
                        'title': info.get('title', 'Unknown Title'),
                        'platform': platform,
                        'url': url
                    }

                except Exception as first_error:
                    print(f"First attempt failed: {str(first_error)}")
                    
                    # Second attempt with different configuration
                    ydl_opts.update({
                        'format': 'best',
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['android'],
                                'player_skip': []
                            }
                        }
                    })

                    print("Attempting second download configuration")
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        raise Exception("Second attempt failed")
                        
                    return {
                        'status': 'success',
                        'title': info.get('title', 'Unknown Title'),
                        'platform': platform,
                        'url': url
                    }

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
