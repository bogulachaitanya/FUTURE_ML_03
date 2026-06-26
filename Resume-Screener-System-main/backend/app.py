import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from ml_engine import screen_resume, extract_skills, clean_text

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Resume Screener API is running!'})

@app.route('/api/screen', methods=['POST'])
def screen_single():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded'}), 400
    file = request.files['resume']
    job_desc = request.form.get('job_description', '')
    candidate = request.form.get('candidate_name', 'Candidate')
    if not job_desc:
        return jsonify({'error': 'Job description is required'}), 400
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    result = screen_resume(file_path, job_desc, candidate)
    os.remove(file_path)
    return jsonify(result)

@app.route('/api/rank', methods=['POST'])
def rank_candidates():
    files = request.files.getlist('resumes')
    job_desc = request.form.get('job_description', '')
    if not files or not job_desc:
        return jsonify({'error': 'Resumes and job description required'}), 400
    results = []
    for file in files:
        name = os.path.splitext(file.filename)[0]
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        result = screen_resume(file_path, job_desc, name)
        results.append(result)
        os.remove(file_path)
    results.sort(key=lambda x: x['total_score'], reverse=True)
    for i, r in enumerate(results):
        r['rank'] = i + 1
    return jsonify({'total_candidates': len(results), 'job_description_skills': extract_skills(clean_text(job_desc)), 'candidates': results})

# Replace the last 2 lines with this:
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)