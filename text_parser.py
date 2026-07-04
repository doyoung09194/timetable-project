from config import DAYS_KR
from subject_matcher import correct_subject

def parse_timetable(raw_results):
    items = []
    for bbox, text, conf in raw_results:
        cx = (bbox[0][0] + bbox[2][0]) / 2
        cy = (bbox[0][1] + bbox[2][1]) / 2
        items.append({'x': cx, 'y': cy, 'text': text.strip()})

    day_x = {item['text']: item['x'] for item in items if item['text'] in DAYS_KR}
    if len(day_x) < 3:
        return {}

    header_y = max(item['y'] for item in items if item['text'] in DAYS_KR)
    below = sorted([i for i in items if i['y'] > header_y + 10], key=lambda x: x['y'])

    rows, current = [], [below[0]] if below else []
    for item in below[1:]:
        if abs(item['y'] - current[-1]['y']) < 30:
            current.append(item)
        else:
            rows.append(current)
            current = [item]
    if current:
        rows.append(current)

    timetable = {day: {} for day in DAYS_KR}
    period = 1
    for row in rows:
        day_subjects = {}
        for item in row:
            corrected = correct_subject(item['text'])
            if corrected != item['text']:
                closest = min(day_x, key=lambda d: abs(day_x[d] - item['x']))
                day_subjects[closest] = corrected
        if len(day_subjects) >= 3 and period <= 7:
            for day, subj in day_subjects.items():
                timetable[day][period] = subj
            period += 1

    return timetable