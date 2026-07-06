from flask import Flask, request, send_file, render_template
from datetime import datetime
import os
from ocr_processor import extract_raw
from text_parser import parse_timetable
from ics_generator import generate_ics

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('images')
    timetable = {}
    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        raw = extract_raw(path)
        result = parse_timetable(raw)
        for day, periods in result.items():
            if day not in timetable:
                timetable[day] = {}
            timetable[day].update(periods)
    ics_data = generate_ics(timetable, datetime.today())

    output_path = 'timetable.ics'
    with open(output_path, 'wb') as f:
            f.write(ics_data)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)