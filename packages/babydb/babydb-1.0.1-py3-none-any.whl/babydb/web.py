from flask import Flask, send_file, jsonify
import json
import os
import tempfile
import gzip
import shutil
from .core import SimpleDB

app = Flask(__name__, static_folder='.', static_url_path='')
db = SimpleDB()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/login/<username>/<password>')
def login(username, password):
    result = db.login(username, password)
    return jsonify({"message": result})

@app.route('/api/list')
def list_all():
    if not db.current_user:
        return jsonify({"error": "Must be logged in to list records"}), 401
    result = db.list_all()
    records = []
    for line in result.split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            records.append({"key": key, "value": json.loads(value)})
    return jsonify({"records": records})

@app.route('/files/<path:filename>')
def serve_file(filename):
    if not db.current_user:
        return jsonify({"error": "Must be logged in to access files"}), 401
    file_path = os.path.join('files', filename)
    if not os.path.exists(file_path):
        return jsonify({"error": f"File {filename} not found"}), 404
    if filename.endswith('.gz'):
        original_ext = '.png' if 'png' in filename else '.jpg' if 'jpg' in filename else '.pdf' if 'pdf' in filename else '.doc' if 'doc' in filename else '.docx'
        temp_dir = tempfile.gettempdir()
        temp_filename = f"decompressed_{filename[:-3]}"
        temp_path = os.path.join(temp_dir, temp_filename)
        try:
            with gzip.open(file_path, 'rb') as src, open(temp_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            return send_file(temp_path, as_attachment=False, download_name=temp_filename)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    return send_file(file_path, as_attachment=False)

def run_web():
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run_web()