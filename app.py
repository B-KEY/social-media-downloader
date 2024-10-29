from flask import Flask, render_template, request, jsonify, g
from utils.downloader import MediaDownloader
import uuid
import os

app = Flask(__name__)

def get_downloader():
    if 'downloader' not in g:
        g.downloader = MediaDownloader()
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

# For Render deployment
app.wsgi_app = app.wsgi_app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
