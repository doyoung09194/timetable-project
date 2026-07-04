import difflib
from config import SUBJECTS, ABBR_MAP

def correct_subject(raw_name):
    if raw_name in ABBR_MAP:
        return ABBR_MAP[raw_name]
    result = difflib.get_close_matches(raw_name, SUBJECTS, n=1, cutoff=0.6)
    if result:
        return result[0]
    return raw_name