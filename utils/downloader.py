import yt_dlp
import os
from urllib.parse import urlparse, unquote

class MediaDownloader:
    def __init__(self):
        self.download_dir = '/tmp/downloads'
        os.makedirs(self.download_dir, exist_ok=True)

    def get_platform(self, url):
        domain = urlparse(url).netloc.lower()
        if 'youtube' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'instagram' in domain or 'instagr.am' in domain:
            return 'instagram'
        elif 'facebook' in domain or 'fb.watch' in domain:
            return 'facebook'
        elif 'tiktok' in domain:
            return 'tiktok'
        return 'unknown'

    def process_download(self, download_info):
        try:
            url = download_info['url']
            platform = self.get_platform(url)

            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'extract_flat': True,
                'skip_download': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'android'],
                    },
                    'instagram': {
                        'compatible_with_web': True,
                    },
                    'facebook': {
                        'compatible_with_web': True,
                    },
                    'tiktok': {
                        'compatible_with_web': True,
                    }
                }
            }

            # Platform specific adjustments
            if platform == 'instagram':
                ydl_opts['format'] = 'best'
            elif platform == 'facebook':
                ydl_opts['format'] = 'best'
            elif platform == 'tiktok':
                ydl_opts['format'] = 'best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception(f"Could not extract {platform} video information")

                # Get the best format URL
                if 'formats' in info:
                    formats = info['formats']
                    # Prefer MP4 format
                    mp4_formats = [f for f in formats if f.get('ext') == 'mp4']
                    if mp4_formats:
                        best_format = max(mp4_formats, key=lambda f: f.get('filesize', 0))
                    else:
                        best_format = formats[-1]  # Last format is usually the best
                    
                    download_url = best_format.get('url')
                else:
                    download_url = info.get('url')

                if not download_url:
                    raise Exception(f"No download URL found for {platform}")

                # Clean the title for filename
                title = info.get('title', 'video')
                title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()

                return {
                    'status': 'success',
                    'title': title,
                    'platform': platform,
                    'download_url': download_url,
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'ext': best_format.get('ext', 'mp4')
                }

        except Exception as e:
            print(f"Download error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'platform': platform,
                'url': url
            }
