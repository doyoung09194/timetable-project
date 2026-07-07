from fastapi import FastAPI
from fastapi.responses import Response
import gradio as gr
import uvicorn
import tempfile
import secrets
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

# 토큰별 ICS 저장 (최대 20개)
ics_store = {}

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
        return None, ""

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

    # 토큰 생성 및 저장
    token = secrets.token_urlsafe(8)
    if len(ics_store) >= 20:
        oldest = next(iter(ics_store))
        del ics_store[oldest]
    ics_store[token] = ics_data

    # 파일 저장 (안드로이드/PC용)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.ics')
    tmp.write(ics_data)
    tmp.close()

    ios_html = f'<p style="text-align:center;margin-top:12px;font-size:15px;">아이폰: <a href="/calendar/{token}.ics" style="color:#007AFF;font-weight:bold;">여기를 Safari에서 탭하세요</a></p>'

    return tmp.name, ios_html


# FastAPI 앱
fastapi_app = FastAPI()

@fastapi_app.get("/calendar/{token}.ics")
async def serve_calendar(token: str):
    if token not in ics_store:
        return Response("만료된 링크입니다. 다시 변환해주세요.", status_code=404, media_type="text/plain")
    return Response(
        content=ics_store[token],
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="timetable.ics"'}
    )


demo = gr.Interface(
    fn=convert,
    inputs=[
        gr.Image(type="filepath", label="시간표 사진 1 (헤더 포함)", height=200),
        gr.Image(type="filepath", label="시간표 사진 2 (선택사항)", height=200),
        gr.Textbox(label="개학일 (YYYY-MM-DD)", value="2026-03-02"),
        gr.Textbox(label="방학 시작일 (YYYY-MM-DD)", value="2026-07-20"),
    ],
    outputs=[
        gr.File(label="캘린더 파일 다운로드 (안드로이드/PC)"),
        gr.HTML(label="아이폰용 링크"),
    ],
    title="학교 시간표 -> 캘린더 변환기",
    description="시간표 사진을 올리면 캘린더(.ics) 파일로 변환해드려요!"
)

app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
