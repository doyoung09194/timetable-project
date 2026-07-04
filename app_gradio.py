import gradio as gr
import tempfile
from datetime import datetime

# gradio_client 버그 패치: bool 스키마 처리 오류 수정
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

demo = gr.Interface(
    fn=convert,
    inputs=gr.File(file_count="multiple", label="시간표 사진 업로드"),
    outputs=gr.File(label="캘린더 파일 다운로드"),
    title="📅 학교 시간표 → 캘린더 변환기",
    description="시간표 사진을 올리면 캘린더(.ics) 파일로 변환해드려요!"
)
demo.launch()
