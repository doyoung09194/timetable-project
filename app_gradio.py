import gradio as gr
import json
from datetime import datetime, date

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

def convert(image1, image2, start_date_str, end_date_str):
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

    if not timetable or all(len(v) == 0 for v in timetable.values()):
        return "<p>시간표를 인식하지 못했어요. 사진을 다시 확인해주세요.</p>"

    timetable.setdefault("수", {})
    timetable["수"][5] = "창의적 체험활동"
    timetable["수"][6] = "창의적 체험활동"

    try:
        start_date = datetime.strptime(start_date_str.strip(), "%Y-%m-%d")
    except Exception:
        start_date = datetime.today()

    end_date = None
    try:
        end_date = datetime.strptime(end_date_str.strip(), "%Y-%m-%d").date()
    except Exception:
        pass

    ics_data = generate_ics(timetable, start_date, end_date)
    ics_text = ics_data.decode('utf-8')
    ics_json = json.dumps(ics_text)

    html = f"""<div style="text-align:center;padding:20px;">
<button onclick="(function(){{var c={ics_json};var b=new Blob([c],{{type:'text/calendar;charset=utf-8'}});var u=URL.createObjectURL(b);var a=document.createElement('a');a.href=u;a.download='시간표.ics';document.body.appendChild(a);a.click();document.body.removeChild(a);setTimeout(function(){{URL.revokeObjectURL(u);}},1000);}})();" style="background:#4CAF50;color:white;padding:16px 32px;border:none;border-radius:10px;font-size:17px;cursor:pointer;font-weight:bold;">📅 캘린더 파일 다운로드</button>
<p style="color:#888;font-size:13px;margin-top:12px;">아이폰: 버튼 탭 → 파일 앱에서 열기 → 캘린더에 추가</p>
</div>"""

    return html

demo = gr.Interface(
    fn=convert,
    inputs=[
        gr.Image(type="filepath", label="시간표 사진 1 (헤더 포함)", height=200),
        gr.Image(type="filepath", label="시간표 사진 2 (선택사항)", height=200),
        gr.Textbox(label="개학일 (YYYY-MM-DD)", value="2026-03-02"),
        gr.Textbox(label="방학 시작일 (YYYY-MM-DD)", value="2026-07-20"),
    ],
    outputs=[
        gr.HTML(label="다운로드"),
    ],
    title="학교 시간표 -> 캘린더 변환기",
    description="시간표 사진을 올리면 캘린더(.ics) 파일로 변환해드려요!"
)
demo.launch(server_name="0.0.0.0")
