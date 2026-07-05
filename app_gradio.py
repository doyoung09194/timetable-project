import gradio as gr
import tempfile
from datetime import datetime

# gradio_client 버그 패치
try:
    import gradio_client.utils as _gcu
    _orig_fn = _gcu._json_schema_to_python_type
    def _patched_fn(schema, defs=None):
        if isinstance(schema, bool):
            return "any"
        return _orig_fn(schema, defs)
    _gcu._json_schema_to_python_type = _patched_fn
except Exception:
    pass

from ocr_processor import extract_raw
from text_parser import parse_timetable
from ics_generator import generate_ics

def convert(image1, image2):
    timetable = {}
    for image_path in [image1, image2]:
        if image_path is None:
            continue
        raw = extract_raw(image_path)
        result = parse_timetable(raw)
        for day, periods in result.items():
            if day not in timetable:
                timetable[day] = {}
            timetable[day].update(periods)
    if not timetable:
        return None
    ics_data = generate_ics(timetable, datetime.today())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.ics')
    tmp.write(ics_data)
    tmp.close()
    return tmp.name

demo = gr.Interface(
    fn=convert,
    inputs=[
        gr.Image(type="filepath", label="시간표 사진 1", height=200),
        gr.Image(type="filepath", label="시간표 사진 2 (선택사항)", height=200),
    ],
    outputs=gr.File(label="캘린더 파일 다운로드"),
    title="📅 학교 시간표 → 캘린더 변환기",
    description="시간표 사진을 올리면 캘린더(.ics) 파일로 변환해드려요!"
)
demo.launch()
