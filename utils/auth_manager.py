import os
import random

class AuthManager:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0'
        ]
        
        self.cookie_file = 'cookies.txt'
        self.load_cookies()

    def load_cookies(self):
        if not os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'w') as f:
                f.write('# Netscape HTTP Cookie File\n')
                f.write('# https://curl.haxx.se/rfc/cookie_spec.html\n')
                f.write('# This is a generated file!  Do not edit.\n\n')

    def get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
            'Connection': 'keep-alive'
        }

    def get_download_options(self, platform):
        options = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'cookiefile': self.cookie_file,
            'http_headers': self.get_headers(),
            'socket_timeout': 30,
            'retries': 5,
            'nocheckcertificate': True
        }
        
        # Remove cookiefile for platforms that don't need it
        if platform in ['youtube', 'facebook']:
            options.pop('cookiefile', None)
        
        return options