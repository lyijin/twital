#!/usr/bin/env python3

"""
> generate_twital.py <

Python script parses Aranda Lab's Google Calendar, then generates the email
that should be sent out every Sunday to the Aranda Lab group.
"""
import datetime
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def parse_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')

def parse_datetime(datetime_string):
    return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S+03:00')

credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('calendar', 'v3', http=http)

# get dates for emails, and for parsing google calendar
today = datetime.date.today()

# python's default has weekdays starting on mondays. recalibrate it to sunday!
weekdays = (today.weekday() + 1) % 7
thisweek_sun = today - datetime.timedelta(days=weekdays)
thisweek_sat = thisweek_sun + datetime.timedelta(days=6)

# convert to ISO time, then query google calendar for events
thisweek_sun_iso = thisweek_sun.isoformat() + 'T00:00:00+03:00'
thisweek_sat_iso = thisweek_sat.isoformat() + 'T23:59:59+03:00'
events_results = service.events().list(
    calendarId='REDACTED@group.calendar.google.com',
    timeMin=thisweek_sun_iso,
    timeMax=thisweek_sat_iso,
    maxResults=20,
    singleEvents=True,
    orderBy='startTime').execute()
events = events_results['items']

# store output in "email_body", which is what will be sent out.
email_body = '''-- T H I S   W E E K   I N   T H E --------------------
  ___                      _         _           _     
 / _ \                    | |       | |         | |    
/ /_\ \_ __ __ _ _ __   __| | __ _  | |     __ _| |__  
|  _  | '__/ _` | '_ \ / _` |/ _` | | |    / _` | '_ \ 
| | | | | | (_| | | | | (_| | (_| | | |___| (_| | |_) |
\_| |_/_|  \__,_|_| |_|\__,_|\__,_| \_____/\__,_|_.__/ 
'''
date_string = 'Week ' + thisweek_sun.strftime('%U: %b %d - ') + \
              thisweek_sat.strftime('%b %d')
email_body += (51 - len(date_string)) * '-' + ' ' + date_string + ' --\n\n'

# header done, now parse events and print main body.
if not events:
    email_body += 'No upcoming events found.'
else:
    event_start = ''
    for event in events:
        # ignore events with no 'summary' tag -- probably stuff that has elapsed
        if 'summary' not in event: continue
        event_name = event['summary']
        
        event_descr = event_loc = event_end = ''
        prev_start = event_start
        if 'date' in event['start']:
            event_start = parse_date(event['start']['date'])
        else:
            event_start = parse_datetime(event['start']['dateTime'])
        
        # following stuff are optional fields
        if 'description' in event:
            event_descr = event['description'].strip()
        
        if 'location' in event:
            event_loc = event['location'].strip()
        
        if 'end' in event:
            if 'date' in event['end']:
                event_end = parse_date(event['end']['date'])
            else:
                event_end = parse_datetime(event['end']['dateTime'])
        
        # print stuff out
        if prev_start:
            if event_start.date() != prev_start.date():
                email_body += event_start.date().strftime('%A %b %d') + '\n'
        else:
            email_body += event_start.date().strftime('%A %b %d') + '\n'
        
        td = event_end - event_start 
        if td > datetime.timedelta(1):
            # if event ends a day after start, it's usually because the 
            # event is set as a whole day event. in that case, suppress
            # printing of the date. dates only get printed for multi-day
            # events, e.g. absences or workshops
            email_body += str(td.days) + ' days ~ '
        
        if event_start:
            if td < datetime.timedelta(1):
                email_body += event_start.time().strftime('%H:%M')
                        
        if event_end:
            if td < datetime.timedelta(1):
                email_body += ' to {} ~ '.format(event_end.time().strftime('%H:%M'))
        
        email_body += event_name
        if event_descr: email_body += ' ({})'.format(event_descr)
        if event_loc: email_body += ' @ {}'.format(event_loc)
        
        email_body += '\n\n'

with open('email_contents.txt', 'w') as f:
    print (email_body.strip(), file=f)
