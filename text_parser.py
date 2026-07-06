from config import DAYS_KR
from subject_matcher import correct_subject

OCR_DIGIT_MAP = {
    'l': '1', 'I': '1', '|': '1', 'i': '1',
    'б': '6', 'G': '6', 'T': '7',
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
    t = OCR_DIGIT_MAP.get(text, text)
    return int(t) if t in [str(i) for i in range(1, 8)] else None

def _fill_missing_periods(period_items):
    if len(period_items) < 2:
        return period_items
    known = sorted(period_items, key=lambda p: p['period'])
    diffs = [(known[i+1]['y'] - known[i]['y']) / (known[i+1]['period'] - known[i]['period'])
             for i in range(len(known)-1)]
    row_h = sum(diffs) / len(diffs)
    ref = known[0]
    existing = {p['period'] for p in period_items}
    result = list(period_items)
    for p in range(1, 8):
        if p not in existing:
            result.append({'x': ref['x'], 'y': ref['y'] + (p - ref['period']) * row_h, 'period': p})
    return result

def parse_timetable(raw_results):
    items = []
    for bbox, text, conf in raw_results:
        cx = (bbox[0][0] + bbox[2][0]) / 2
        cy = (bbox[0][1] + bbox[2][1]) / 2
        items.append({'x': cx, 'y': cy, 'text': text.strip()})

    if not items:
        return {day: {} for day in DAYS_KR}

    timetable = {day: {} for day in DAYS_KR}
    day_x = {item['text']: item['x'] for item in items if item['text'] in DAYS_KR}

    if 3 <= len(day_x) < 5:
        for i, day in enumerate(DAYS_KR):
            if day not in day_x:
                prev = [DAYS_KR[j] for j in range(i-1, -1, -1) if DAYS_KR[j] in day_x]
                nxt  = [DAYS_KR[j] for j in range(i+1, 5) if DAYS_KR[j] in day_x]
                if prev and nxt:
                    day_x[day] = (day_x[prev[0]] + day_x[nxt[0]]) / 2

    if len(day_x) < 3:
        subj_items = [item for item in items
                      if item['text'] not in DAYS_KR
                      and correct_subject(item['text']) != item['text']]
        if not subj_items:
            return timetable
        col_centers = _cluster_columns([i['x'] for i in subj_items])
        if len(col_centers) < 2:
            return timetable
        day_x = {DAYS_KR[i]: col_centers[i] for i in range(min(5, len(col_centers)))}

    min_x = min(item['x'] for item in items)
    period_items = []
    for item in items:
        if item['x'] > min_x + 200:
            continue
        p = _to_period_num(item['text'])
        if p is not None:
            period_items.append({'x': item['x'], 'y': item['y'], 'period': p})

    if not period_items:
        return timetable

    period_items = _fill_missing_periods(period_items)

    # 행 높이 계산
    sorted_p = sorted(period_items, key=lambda p: p['period'])
    if len(sorted_p) >= 2:
        row_h = (sorted_p[-1]['y'] - sorted_p[0]['y']) / (sorted_p[-1]['period'] - sorted_p[0]['period'])
    else:
        row_h = 240

    subject_items = [item for item in items
                     if item['text'] not in DAYS_KR
                     and item['x'] > min_x + 80
                     and correct_subject(item['text']) != item['text']]

    for subj_item in subject_items:
        corrected = correct_subject(subj_item['text'])
        if corrected == subj_item['text']:
            continue
        closest_period = min(period_items, key=lambda p: abs(p['y'] - subj_item['y']))
        period_num = closest_period['period']
        y_dist = abs(closest_period['y'] - subj_item['y'])
        sorted_days = sorted(day_x, key=lambda d: abs(day_x[d] - subj_item['x']))

        # y 오차가 크면 다른 요일로 overflow 금지
        if y_dist > 0.30 * row_h:
            if period_num not in timetable[sorted_days[0]]:
                timetable[sorted_days[0]][period_num] = corrected
            # 이미 차있으면 skip (틀린 데이터 방지)
        else:
            assigned = False
            for day in sorted_days:
                if period_num not in timetable[day]:
                    timetable[day][period_num] = corrected
                    assigned = True
                    break
            if not assigned:
                timetable[sorted_days[0]][period_num] = corrected

    return timetable
