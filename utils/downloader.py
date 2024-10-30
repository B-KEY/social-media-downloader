import os
import yt_dlp
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class MediaDownloader:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.progress_callback = None

    def _get_platform(self, url):
        """Determine platform from URL"""
        domain = urlparse(url).netloc.lower()
        if any(x in domain for x in ['youtube.com', 'youtu.be']):
            return 'youtube'
        elif 'tiktok.com' in domain:
            return 'tiktok'
        elif 'instagram.com' in domain:
            return 'instagram'
        elif 'facebook.com' in domain or 'fb.com' in domain:
            return 'facebook'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'twitter'
        return 'unknown'

    def process_download(self, download_info):
        """Process download request"""
        try:
            url = download_info['url']
            quality = download_info.get('quality', 'best')
            platform = self._get_platform(url)

            logger.info(f"Starting download: {platform} - {url}")

            # Configure yt-dlp options
            ydl_opts = {
                'format': self._get_format_string(platform, quality),
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'nocheckcertificate': True,
                'progress_hooks': [self._progress_hook],
                'merge_output_format': 'mp4',
                'retries': 3,
                'fragment_retries': 3,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Could not extract video information")

                # Prepare filename
                video_title = self._sanitize_filename(info.get('title', 'video'))
                file_path = os.path.join(self.download_dir, f"{video_title}.mp4")
                ydl_opts['outtmpl'] = file_path

                # Download video
                ydl.download([url])

                return {
                    'status': 'success',
                    'file_path': file_path,
                    'title': video_title,
                    'ext': 'mp4'
                }

        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return {'status': 'error', 'error': str(e)}

    def _get_format_string(self, platform, quality):
        """Get format string based on platform and quality"""
        if platform == 'youtube':
            if quality != 'best':
                return f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]'
            return 'bestvideo+bestaudio/best'
        elif platform == 'tiktok':
            return 'best[ext=mp4]/best'
        else:
            return 'best'

    def _progress_hook(self, d):
        """Handle download progress updates"""
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    percentage = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    
                    if self.progress_callback:
                        self.progress_callback({
                            'percentage': percentage,
                            'speed': speed
                        })
            except Exception as e:
                logger.error(f"Progress hook error: {str(e)}")

    def _sanitize_filename(self, filename):
        """Sanitize filename to prevent issues"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Limit length
        filename = filename[:50]
        
        return filename.strip()