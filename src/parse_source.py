import source
import datetime
import dateutil.relativedelta as rd
import dateutil.rrule as rr
from collections import defaultdict


def get_source_data():
    url = 'https://docs.google.com/spreadsheets/d/1J6B-dp2syrz_uQIy0BvyxKas8InCUWXG4Fn9hKeMRZI/edit?usp=sharing'
    _, data = source.convert_to_dict(source.get_csv_data(url))
    return data


def daily_dates():
    start_date = datetime.date.today()
    return rr.rrule(rr.DAILY, count=365, dtstart=start_date)

def alternate_day_dates():
    start_date = datetime.date.today()
    end_date = start_date + rd.relativedelta(days=365)
    return rr.rrule(rr.DAILY, interval=2, dtstart=start_date, until=end_date)

def weekly_dates():
    """
    Next 52 Fridays
    """
    start_date = datetime.date.today()
    return rr.rrule(
        rr.WEEKLY,
        dtstart=start_date,
        count=52,
        wkst=rr.SU,
        byweekday=(rr.FR),
    )


def fortnight_dates():
    """
    Alternate 26 Fridays
    """
    start_date = datetime.date.today()
    return rr.rrule(
        rr.WEEKLY,
        dtstart=start_date,
        count=26,
        interval=2,
        wkst=rr.SU,
        byweekday=(rr.FR),
    )

def monthly_dates():
    """
    4th friday of every month for next 12
    """
    start_date = datetime.date.today()
    return rr.rrule(rr.MONTHLY, dtstart=start_date, count=12, byweekday=(rr.FR(4)))


def seasonal_dates():
    start_date = datetime.date.today()
    return rr.rrule(
        rr.YEARLY,
        dtstart=start_date,
        count=1,
        byweekday=(rr.FR(4)),
        bymonth=(3, 6, 9, 12)
    )


def yearly_dates():
    """
    Final cleaning at end of the year
    """
    start_date = datetime.date.today()
    return rr.rrule(
        rr.YEARLY,
        dtstart=start_date,
        count=1,
        byweekday=(rr.FR(4)),
        bymonth=(12)
    )

DATES_FOR_FREQ = {
    'daily':daily_dates,
    'alternate_day': alternate_day_dates,
    'weekly': weekly_dates,
    'fortnightly':fortnight_dates,
    'monthly': monthly_dates,
    'yearly': yearly_dates,
    'season': seasonal_dates,
} # stores functions as values for frequency as keys. frequncy identifiers as keys

def guess_frequency_identifier(frequency):
    if frequency.lower() in ['daily', 'weekly', 'monthly', 'fortnightly', 'yearly']:
        return frequency.lower()
    if 'season' in frequency.lower():
        # once a season
        return 'season'
    if frequency.lower() in ['alternate days', 'alternate day']:
        return 'alternate_day'

    print(f"{frequency} isn't implemented well")
    return '-'


def date_to_tuple(date):
    return date.year, date.month, date.day


def convert_to_masterdict(data):
    # create empty master dict
    masterdict = defaultdict(list)
    for row in data:
        frequency = row['Frequency']
        task = row['Item']
        frequency_identifier = guess_frequency_identifier(frequency)
        dates_for_row = DATES_FOR_FREQ.get(
            frequency_identifier, lambda :list()
        )()
        for date in dates_for_row:
            masterdict[date_to_tuple(date)].append(task)
    return masterdict

def parse():
    return convert_to_masterdict(get_source_data())



if __name__ == '__main__':
    data = get_source_data()
    master_dict = convert_to_masterdict(data)
    for date, tasks in master_dict.items():
        print(f"{date} : {','.join(tasks)}")

"""
get data in the form of list of dicts. Convert it into a dictionary of lists,
with key as date tuple (yyyy, mm, dd) and
value as list of tasks to be done.
"""

