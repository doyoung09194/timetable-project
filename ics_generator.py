from datetime import datetime, timedelta, date, timezone
import uuid

DAYS_ORDER = ["월", "화", "수", "목", "금"]

def _fold(line):
    """RFC 5545: 75옥텟 이상이면 CRLF+공백으로 줄바꿈"""
    encoded = line.encode('utf-8')
    if len(encoded) <= 75:
        return line + '\r\n'
    result = []
    while len(encoded) > 75:
        chunk = encoded[:75].decode('utf-8', errors='ignore')
        result.append(chunk)
        encoded = encoded[75:]
    result.append(encoded.decode('utf-8'))
    return '\r\n '.join(result) + '\r\n'

def generate_ics(timetable, start_date, end_date=None):
    lines = []
    lines.append('BEGIN:VCALENDAR\r\n')
    lines.append('VERSION:2.0\r\n')
    lines.append('PRODID:-//School Timetable//EN\r\n')
    lines.append('CALSCALE:GREGORIAN\r\n')
    lines.append('METHOD:PUBLISH\r\n')
    lines.append('X-WR-CALNAME:학교 시간표\r\n')

    monday = start_date - timedelta(days=start_date.weekday())
    now = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    until_str = ''
    if end_date:
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        until_str = ';UNTIL=' + end_date.strftime('%Y%m%d')

    for day_kr in DAYS_ORDER:
        if day_kr not in timetable:
            continue
        periods = timetable[day_kr]
        day_offset = DAYS_ORDER.index(day_kr)
        event_date = (monday + timedelta(days=day_offset)).date()
        dtstart = event_date.strftime('%Y%m%d')
        dtend = (event_date + timedelta(days=1)).strftime('%Y%m%d')

        for period in sorted(periods.keys()):
            subject = periods[period]
            uid = str(uuid.uuid4()) + '@timetable'
            summary = f'{period}교시 {subject}'

            lines.append('BEGIN:VEVENT\r\n')
            lines.append(f'UID:{uid}\r\n')
            lines.append(f'DTSTAMP:{now}\r\n')
            lines.append(f'DTSTART;VALUE=DATE:{dtstart}\r\n')
            lines.append(f'DTEND;VALUE=DATE:{dtend}\r\n')
            lines.append(_fold(f'SUMMARY:{summary}'))
            lines.append(f'RRULE:FREQ=WEEKLY{until_str}\r\n')
            lines.append('END:VEVENT\r\n')

    lines.append('END:VCALENDAR\r\n')
    return ''.join(lines).encode('utf-8')
