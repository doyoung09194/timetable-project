from icalendar import Calendar, Event
from datetime import datetime, timedelta
from config import PERIOD_TIMES, DAY_MAP

DAYS_ORDER = ["월", "화", "수", "목", "금"]

def generate_ics(timetable, start_date):
    cal = Calendar()
    cal.add('prodid', '-//학교 시간표//KR')
    cal.add('version', '2.0')

    # 이번 주 월요일 기준
    monday = start_date - timedelta(days=start_date.weekday())

    for day_kr, periods in timetable.items():
        if day_kr not in DAYS_ORDER:
            continue
        day_offset = DAYS_ORDER.index(day_kr)
        event_date = monday + timedelta(days=day_offset)

        for period, subject in periods.items():
            times = PERIOD_TIMES.get(period)
            if not times:
                continue

            start_h, start_m = map(int, times['start'].split(':'))
            end_h, end_m = map(int, times['end'].split(':'))

            event = Event()
            event.add('summary', subject)
            event.add('dtstart', event_date.replace(hour=start_h, minute=start_m, second=0, microsecond=0))
            event.add('dtend', event_date.replace(hour=end_h, minute=end_m, second=0, microsecond=0))
            event.add('rrule', {'freq': 'weekly'})

            cal.add_component(event)

    return cal.to_ical()
