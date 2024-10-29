import yt_dlp
import os
import re
import time
import threading
from pathlib import Path

class MediaDownloader:
    def __init__(self, download_dir='/tmp/downloads'):
        self.download_dir = download_dir
        self.is_cancelled = False
        self.is_paused = False
        self.current_download = {
            'status': 'idle',
            'progress': 0,
            'speed': 0,
            'eta': 0
        }
        os.makedirs(self.download_dir, exist_ok=True)

    def get_platform(self, url):
        url = url.lower()
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'facebook.com' in url or 'fb.watch' in url:
            return 'facebook'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'twitter'
        return 'unknown'

    def clean_url(self, url):
        """Clean the URL by removing playlist and other unnecessary parameters"""
        if 'youtube.com' in url.lower() or 'youtu.be' in url.lower():
            try:
                # Extract video ID
                if 'watch?v=' in url:
                    video_id = url.split('watch?v=')[1].split('&')[0]
                    return f'https://www.youtube.com/watch?v={video_id}'
                elif 'youtu.be/' in url:
                    video_id = url.split('youtu.be/')[1].split('?')[0].split('&')[0]
                    return f'https://youtu.be/{video_id}'
            except Exception:
                pass
        return url

    def sanitize_filename(self, filename):
        # Remove invalid characters and limit length
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'[&]', 'and', filename)
        # Limit filename length (Windows has 255 char limit)
        if len(filename) > 200:
            filename = filename[:200]
        return filename.strip()

    def get_video_info(self, url):
        url = self.clean_url(url)
        platform = self.get_platform(url)
        options = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration'),
                    'filesize': info.get('filesize'),
                    'thumbnail': info.get('thumbnail'),
                    'platform': platform
                }
        except Exception as e:
            raise Exception(f"Could not fetch video information: {str(e)}")

    def progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("Download cancelled")
            
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    progress = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed = speed / (1024 * 1024)  # Convert to MB/s
                    
                    self.current_download = {
                        'status': 'downloading',
                        'progress': round(progress, 1),
                        'speed': round(speed, 2) if speed else 0,
                        'eta': d.get('eta', 0)
                    }
                    
                    if self.is_paused:
                        raise Exception("Download paused")
                    
            except Exception as e:
                print(f"Progress calculation error: {e}")

        elif d['status'] == 'finished':
            self.current_download = {
                'status': 'completed',
                'progress': 100,
                'speed': 0,
                'eta': 0
            }

    def download_worker(self, url, ydl_opts):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    title = self.sanitize_filename(info.get('title', 'video'))
                    self.current_download.update({
                        'title': title,
                        'filename': f"{title}.{info.get('ext', 'mp4')}"
                    })
                    ydl.download([url])
        except Exception as e:
            if not self.is_cancelled:
                self.current_download.update({
                    'status': 'error',
                    'error': str(e)
                })

    def process_download(self, download_info):
        try:
            url = self.clean_url(download_info['url'])  # Clean the URL first
            quality = download_info.get('quality', 'best')
            
            ydl_opts = {
                'format': self.get_format(url, quality),
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'noplaylist': True,  # Add this to prevent playlist downloads
                'extract_flat': False,
                'playlistrandom': False,
                'playliststart': 1,
                'playlistend': 1
            }
            
            self.is_cancelled = False
            self.is_paused = False
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'title': info.get('title', 'Unknown'),
                    'platform': self.get_platform(url)
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def get_format(self, url, quality='best'):
        """Get the format string based on URL and quality"""
        platform = self.get_platform(url)
        
        if platform == 'youtube':
            # Convert quality string to height
            quality_map = {
                'highest': 2160,
                'high': 1080,
                'medium': 720,
                'low': 480,
                'lowest': 360
            }
            height = quality_map.get(quality, 720)  # default to 720p
            return f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best'
        elif platform == 'twitter':
            return 'best[ext=mp4]/best'
        else:  # facebook, instagram, tiktok, etc.
            return 'best'

    def cleanup_partial_files(self, filename_pattern):
        """Clean up partial download files"""
        try:
            directory = Path(self.download_dir)
            for file in directory.glob(f"{filename_pattern}*.part*"):
                try:
                    file.unlink()
                except:
                    pass
        except Exception as e:
            print(f"Cleanup error: {e}")

    def cancel_download(self):
        self.is_cancelled = True
        self.current_download = {
            'status': 'cancelled',
            'progress': 0
        }

    def pause_download(self):
        self.is_paused = True
        if self.current_download:
            self.current_download['status'] = 'paused'

    def resume_download(self):
        self.is_paused = False
        if self.current_download:
            self.current_download['status'] = 'downloading'

    def get_progress(self):
        """Get current download progress"""
        return self.current_download

    def get_download_status(self, download_id):
        return self.downloads.get(download_id, {
            'status': 'not_found',
            'progress': 0
        })

    def cleanup(self):
        """Reset the downloader state"""
        self.is_cancelled = False
        self.is_paused = False
        self.current_download = {
            'status': 'idle',
            'progress': 0,
            'speed': 0,
            'eta': 0
        }
