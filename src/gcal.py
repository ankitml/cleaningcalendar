import datetime
import time
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleCalendar:

    def get_template(self, n_days):
        return {
          'summary': "Today's cleaning tasks",
          'start': {
            'dateTime': datetime.datetime.strftime(
                self.start_date,
                '%Y-%m-%dT%H:%M:%S-04:00'
            ),
            'timeZone': 'America/Toronto',
          },
          'end': {
            'dateTime': datetime.datetime.strftime(
                self.start_date + datetime.timedelta(hours=1),
                '%Y-%m-%dT%H:%M:%S-04:00'
            ),
            'timeZone': 'America/Toronto',
          },
          'recurrence': [
            f'RRULE:FREQ=DAILY;COUNT={n_days}'
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

    def __init__(self, n_days, start_date):
        self.creds = None
        self.start_date = datetime.datetime(*start_date, 9)
        self.scopes = ['https://www.googleapis.com/auth/calendar.events']
        self.login()
        self.service = build('calendar', 'v3', credentials=self.creds)
        self.template = self.get_template(n_days)

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
                    'credentials.json', self.scopes)
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
            body=self.template,
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
