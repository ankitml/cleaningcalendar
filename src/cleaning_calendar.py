from parse_source import parse
from jinja2 import Template
import datetime
import source
import time
import gcal

URL = 'https://docs.google.com/spreadsheets/d/1J6B-dp2syrz_uQIy0BvyxKas8InCUWXG4Fn9hKeMRZI/edit?usp=sharing'

def get_source_data():
    _, data = source.convert_to_dict(source.get_csv_data(URL))
    return data


def construct_description(tasks):
    template = Template("<h4>Tasks</h4><ul> {% for task in tasks %} <li>{{ task }}</li> {% endfor %} </ul>")
    return template.render(tasks=tasks)

def run():
    source_data = get_source_data()
    data = parse(source_data)
    start_date = list(data.keys())[0]
    # data is in dict with key as date and list of tasks as values
    calendar = gcal.GoogleCalendar(365, start_date)
    calendar_event = calendar.create_reoccuring_event()
    all_cal_instances = calendar.get_all_instances_of_reoccuring_event(calendar_event)
    for i, instance in enumerate(all_cal_instances):
        time.sleep(.5)
        instance_date = datetime.datetime.strptime(
            instance['start']['dateTime'][0:10],
            '%Y-%m-%d'
        )
        date_tuple = instance_date.year, instance_date.month, instance_date.day
        description = construct_description(data.get(date_tuple))
        calendar.modify_single_instance_description(
            instance,
            description,
        )


if __name__ == '__main__':
    run()

