from icalendar import Calendar, Event, vDate, vDatetime
from datetime import datetime, timedelta, date, timezone
from config import DAY_MAP
import uuid

DAYS_ORDER = ["월", "화", "수", "목", "금"]

def generate_ics(timetable, start_date, end_date=None):
    cal = Calendar()
    cal.add('prodid', '-//학교 시간표//KR')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')

    monday = start_date - timedelta(days=start_date.weekday())
    now = datetime.now(timezone.utc)

    # UNTIL: dtstart가 DATE이면 UNTIL도 반드시 DATE여야 함 (RFC 5545)
    rrule = {'freq': 'weekly'}
    if end_date:
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        rrule['until'] = end_date  # date 객체 그대로 전달

    for day_kr, periods in timetable.items():
        if day_kr not in DAYS_ORDER:
            continue
        day_offset = DAYS_ORDER.index(day_kr)
        event_date = (monday + timedelta(days=day_offset)).date()

        for period, subject in sorted(periods.items()):
            event = Event()
            event.add('uid', str(uuid.uuid4()) + '@timetable')
            event.add('dtstamp', now)
            event.add('summary', f"{period}교시 {subject}")
            event.add('dtstart', event_date)
            event.add('dtend', event_date + timedelta(days=1))
            event.add('rrule', rrule)
            cal.add_component(event)

    return cal.to_ical()
