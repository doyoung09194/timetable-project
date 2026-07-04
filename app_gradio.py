import gradio as gr
import tempfile
from datetime import datetime
from ocr_processor import extract_raw
from text_parser import parse_timetable
from ics_generator import generate_ics

def convert(images):
    if not images:
        return None
    timetable = {}
    for image in images:
        image_path = image if isinstance(image, str) else image.name
        raw = extract_raw(image_path)
        result = parse_timetable(raw)
        for day, periods in result.items():
            if day not in timetable:
                timetable[day] = {}
            timetable[day].update(periods)
    ics_data = generate_ics(timetable, datetime.today())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.ics')
    tmp.write(ics_data)
    tmp.close()
    return tmp.name

with gr.Blocks(title="학교 시간표 → 캘린더 변환기") as demo:
    gr.Markdown("# 📅 학교 시간표 → 캘린더 변환기")
    gr.Markdown("시간표 사진을 올리면 캘린더(.ics) 파일로 변환해드려요!")
    with gr.Row():
        file_input = gr.Files(label="시간표 사진 업로드")
        file_output = gr.File(label="캘린더 파일 다운로드")
    btn = gr.Button("변환하기", variant="primary")
    btn.click(fn=convert, inputs=file_input, outputs=file_output)

demo.launch(show_api=False)
