from config import DAYS_KR
from subject_matcher import correct_subject

# OCR이 숫자를 잘못 읽는 경우 매핑
OCR_DIGIT_MAP = {
    'l': '1', 'I': '1', '|': '1', 'i': '1', '！': '1',
    'б': '6', 'G': '6',
    'T': '7',
}

def _cluster_columns(x_list, gap=80):
    if not x_list:
        return []
    sorted_xs = sorted(set(int(x) for x in x_list))
    groups = [[sorted_xs[0]]]
    for x in sorted_xs[1:]:
        if x - groups[-1][-1] > gap:
            groups.append([x])
        else:
            groups[-1].append(x)
    return [sum(g) / len(g) for g in groups]

def _to_period_num(text):
    """텍스트를 교시 번호(1-7)로 변환. 변환 불가면 None."""
    t = OCR_DIGIT_MAP.get(text, text)
    if t in [str(i) for i in range(1, 8)]:
        return int(t)
    return None

def parse_timetable(raw_results):
    items = []
    for bbox, text, conf in raw_results:
        cx = (bbox[0][0] + bbox[2][0]) / 2
        cy = (bbox[0][1] + bbox[2][1]) / 2
        items.append({'x': cx, 'y': cy, 'text': text.strip()})

    if not items:
        return {}

    timetable = {day: {} for day in DAYS_KR}

    # 요일 헤더 x 좌표
    day_x = {item['text']: item['x'] for item in items if item['text'] in DAYS_KR}

    if len(day_x) < 3:
        subj_items = [item for item in items
                      if item['text'] not in DAYS_KR
                      and correct_subject(item['text']) != item['text']]
        if not subj_items:
            return {}
        col_centers = _cluster_columns([i['x'] for i in subj_items])
        if len(col_centers) < 2:
            return {}
        day_x = {DAYS_KR[i]: col_centers[i] for i in range(min(5, len(col_centers)))}

    # 교시 번호 찾기 (왼쪽 컬럼, OCR 오인식 포함)
    min_x = min(item['x'] for item in items)
    period_items = []
    for item in items:
        if item['x'] > min_x + 200:
            continue
        p = _to_period_num(item['text'])
        if p is not None:
            period_items.append({'x': item['x'], 'y': item['y'], 'period': p})

    # 교시 번호가 없으면 y좌표 순서로 1부터 부여
    if not period_items:
        # 헤더 아래 구분되는 y 위치들을 찾아서 교시로 사용
        header_y = max((item['y'] for item in items if item['text'] in DAYS_KR), default=0)
        subj_ys = sorted(set(
            round(item['y'] / 50) * 50
            for item in items
            if item['y'] > header_y + 20
            and item['text'] not in DAYS_KR
            and correct_subject(item['text']) != item['text']
        ))
        for i, y in enumerate(subj_ys[:7]):
            period_items.append({'x': min_x, 'y': y, 'period': i + 1})

    if not period_items:
        return {}

    # 과목으로 인식된 아이템들 (요일 제외)
    subject_items = [item for item in items
                     if item['text'] not in DAYS_KR
                     and item['x'] > min_x + 80
                     and correct_subject(item['text']) != item['text']]

    for subj_item in subject_items:
        corrected = correct_subject(subj_item['text'])
        if corrected == subj_item['text']:
            continue
        # 가장 가까운 교시 번호 (y 기준)
        closest_period = min(period_items, key=lambda p: abs(p['y'] - subj_item['y']))
        period_num = closest_period['period']
        # 가장 가까운 요일 (x 기준)
        closest_day = min(day_x, key=lambda d: abs(day_x[d] - subj_item['x']))
        timetable[closest_day][period_num] = corrected

    return timetable
