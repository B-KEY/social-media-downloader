import yt_dlp
import os
from urllib.parse import urlparse
import random

class MediaDownloader:
    def __init__(self):
        self.download_dir = 'downloads'
        os.makedirs(self.download_dir, exist_ok=True)
        
        # List of user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.0.0 Mobile/15E148 Safari/604.1'
        ]

    def get_random_user_agent(self):
        return random.choice(self.user_agents)

    def process_download(self, download_info):
        try:
            url = download_info['url']
            quality = download_info.get('quality', 'best')
            platform = self.get_platform(url)

            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'noplaylist': True,
                'nocheckcertificate': True,
                'prefer_insecure': True,
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                'socket_timeout': 30,
                'http_headers': {
                    'User-Agent': self.get_random_user_agent(),
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'player_skip': ['js', 'configs', 'webpage']
                    }
                }
            }

            # Add proxy if available
            proxy = os.getenv('HTTP_PROXY')
            if proxy:
                ydl_opts['proxy'] = proxy

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    print(f"Attempting download with first configuration: {url}")
                    meta = ydl.extract_info(url, download=False)
                    if not meta:
                        raise Exception("Could not extract video information")

                    # Get available formats
                    formats = meta.get('formats', [])
                    if not formats:
                        raise Exception("No formats available")

                    # Select format
                    selected_format = None
                    for f in formats:
                        if f.get('ext') == 'mp4' and f.get('format_note') != 'tiny':
                            selected_format = f['format_id']
                            break

                    if selected_format:
                        ydl_opts['format'] = selected_format

                    # Actual download
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
                                'player_client': ['web'],
                                'player_skip': []
                            }
                        },
                        'http_headers': {
                            'User-Agent': self.get_random_user_agent(),
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
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
                'error': f"Could not download from {platform}: {str(e)}",
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
