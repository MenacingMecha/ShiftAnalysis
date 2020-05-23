from sys import argv
from icalendar import Calendar
from datetime import datetime, date
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
        #print("day:", self.start.day)
        return hours

class WorkDay:
    def __init__(self, _date: date, _shifts: List[WorkShift]):
        self.date = _date
        self.shifts = _shifts
    
    def get_duration(self) -> float:
        duration = 0
        for shift in self.shifts:
            duration += shift.GetDuration()
        return duration

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

def get_work_days_from_shifts(shifts: List[WorkShift]) -> List[WorkDay]:
    workday_values = {}
    for shift in shifts:
        date = shift.start.date()
        #print("date of shift:", date)
        #print("duration of shift", shift.GetDuration())
        if date not in workday_values:
            shifts_in_day = []
            workday_values[date] = shifts_in_day
        workday_values[date].append(shift)
    workdays = []
    for key in workday_values:
        workday = WorkDay(key, workday_values[key])
        workdays.append(workday)
    return workdays

def get_mean_shift_duration(shifts: List[WorkShift]) -> float:
    shift_durations = []
    for shift in shifts:
        shift_durations.append(shift.GetDuration())
    return mean(shift_durations)

def get_mean_day_duration(work_days: List[WorkDay]) -> float:
    work_day_durations = []
    for day in work_days:
        work_day_durations.append(day.get_duration())
    return mean(work_day_durations)

def main():
    # catch error if no args passed
    work_shifts = GetShiftsFromCalendar(argv[1])
    print("total shifts:", len(work_shifts))
    print("mean shift duration:", get_mean_shift_duration(work_shifts))
    work_days = get_work_days_from_shifts(work_shifts)
    print("work days:", len(work_days))
    print("average work day duration:", get_mean_day_duration(work_days))

if __name__ == '__main__':
    main()