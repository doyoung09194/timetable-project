import easyocr
from PIL import Image

reader = easyocr.Reader(['ko', 'en'])

def extract_raw(image_path):
    img = Image.open(image_path)
    w, h = img.size
    # 600px로 더 줄이기 (속도 우선)
    max_dim = 600
    if max(w, h) > max_dim:
        ratio = max_dim / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        tmp_path = image_path + "_resized.jpg"
        img.save(tmp_path, quality=95)
        image_path = tmp_path
    return reader.readtext(image_path)
