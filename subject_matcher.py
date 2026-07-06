import difflib
from config import SUBJECTS, ABBR_MAP

def correct_subject(raw_name):
    if len(raw_name) < 2:
        return raw_name
    # 1. 정확한 매칭
    if raw_name in ABBR_MAP:
        return ABBR_MAP[raw_name]
    # 2. 접두사 매칭
    for abbr, full in ABBR_MAP.items():
        if raw_name.startswith(abbr):
            return full
    # 3. 유사도 매칭 (3글자 이상만)
    if len(raw_name) >= 3:
        all_keys = list(ABBR_MAP.keys()) + SUBJECTS
        result = difflib.get_close_matches(raw_name, all_keys, n=1, cutoff=0.65)
        if result:
            r = result[0]
            if r in ABBR_MAP:
                return ABBR_MAP[r]
            return r
    return raw_name
