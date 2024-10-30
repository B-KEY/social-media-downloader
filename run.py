import os
from pathlib import Path
from app import app
from waitress import serve

# Ensure downloads directory exists
downloads_dir = os.path.join(str(Path.home()), 'Desktop', 'downloads')
os.makedirs(downloads_dir, exist_ok=True)

if __name__ == '__main__':
    print(f"Server starting... Downloads will be saved to: {downloads_dir}")
    serve(app, host='127.0.0.1', port=5000) 