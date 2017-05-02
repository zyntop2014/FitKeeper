from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

GMT_OFF = '-04:00'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
CAL_SCOPES = 'https://www.googleapis.com/auth/calendar'; # Read & Write
CLIENT_SECRET_FILE = 'client_secret.json'

APPLICATION_NAME = 'Google Calendar API Python Quickstart'



def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('.')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, CAL_SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    else:
        print("Successfully get credentials")
    return credentials


def get_cal_service():
    """
    Get a Google Calendar service.
    Return:
        service: An object of Google Calendar service
    """
    # credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('calendar', 'v3', http=http)


def get_all_events(service):
    """
    Read user's Google Calendar,
    get all events (including their start time and end time)
    listed on the calendar.
    """
    now = datetime.datetime.now().isoformat()+GMT_OFF
    endofday = datetime.datetime.now().date().isoformat()+'T23:59:59.999999'+GMT_OFF
    eventsResult = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax = endofday,
        singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    busy_timeslot = [] # Record

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        busy_timeslot.append((start, end))
    print(busy_timeslot)
    return busy_timeslot

# def read_events_test(service):



def add_events(service):
    """
    Add events on Google Calendar.
    """
    summary = 'Test adding events'  # summary of the event
    start_time = (datetime.datetime.now()+datetime.timedelta(hours=1)).isoformat()+GMT_OFF # start time, ISO format
    end_time = (datetime.datetime.now()+datetime.timedelta(hours=2)).isoformat()+GMT_OFF  # end time, ISO format

    event = {
        "summary": "%s" %(summary),
        "start": {"dateTime": "%s" %(start_time)},
        "end": {"dateTime": "%s" %(end_time)},
    }
    e = service.events().insert(calendarId='primary',
        body=event).execute()
    print ("Added an event to your calendar.")
    return None


def main():
    calendar = get_cal_service()
    add_events(calendar)
    busy_timeslot = get_all_events(calendar)
    print (busy_timeslot)


if __name__ == '__main__':
    main()
