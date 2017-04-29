import datetime, json
from urllib2 import Request
GMT_OFF = '-04:00'

def get_busy_time(events):
    now = datetime.datetime.now().isoformat()+GMT_OFF
    end_of_day = datetime.datetime.now().date().isoformat()+'T23:59:59.999999'+GMT_OFF
    busy_time = []
    for event in events:
        if event['start']['dateTime'] > now and \
            event['end']['dateTime'] < end_of_day:
            busy_time.append((event['start']['dateTime'], event['end']['dateTime']))

    return busy_time


def add_event(remote_app, access_token, start_time='0', end_time='0',
            summury=''):
    headers = {'Authorization': 'OAuth '+access_token}
    event = {
      "start": {
        "dateTime": "2017-04-15T06:30:00-04:00"
      },
      "end": {
        "dateTime": "2017-04-15T07:30:00-04:00"
      },
      "summary": "Event added by http POST method"
    }

    resp = remote_app.post('https://www.googleapis.com/calendar/v3/calendars/primary/events',
                  data=event, format='json', method='POST', headers=headers)
                #   , method='POST', headers=headers)
    print "Add event HTTP code:", resp.status
    return None

def cal_format_time(time):
    return time.split('.')[0]+GMT_OFF
