from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv
from PIL import Image
import io
import time

app = Flask(__name__)
# Enable CORS for all routes and all origins
CORS(app)

# Load environment variables
load_dotenv()

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({"status": "API is running"})

@app.after_request
def after_request(response):
    # Add CORS headers to every response
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.route('/process', methods=['POST', 'OPTIONS'])
def process_images():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204

    if 'source' not in request.files or 'target' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    source_file = request.files['source']
    target_file = request.files['target']

    if source_file.filename == '' or target_file.filename == '':
        return jsonify({'error': 'No files selected'}), 400

    if not (allowed_file(source_file.filename) and allowed_file(target_file.filename)):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Your existing processing logic here
        timestamp = str(int(time.time()))
        result_filename = f'result_{timestamp}.webp'
        result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)

        # Save the result
        # This is where you'd put your face swap processing logic
        # For now, we'll just save the target image as the result
        target_image = Image.open(target_file)
        target_image.save(result_path, 'WEBP')

        return jsonify({
            'status': 'success',
            'file_path': f'/results/{result_filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<filename>')
def uploaded_file(filename):
    try:
        return send_file(
            os.path.join(app.config['RESULT_FOLDER'], filename),
            mimetype='image/webp'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))