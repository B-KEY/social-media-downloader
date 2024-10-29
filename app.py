from flask import Flask, render_template, request, jsonify, g
from utils.downloader import MediaDownloader
import uuid
import os

app = Flask(__name__)

def get_downloader():
    if 'downloader' not in g:
        g.downloader = MediaDownloader(download_dir='/tmp/downloads')
    return g.downloader

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        url = data.get('url')
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        downloader = get_downloader()
        result = downloader.process_download({
            'id': str(uuid.uuid4()),
            'url': url,
            'quality': quality
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True)
