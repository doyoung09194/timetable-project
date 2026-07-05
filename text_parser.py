from config import DAYS_KR
from subject_matcher import correct_subject

def _cluster_columns(x_list, gap=80):
    """x 좌표 리스트를 간격 기준으로 컬럼 그룹으로 묶기"""
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

    # 헤더 없으면 과목 x 좌표로 컬럼 추정
    if len(day_x) < 3:
        subj_items = [item for item in items if correct_subject(item['text']) != item['text']]
        if not subj_items:
            return {}
        col_centers = _cluster_columns([i['x'] for i in subj_items])
        if len(col_centers) < 2:
            return {}
        day_x = {DAYS_KR[i]: col_centers[i] for i in range(min(5, len(col_centers)))}

    # 교시 번호 찾기 (왼쪽 끝 컬럼에 있는 1~7)
    min_x = min(item['x'] for item in items)
    period_items = sorted(
        [item for item in items
         if item['text'] in [str(i) for i in range(1, 8)]
         and item['x'] < min_x + 150],
        key=lambda i: i['y']
    )

    if period_items:
        # 교시 번호 기반 파싱
        for p_item in period_items:
            period_num = int(p_item['text'])
            p_y = p_item['y']
            row_items = [i for i in items
                         if abs(i['y'] - p_y) < 45 and i['x'] > p_item['x'] + 30]
            for item in row_items:
                corrected = correct_subject(item['text'])
                if corrected != item['text']:
                    closest = min(day_x, key=lambda d: abs(day_x[d] - item['x']))
                    timetable[closest][period_num] = corrected
    else:
        # 헤더 아래 행 순서대로 파싱
        header_y = max((item['y'] for item in items if item['text'] in DAYS_KR), default=0)
        below = sorted([i for i in items if i['y'] > header_y + 10], key=lambda i: i['y'])
        if not below:
            return {}

        rows, current = [], [below[0]]
        for item in below[1:]:
            if abs(item['y'] - current[-1]['y']) < 30:
                current.append(item)
            else:
                rows.append(current)
                current = [item]
        if current:
            rows.append(current)

        period = 1
        for row in rows:
            day_subjects = {}
            for item in row:
                corrected = correct_subject(item['text'])
                if corrected != item['text']:
                    closest = min(day_x, key=lambda d: abs(day_x[d] - item['x']))
                    day_subjects[closest] = corrected
            if len(day_subjects) >= 2 and period <= 7:
                for day, subj in day_subjects.items():
                    timetable[day][period] = subj
                period += 1

    return timetable
