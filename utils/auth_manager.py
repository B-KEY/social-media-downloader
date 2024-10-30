import os
import json
import logging
import browser_cookie3
from pathlib import Path

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self):
        self.cookie_dir = os.path.join(os.getcwd(), 'cookies')
        os.makedirs(self.cookie_dir, exist_ok=True)
        self.cookie_file = os.path.join(self.cookie_dir, 'cookies.txt')
        self._initialize_cookies()

    def _initialize_cookies(self):
        """Initialize cookie file if it doesn't exist"""
        if not os.path.exists(self.cookie_file):
            try:
                # Try to get cookies from browser
                self._extract_browser_cookies()
            except Exception as e:
                logger.warning(f"Could not extract browser cookies: {str(e)}")
                # Create empty cookie file
                with open(self.cookie_file, 'w') as f:
                    f.write('')

    def _extract_browser_cookies(self):
        """Extract cookies from browser"""
        try:
            # Try Chrome first
            cookies = browser_cookie3.chrome(domain_name=".instagram.com")
        except:
            try:
                # Try Firefox if Chrome fails
                cookies = browser_cookie3.firefox(domain_name=".instagram.com")
            except:
                logger.warning("Could not extract cookies from any browser")
                return

        # Save cookies to file
        with open(self.cookie_file, 'w') as f:
            for cookie in cookies:
                f.write(f"{cookie.domain}\tTRUE\t{cookie.path}\t"
                       f"{'TRUE' if cookie.secure else 'FALSE'}\t{cookie.expires}\t"
                       f"{cookie.name}\t{cookie.value}\n")

    def check_auth(self, platform):
        """Check if we have valid authentication for platform"""
        try:
            if not os.path.exists(self.cookie_file):
                return False

            with open(self.cookie_file, 'r') as f:
                content = f.read()
                
            # Check for platform-specific cookies
            platform_domains = {
                'instagram': '.instagram.com',
                'facebook': '.facebook.com',
                'twitter': ['.twitter.com', '.x.com']
            }
            
            domains = platform_domains.get(platform, [])
            if isinstance(domains, str):
                domains = [domains]
                
            return any(domain in content for domain in domains)

        except Exception as e:
            logger.error(f"Auth check error: {str(e)}")
            return False

    def get_headers(self):
        """Get common headers for requests"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
