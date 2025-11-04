from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # allows React frontend to call Flask backend

# Folder for saving uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return jsonify({"message": "Resume Checker Backend Running"})

@app.route('/check_resume', methods=['POST'])
def check_resume():
    # Check if a file is in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    position = request.form.get('position', '')
    description = request.form.get('description', '')

    if file.filename == '':
        return jsonify({'error': 'Empty file name'}), 400

    # Save uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # --- Resume Processing Logic (replace with AI model if needed) ---
    # For now, we’ll just simulate analysis.
    result = {
        'position': position,
        'recommendation': f"Your resume seems suitable for {position}. You may want to highlight skills related to leadership and impact.",
        'job_description_summary': description[:150] + '...' if description else "No job description provided."
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
