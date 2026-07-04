from icalendar import Calendar, Event
from datetime import datetime, timedelta
from config import PERIOD_TIMES, DAY_MAP

def generate_ics(timetable, start_date):
    cal = Calendar()
    cal.add('prodid', '-//학교 시간표//KR')
    cal.add('version', '2.0')

    for day_kr, periods in timetable.items():
        day_en = DAY_MAP.get(day_kr)
        if not day_en:
            continue
        for period, subject in periods.items():
            times = PERIOD_TIMES.get(period)
            if not times:
                continue

            event = Event()
            event.add('summary', subject)

            start_h, start_m = map(int, times['start'].split(':'))
            end_h, end_m = map(int, times['end'].split(':'))

            event_start = start_date + timedelta(days=DAYS_ORDER.index(day_kr))
            event.add('dtstart', event_start.replace(hour=start_h, minute=start_m))
            event.add('dtstart', event_start.date())
            event.add('dtend', (event_start + timedelta(days=1)).date())

            cal.add_component(event)

    return cal.to_ical()

DAYS_ORDER = ["월", "화", "수", "목", "금"]