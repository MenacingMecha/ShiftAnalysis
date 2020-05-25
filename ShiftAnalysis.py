import argparse
import datetime
import statistics
from typing import List, Dict
import icalendar

class WorkShift:
    """ A defined period of work time """

    def __init__(self, _start: datetime.datetime, _end: datetime.datetime, _is_crunch: bool):
        self.start = _start
        self.end = _end
        self.is_crunch = _is_crunch

    def GetDuration(self) -> float:
        SECONDS_IN_HOUR = 3600
        duration = self.end - self.start
        duration_in_s = duration.total_seconds()
        hours = duration_in_s / SECONDS_IN_HOUR
        return hours

class WorkDay:
    """ A collection of shifts across a given day """

    def __init__(self, _date: datetime.datetime.date, _shifts: List[WorkShift]):
        self.date = _date
        self.shifts = _shifts

    def get_duration(self) -> float:
        duration = 0
        for shift in self.shifts:
            duration += shift.GetDuration()
        return duration
    
    def has_crunch(self) -> bool:
        is_crunch = False
        for shift in self.shifts:
            if shift.is_crunch:
                is_crunch = True
                break
        return is_crunch

class WorkWeek:
    """ A collection of work days across a given week. Includes weekends for safety. """

    def __init__(self, weekId: int, workdays: Dict[int, WorkDay]):
        self.weekId = weekId
        self.workdays = workdays
    
    def get_duration(self) -> float:
        duration = 0.
        for workday in self.workdays:
            duration += workday.get_duration()
        return duration

class ShiftAnalysis:
    @staticmethod
    def get_mean_shift_duration(shifts: List[WorkShift]) -> float:
        shift_durations = []
        for shift in shifts:
            shift_durations.append(shift.GetDuration())
        return statistics.mean(shift_durations)

    @staticmethod
    def get_mean_day_duration(work_days: List[WorkDay]) -> float:
        work_day_durations = []
        for day in work_days:
            work_day_durations.append(day.get_duration())
        return statistics.mean(work_day_durations)

    @staticmethod
    def get_mean_week_duration(work_weeks: List[WorkWeek]) -> float:
        work_week_durations = []
        for week in work_weeks:
            work_week_durations.append(week.get_duration())
        return statistics.mean(work_week_durations)

    @staticmethod
    def get_crunch_days(workdays: List[WorkDay]) -> int:
        crunch_days = 0
        for workday in workdays:
            if workday.has_crunch():
                crunch_days += 1
        return crunch_days

class Error(Exception):
    def __init__(self, message:str):
        self.message = message

def get_shifts_from_calendar(path_to_calendar: str, shift_keyword_identifier: str,
        crunch_keyword_identifier: str) -> List[WorkShift]:
    work_shifts = []
    # TODO: refactor to 'with source_file open'
    source_file = open(path_to_calendar, 'rb')
    calendar = icalendar.Calendar.from_ical(source_file.read())
    for component in calendar.walk():
        if component.name == 'VEVENT':
            title = component.get('summary')
            if shift_keyword_identifier.casefold() in title.casefold():
                start = component.decoded('dtstart')
                end = component.decoded('dtend')
                is_crunch = crunch_keyword_identifier.casefold() in title.casefold()
                new_shift = WorkShift(start, end, is_crunch)
                work_shifts.append(new_shift)
    source_file.close()
    if len(work_shifts) < 1:
        raise Error("No work shifts found in " + path_to_calendar + " with the keyword '"
            + shift_keyword_identifier + "'!")
    return work_shifts

def get_work_days_from_shifts(shifts: List[WorkShift]) -> List[WorkDay]:
    """Converts a list of WorkShifts to a list of WorkDays"""

    # Construct unique key pairs of day/shifts
    workday_keypairs = {}
    for shift in shifts:
        date = shift.start.date()
        #print("date of shift:", date)
        #print("duration of shift", shift.GetDuration())
        if date not in workday_keypairs:
            shifts_in_day = []
            workday_keypairs[date] = shifts_in_day
        workday_keypairs[date].append(shift)
    # convert key pairs to WorkDay objects
    workday_objects = []
    for key in workday_keypairs:
        workday = WorkDay(key, workday_keypairs[key])
        workday_objects.append(workday)
    return workday_objects

def get_work_weeks_from_days(days: List[WorkDay]) -> List[WorkWeek]:
    """Converts a list of WorkDays to WorkWeeks"""

    workweek_keypairs = {}
    for day in days:
        isoweek = day.date.isocalendar()[1]
        if isoweek not in workweek_keypairs:
            workweek_keypairs[isoweek] = []
        workweek_keypairs[isoweek].append(day)
    workweek_objects = []
    for key in workweek_keypairs:
        workweek = WorkWeek(key, workweek_keypairs[key])
        workweek_objects.append(workweek)
    assert len(workweek_objects) > 0
    return workweek_objects

def print_duration_hours(summary:str, value:float, float_percision: int = 2):
    """Prints a duration value"""

    print(summary+":", str(round(value, float_percision))+"h")

def print_percentage(summary:str, value_a:int, value_b: int, float_percision: int = 2):
    """ Prints two values with their percentage difference"""

    print(summary+":", value_a, "/", value_b, "({:.0%})".format(value_a/value_b))

def parse_arguments() -> argparse.Namespace:
    """ Returns an argparse.Namespace (think struct) of parsed terminal arguments """

    argument_parser = argparse.ArgumentParser(description="Analyse work habits from ical calendar")
    argument_parser.add_argument('pathToIcs', help='path to the ical file to analyse')
    argument_parser.add_argument('-s', dest='shift_keyword', default='Shift',
        help='keyword for detirmining which events are shifts')
    argument_parser.add_argument('-c', dest='crunch_keyword', default='Crunch',
        help='keyword for detirmining which events are crunch shifts')
    return argument_parser.parse_args()

def main():
    arguments = parse_arguments()
    work_shifts = get_shifts_from_calendar(arguments.pathToIcs, arguments.shift_keyword,
        arguments.crunch_keyword)
    work_days = get_work_days_from_shifts(work_shifts)
    crunch_days = ShiftAnalysis.get_crunch_days(work_days)
    work_weeks = get_work_weeks_from_days(work_days)
    # for week in work_weeks:
    #     print("week duration:", week.get_duration())
    print("total shifts logged:", len(work_shifts))
    print_duration_hours("mean shift duration", ShiftAnalysis.get_mean_shift_duration(work_shifts))
    print_duration_hours("mean work day duration", ShiftAnalysis.get_mean_day_duration(work_days))
    print_duration_hours("mean work week duration", ShiftAnalysis.get_mean_week_duration(work_weeks))
    print_percentage("days with crunch", crunch_days, len(work_days))
    print("number of work weeks:", len(work_weeks))

if __name__ == '__main__':
    main()