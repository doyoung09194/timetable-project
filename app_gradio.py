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
from text_parser import parse_timetable, _fill_missing_periods, _to_period_num
from ics_generator import generate_ics
from subject_matcher import correct_subject

def convert(image1, image2):
    timetable = {}
    debug_lines = []

    for image_path in [image1, image2]:
        if image_path is None:
            continue
        raw = extract_raw(image_path)

        items = []
        for bbox, text, conf in raw:
            cx = (bbox[0][0] + bbox[2][0]) / 2
            cy = (bbox[0][1] + bbox[2][1]) / 2
            items.append({'x': cx, 'y': cy, 'text': text.strip()})
        if items:
            min_x = min(i['x'] for i in items)
            period_items = []
            for item in items:
                if item['x'] > min_x + 200:
                    continue
                p = _to_period_num(item['text'])
                if p is not None:
                    period_items.append({'x': item['x'], 'y': item['y'], 'period': p})
            period_items = _fill_missing_periods(period_items)
            for pi in sorted(period_items, key=lambda p: p['period']):
                debug_lines.append(f"{pi['period']}교시 y={int(pi['y'])}")
            for item in items:
                if item['x'] <= min_x + 80:
                    continue
                corrected = correct_subject(item['text'])
                if corrected != item['text']:
                    debug_lines.append(f"  '{item['text']}'->'{corrected}' x={int(item['x'])} y={int(item['y'])}")

        result = parse_timetable(raw)
        debug_lines.append(f"파싱: {result}")
        for day, periods in result.items():
            if day not in timetable:
                timetable[day] = {}
            timetable[day].update(periods)

    debug_text = "\n".join(debug_lines)

    if not timetable or all(len(v) == 0 for v in timetable.values()):
        return None, debug_text

    timetable.setdefault("수", {})
    timetable["수"][5] = "창의적 체험활동"
    timetable["수"][6] = "창의적 체험활동"

    ics_data = generate_ics(timetable, datetime.today())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.ics')
    tmp.write(ics_data)
    tmp.close()
    return tmp.name, debug_text

demo = gr.Interface(
    fn=convert,
    inputs=[
        gr.Image(type="filepath", label="시간표 사진 1 (헤더 포함)", height=200),
        gr.Image(type="filepath", label="시간표 사진 2 (선택사항)", height=200),
    ],
    outputs=[
        gr.File(label="캘린더 파일 다운로드"),
        gr.Textbox(label="디버그", lines=20),
    ],
    title="학교 시간표 -> 캘린더 변환기",
    description="시간표 사진을 올리면 캘린더(.ics) 파일로 변환해드려요!"
)
demo.launch()
