import yt_dlp
import os
from urllib.parse import urlparse

class MediaDownloader:
    def __init__(self):
        self.download_dir = 'downloads'
        os.makedirs(self.download_dir, exist_ok=True)

    def get_format(self, url, quality):
        if 'youtube.com' in url or 'youtu.be' in url:
            if quality == 'best':
                return 'best[ext=mp4]/best'
            return f'best[height<={quality[:-1]}][ext=mp4]/best'
        return 'best'

    def clean_url(self, url):
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            if 'watch?v=' in url:
                video_id = url.split('watch?v=')[1].split('&')[0]
                return f'https://www.youtube.com/watch?v={video_id}'
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
                return f'https://youtu.be/{video_id}'
        return url

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

    def process_download(self, download_info):
        try:
            url = self.clean_url(download_info['url'])
            quality = download_info.get('quality', 'best')
            platform = self.get_platform(url)
            
            ydl_opts = {
                'format': self.get_format(url, quality),
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'extract_flat': True,
                'skip_download': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("Could not extract video information")

                formats = info.get('formats', [])
                if not formats:
                    raise Exception("No formats available")

                best_format = None
                for f in formats:
                    if f.get('ext') == 'mp4':
                        if not best_format or f.get('filesize', 0) > best_format.get('filesize', 0):
                            best_format = f

                if not best_format:
                    best_format = formats[-1]

                return {
                    'status': 'success',
                    'title': info.get('title', 'Unknown Title'),
                    'platform': platform,
                    'download_url': best_format.get('url'),
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
