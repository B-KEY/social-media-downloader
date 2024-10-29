import yt_dlp
import os
from urllib.parse import urlparse

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

    def get_download_url(self, info, platform):
        try:
            # For YouTube
            if platform == 'youtube':
                formats = info.get('formats', [])
                # Filter for MP4 formats with both video and audio
                mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('acodec') != 'none']
                if mp4_formats:
                    return max(mp4_formats, key=lambda f: f.get('filesize', 0)).get('url')
                return formats[-1].get('url')

            # For Instagram
            elif platform == 'instagram':
                return info.get('url') or info.get('webpage_url')

            # For Facebook
            elif platform == 'facebook':
                if 'formats' in info:
                    formats = info['formats']
                    hd_format = next((f for f in formats if f.get('format_id') == 'hd'), None)
                    if hd_format:
                        return hd_format.get('url')
                return info.get('url')

            # For TikTok
            elif platform == 'tiktok':
                return info.get('url') or info.get('webpage_url')

            # Default fallback
            return info.get('url')

        except Exception as e:
            print(f"Error getting download URL: {str(e)}")
            return None

    def process_download(self, download_info):
        try:
            url = download_info['url']
            platform = self.get_platform(url)

            # Platform-specific options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'skip_download': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
            }

            # Platform specific configurations
            if platform == 'youtube':
                ydl_opts.update({
                    'format': 'best[ext=mp4]',
                    'extract_flat': False,
                    'extractor_args': {'youtube': {'player_client': ['web']}}
                })
            elif platform == 'instagram':
                ydl_opts.update({
                    'format': 'best',
                    'extract_flat': False
                })
            elif platform == 'facebook':
                ydl_opts.update({
                    'format': 'best',
                    'extract_flat': False
                })
            elif platform == 'tiktok':
                ydl_opts.update({
                    'format': 'best',
                    'extract_flat': False
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Extracting info for {platform}: {url}")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception(f"Could not extract {platform} video information")

                # Get download URL based on platform
                download_url = self.get_download_url(info, platform)
                
                if not download_url:
                    raise Exception(f"No download URL found for {platform}")

                # Get clean title
                title = info.get('title', 'video')
                title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()

                return {
                    'status': 'success',
                    'title': title,
                    'platform': platform,
                    'download_url': download_url,
                    'thumbnail': info.get('thumbnail'),
                    'duration': info.get('duration'),
                    'ext': 'mp4'
                }

        except Exception as e:
            print(f"Download error for {platform}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'platform': platform,
                'url': url
            }
