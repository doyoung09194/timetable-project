import easyocr

reader = easyocr.Reader(['ko', 'en'])

def extract_text(image_path):
    results = reader.readtext(image_path)
    lines = [text for (_, text, _) in results]
    return "\n".join(lines)
def extract_raw(image_path):
    return reader.readtext(image_path)