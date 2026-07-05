from icalendar import Calendar, Event
from datetime import datetime, timedelta, date
from config import DAY_MAP

DAYS_ORDER = ["월", "화", "수", "목", "금"]

def generate_ics(timetable, start_date):
    cal = Calendar()
    cal.add('prodid', '-//학교 시간표//KR')
    cal.add('version', '2.0')

    monday = start_date - timedelta(days=start_date.weekday())

    for day_kr, periods in timetable.items():
        if day_kr not in DAYS_ORDER:
            continue
        day_offset = DAYS_ORDER.index(day_kr)
        event_date = (monday + timedelta(days=day_offset)).date()

        for period, subject in periods.items():
            event = Event()
            event.add('summary', f"{period}교시 {subject}")
            event.add('dtstart', event_date)
            event.add('dtend', event_date + timedelta(days=1))
            event.add('rrule', {'freq': 'weekly'})
            cal.add_component(event)

    return cal.to_ical()
