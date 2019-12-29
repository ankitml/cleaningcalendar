import datetime
import time
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleCalendar:

    EVENT_TEMPLATE = {
      'summary': "Today's cleaning tasks",
      'start': {
        'dateTime': '2020-01-01T09:00:00-07:00',
        'timeZone': 'America/Toronto',
      },
      'end': {
        'dateTime': '2020-01-01T10:00:00-07:00',
        'timeZone': 'America/Toronto',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=10'
      ],
      'attendees': [
        {'email': 'ankitmittaliitb@gmail.com'},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
        ],
      },
    }

    def __init__(self):
        self.creds = None
        self.scopes = ['https://www.googleapis.com/auth/calendar.events']
        self.login()
        self.service = build('calendar', 'v3', credentials=self.creds)

    def login(self):
        """
        login to google calendar
        """
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.creds = creds

    def create_reoccuring_event(self):
        """
        Create reoccuring event
        """
        event = self.service.events().insert(
            calendarId='primary',
            body=self.EVENT_TEMPLATE,
            sendUpdates='all',
            supportsAttachments=True,
        ).execute()
        return event

    def get_all_instances_of_reoccuring_event(self, event):
        page_token = None
        while True:
            events = self.service.events().instances(
                calendarId='primary',
                eventId=event['id'],
                pageToken=page_token
            ).execute()
            for e in events['items']:
                yield e
            page_token = events.get('nextPageToken')
            if not page_token:
                break

    def modify_single_instance_description(self, event_instance, description):
        body = {
            'description': description,
        }
        event = self.service.events().patch(
            calendarId='primary',
            eventId=event_instance['id'],
            body=body,
        ).execute()


if __name__ == '__main__':
    event = {'kind': 'calendar#event', 'etag': '"3155299049108000"', 'id': 'nar8j743rfc3g77biboi6vl9dc', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=bmFyOGo3NDNyZmMzZzc3Ymlib2k2dmw5ZGNfMjAyMDAxMDFUMTYwMDAwWiBhbmtpdG1sQG0', 'created': '2019-12-29T19:58:44.000Z', 'updated': '2019-12-29T19:58:44.689Z', 'summary': "Today's cleaning tasks", 'creator': {'email': 'ankitml@gmail.com', 'self': True}, 'organizer': {'email': 'ankitml@gmail.com', 'self': True}, 'start': {'dateTime': '2020-01-01T11:00:00-05:00', 'timeZone': 'America/Toronto'}, 'end': {'dateTime': '2020-01-01T12:00:00-05:00', 'timeZone': 'America/Toronto'}, 'recurrence': ['RRULE:FREQ=DAILY;COUNT=10'], 'iCalUID': 'nar8j743rfc3g77biboi6vl9dc@google.com', 'sequence': 0, 'attendees': [{'email': 'ankitmittaliitb@gmail.com', 'responseStatus': 'needsAction'}], 'reminders': {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 1440}]}}
    google_cal = GoogleCalendar()
    #event = google_cal.create_reoccuring_event()
    all_instances = google_cal.get_all_instances_of_reoccuring_event(event)
    for i, instance in enumerate(all_instances):
        time.sleep(.5)
        instance_date = datetime.datetime.strptime(
            instance['start']['dateTime'][0:10],
            '%Y-%m-%d'
        )
        date_tuple = instance_date.day, instance_date.month, instance_date.year
        google_cal.modify_single_instance_description(
            instance,
            f"This event is for date {date_tuple}"
        )
