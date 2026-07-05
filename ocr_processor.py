import easyocr
from PIL import Image

reader = easyocr.Reader(['ko', 'en'])

def extract_raw(image_path):
    # 이미지 크기 줄이기 (OCR 속도 향상)
    img = Image.open(image_path)
    w, h = img.size
    max_dim = 1000
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        tmp_path = image_path + "_resized.jpg"
        img.save(tmp_path)
        image_path = tmp_path
    return reader.readtext(image_path)
