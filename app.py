from flask import Flask, request, send_file, render_template, send_from_directory, jsonify
from gradio_client import Client, file
import shutil
import os
import tempfile
import base64

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_images():
    if 'source' not in request.files or 'target' not in request.files:
        return 'No files uploaded', 400

    source_file = request.files['source']
    target_file = request.files['target']

    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        source_path = os.path.join(temp_dir, 'source.png')
        target_path = os.path.join(temp_dir, 'target.png')
        
        # Save uploaded files
        source_file.save(source_path)
        target_file.save(target_path)

        # Initialize the client
        client = Client("felixrosberg/face-swap")
        
        # Process the images
        result = client.predict(
            target=file(target_path),
            source=file(source_path),
            slider=100,
            adv_slider=100,
            settings=[],
            api_name="/run_inference"
        )

        # Copy result to a known location
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_image.webp')
        shutil.copy2(result, output_path)
        
        # Return the file path
        return jsonify({'status': 'success', 'file_path': '/get_result'})

@app.route('/get_result')
def get_result():
    return send_file('generated_image.webp', mimetype='image/webp')

if __name__ == '__main__':
    app.run(debug=True)