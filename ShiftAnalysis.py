from sys import argv
from icalendar import Calendar
from datetime import datetime
from typing import List
from statistics import mean

class WorkShift:
    def __init__(self, _start: datetime, _end: datetime):
        self.start = _start
        self.end = _end
    
    def GetDuration(self) -> float:
        SECONDS_IN_HOUR = 3600
        duration = self.end - self.start
        duration_in_s = duration.total_seconds()
        hours = duration_in_s / SECONDS_IN_HOUR
        return hours

def GetShiftsFromCalendar(path_to_calendar: str) -> List[WorkShift]:
    work_shifts = []
    source_file = open(path_to_calendar, 'rb')
    calendar = Calendar.from_ical(source_file.read())
    for component in calendar.walk():
        if component.name == 'VEVENT':
            start = component.decoded('dtstart')
            end = component.decoded('dtend')
            new_shift = WorkShift(start, end)
            work_shifts.append(new_shift)
    source_file.close()
    return work_shifts

def get_mean_shift_duration(shifts: List[WorkShift]) -> float:
    shift_durations = []
    for shift in shifts:
        shift_durations.append(shift.GetDuration())
    return mean(shift_durations)

def main():
    work_shifts = GetShiftsFromCalendar(argv[1])
    print("total shifts:", len(work_shifts))
    print("mean shift duration:", get_mean_shift_duration(work_shifts))

if __name__ == '__main__':
    main()