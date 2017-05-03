from bs4 import BeautifulSoup
from collections import defaultdict
import requests, lxml.html, re, json
import time, datetime


def table_to_list(table):
    dct = table_to_2d_dict(table)
    return list(iter_2d_dict(dct))


def table_to_2d_dict(table):
    result = defaultdict(lambda: defaultdict(str))
    for row_i, row in enumerate(table.xpath('./tr')):
        for col_i, col in enumerate(row.xpath('./td|./th')):
            colspan = int(col.get('colspan', 1))
            rowspan = int(col.get('rowspan', 1))
            col_data = lxml.etree.tostring(col)
            while row_i in result and col_i in result[row_i]:
                col_i += 1
            for i in range(row_i, row_i + rowspan):
                for j in range(col_i, col_i + colspan):
                    result[i][j] = col_data
    return result


def iter_2d_dict(dct):
    for i, row in sorted(dct.items()):
        cols = []
        for j, col in sorted(row.items()):
            cols.append(col)
        yield cols


resp = requests.get(
    'http://timetables.cit.ie:70/reporting/Individual;Student+Set;name;CO.DCOM2-B?weeks=3-15&days=1-5&periods=1-40&height=100&width=100')
soup = BeautifulSoup(resp.text, 'html.parser')
class_timetables = soup.find_all('table', {'cellspacing': '0', 'border': '1'})

if len(class_timetables) > 1:
    print('I don\'t support more than one table at once yet.')
    quit()

class_timetable_html = str(class_timetables[0])
class_timetable_etree = lxml.etree.fromstring(class_timetable_html)
class_timetable_list = table_to_list(class_timetable_etree)

events = []
for class_timetable_row in class_timetable_list[1:]:
    _time = BeautifulSoup(class_timetable_row[0], 'html.parser').text.strip()
    for class_event_index, class_event in enumerate(class_timetable_row):
        if class_event_index == 0:
            continue

        day = BeautifulSoup(class_timetable_list[0][class_event_index], 'html.parser').text.strip()
        class_event_info = BeautifulSoup(class_event, 'html.parser').text.strip()
        class_event_info = re.sub('\n+', '\n', class_event_info).split('\n')

        if len(class_event_info) < 3:
            continue

        class_date_range = re.sub('([A-Za-z])(\d)', r'\1 \2', class_event_info[2].replace('wk', '')).split('-')
        class_event_dict = {'subject_name': class_event_info[0], 'room_number': class_event_info[1],
                            'date_start': class_date_range[0], 'date_end': class_date_range[1]}
        events.append({'day': day, 'time': _time, 'details': class_event_dict})

sorted_events_original = sorted(events, key=lambda k: k['day'])
sorted_events_new = []
for event_index, current_event in enumerate(sorted_events_original):
    is_final_event = (event_index == len(sorted_events_original) - 1)
    if is_final_event:
        next_event = {'details': None}
    else:
        next_event = sorted_events_original[event_index + 1]
    if next_event['details'] == current_event['details']:
        if not 'time_start' in current_event:
            current_event['time_start'] = current_event['time']
        next_event['time_start'] = current_event['time_start']
    else:
        current_event['time_end'] = (
        datetime.datetime.strptime(current_event.pop('time'), '%H:%M') + datetime.timedelta(minutes=15)).strftime(
            '%H:%M')
        sorted_events_new.append(current_event)

print(json.dumps(sorted_events_new, indent=4))