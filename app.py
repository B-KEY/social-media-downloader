from flask import Flask, render_template, request, jsonify, g, send_file, Response
from flask_socketio import SocketIO, emit
import os
import logging
from utils.downloader import MediaDownloader
import secrets
import json
import time

# Global variable for tracking download progress
current_download_progress = {'percentage': 0, 'speed': 0}

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = secrets.token_hex(16)

# Configure download folder for Render.com
DOWNLOAD_FOLDER = '/tmp/downloads' if os.environ.get('RENDER') else os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max-limit

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_downloader():
    if 'downloader' not in g:
        g.downloader = MediaDownloader(DOWNLOAD_FOLDER)
    return g.downloader

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'Invalid request'}), 400

        downloader = get_downloader()
        url = data['url']
        quality = data.get('quality', 'best')
        
        # Process download
        result = downloader.process_download({
            'url': url,
            'quality': quality
        })

        if result.get('status') == 'error':
            return jsonify(result), 400

        return jsonify({
            'status': 'success',
            'file_path': result['file_path'],
            'title': result['title'],
            'ext': result.get('ext', 'mp4')
        })

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/get_file/<filename>')
def get_file(filename):
    try:
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'error': 'File not found'}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"File download error: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    try:
        current_time = time.time()
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                if current_time - os.path.getmtime(file_path) > 3600:
                    os.remove(file_path)
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")

@app.after_request
def after_request(response):
    cleanup_old_files()
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    socketio.run(app, host='0.0.0.0', port=port)