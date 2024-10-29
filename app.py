from flask import Flask, render_template, request, jsonify, g, send_file
from utils.downloader import MediaDownloader
import os
import uuid

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
        
        if result.get('status') == 'success' and result.get('file_path'):
            # Send the file to the client
            return send_file(
                result['file_path'],
                as_attachment=True,
                download_name=os.path.basename(result['file_path'])
            )
            
        return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
