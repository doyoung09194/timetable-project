import gradio as gr
import tempfile
from datetime import datetime

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
from subject_matcher import correct_subject

def convert(image1, image2):
    timetable = {}
    debug_lines = []

    for image_path in [image1, image2]:
        if image_path is None:
            continue
        raw = extract_raw(image_path)
        debug_lines.append(f"=== OCR 결과 ({len(raw)}개) ===")
        for bbox, text, conf in raw:
            corrected = correct_subject(text.strip())
            mark = " ✓" if corrected != text.strip() else ""
            debug_lines.append(f"  '{text.strip()}'{mark}")

        result = parse_timetable(raw)
        debug_lines.append(f"파싱 결과: {result}")

        for day, periods in result.items():
            if day not in timetable:
                timetable[day] = {}
            timetable[day].update(periods)

    debug_text = "\n".join(debug_lines)

    if not timetable:
        return None, "인식된 과목이 없습니다.\n\n" + debug_text

    ics_data = generate_ics(timetable, datetime.today())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.ics')
    tmp.write(ics_data)
    tmp.close()
    return tmp.name, debug_text

demo = gr.Interface(
    fn=convert,
    inputs=[
        gr.Image(type="filepath", label="시간표 사진 1", height=200),
        gr.Image(type="filepath", label="시간표 사진 2 (선택사항)", height=200),
    ],
    outputs=[
        gr.File(label="캘린더 파일 다운로드"),
        gr.Textbox(label="디버그 정보", lines=20),
    ],
    title="📅 학교 시간표 → 캘린더 변환기",
    description="시간표 사진을 올리면 캘린더(.ics) 파일로 변환해드려요!"
)
demo.launch()
