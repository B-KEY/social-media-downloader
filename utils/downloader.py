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
                return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            return f'bestvideo[height<={quality[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
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
            
            ydl_opts = {
                'format': self.get_format(url, quality),
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                    if info:
                        # Get the downloaded file path
                        if 'requested_downloads' in info:
                            file_path = info['requested_downloads'][0]['filepath']
                        else:
                            file_path = ydl.prepare_filename(info)
                        
                        # Read the file and return it
                        if os.path.exists(file_path):
                            return {
                                'status': 'success',
                                'title': info.get('title', 'Unknown'),
                                'platform': self.get_platform(url),
                                'file_path': file_path
                            }
                    raise Exception("Download failed")
                        
                except Exception as e:
                    print(f"First attempt failed: {str(e)}")
                    raise
                    
        except Exception as e:
            print(f"Download error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'platform': self.get_platform(url),
                'url': url
            }
