import easyocr
from PIL import Image

reader = easyocr.Reader(['ko', 'en'])

def extract_raw(image_path):
    img = Image.open(image_path)
    w, h = img.size
    # 너비 기준으로 800px로 줄이기
    target_w = 800
    if w > target_w:
        ratio = target_w / w
        img = img.resize((target_w, int(h * ratio)), Image.LANCZOS)
        tmp_path = image_path + "_resized.jpg"
        img.save(tmp_path, quality=90)
        image_path = tmp_path
    return reader.readtext(image_path)
