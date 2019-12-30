"""
1. Read template from google sheets. Make list of tasks and its frequencies. 
"""
import requests
import io
import csv

def get_csv_data(url):
    url = url.replace('edit?usp=sharing', '') + 'export?format=csv'
    response = requests.get(url=url)
    return response.text


def convert_to_dict(csv_string):
    reader = csv.DictReader(io.StringIO(csv_string))
    return tuple(reader.fieldnames), [dict(row) for row in reader]


