# Plan and documentation for personal webapp (MagicMirror):

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from random import randrange
from flask import Flask, send_file, render_template
import datetime
import requests
import json

framingham_lat = "42.27"
framingham_lon = "-71.41"
SERVICE = None
CAL_SERVICE = None
Pexel_API = ""
OW_API = ""

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/calendar.readonly']
ROUTINE_SPREADSHEET_ID = '1U9sXVoEhAfktntB6OKF39oTR82OC9942qYezCNsGC80'

app = Flask(__name__,
            static_url_path='',
            static_folder='resources/static',
            template_folder='resources/')
            
def get_API_keys():
    global Pexel_API, OW_API
    with open('resources/PexelAPI.txt', 'r') as key:
        Pexel_API = key.read()
    with open('resources/OW_API.txt', 'r') as key:
        OW_API = key.read()

def KtoF(kelvin_temp):
    return (kelvin_temp - 273.15) * (9.0/5) + 32

@app.route("/get_background")
def get_new_background_url():
    if Pexel_API == "":
        get_API_keys()
    # Based off API documentation at https://www.pexels.com/api/documentation/
    pexel_url = "https://api.pexels.com/v1/search?query=Mountains&per_page=1&page=" + str(randrange(1000))
    pexel_auth = {"Authorization" : Pexel_API}

    pexel = requests.get(pexel_url, headers=pexel_auth)
    pexel_resp = pexel.json()
    return json.dumps(pexel_resp['photos'][0]['src']['large2x'])

def get_weather_icon(icon_str):
    return "http://openweathermap.org/img/wn/{}.png".format(icon_str)

def get_hourly_weather(lat, lon):
    # Based off API documentation at https://openweathermap.org/api/one-call-api
    ow_url = "https://api.openweathermap.org/data/2.5/onecall?lat={0}&lon={1}&exclude=current,daily&appid={2}".format(lat, lon, OW_API)

    ow = requests.get(ow_url)
    ow_json = ow.json()
    interesting_info = [{"time": datetime.datetime.fromtimestamp(entry['dt']).strftime("%H:%M"), "temp": KtoF(entry['temp'])//1, "icon": get_weather_icon(entry['weather'][0]['icon'])} for entry in ow_json['hourly']]
    interesting_info[0]['icon'] = interesting_info[0]['icon'][:-4] + "@2x.png"
    return interesting_info

def get_workout_url():
    return "https://www.beachbodyondemand.com"

def get_daily_chores(service):
    day_column = chr(datetime.datetime.now().weekday() + ord("A"))
    sheet_range = "Sheet1!{0}2:{0}5".format(day_column)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ROUTINE_SPREADSHEET_ID, range=sheet_range).execute()
    values = result.get('values', [])

    return [val[0] for val in values]

def get_routine(service, routine_string):
    routine_to_column = {
        "evening" : "H",
        "morning" : "I",
        "daily" : "J"
    }
    sheet_range = "Sheet1!{0}2:{0}9".format(routine_to_column[routine_string])

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ROUTINE_SPREADSHEET_ID, range=sheet_range).execute()
    values = result.get('values', [])

    if not values:
        return []
    else:
        return values

def get_display_for_events(event_list):
    ad_events = []
    timed_events = []
    for ev in event_list:
        if ev['start'].get('date'):
            ad_events.append((None, ev['summary']))
        else:
            dt = ev['start'].get('dateTime')
            dt = datetime.datetime.strptime(dt[:-6], "%Y-%m-%dT%H:%M:%S")
            timed_events.append((dt, dt.strftime("%H:%M"), ev['summary']))

    # sort the lists
    ad_events.sort(key=lambda (x, y) : y)
    timed_events.sort(key=lambda (x, y, z): x)

    # concatenate and return what we want to display
    return [event for event in ad_events] + [(time, summ) for (dt, time, summ) in timed_events]

def get_daily_events(service):
    # Assume we are in Eastern TZ for ease
    now = datetime.datetime.now()
    today = now.replace(hour=0, minute=0, second=0).isoformat() + '-04:00'
    tomorrow = now.replace(day=now.day + 1, hour=0, minute=0, second=0).isoformat() + '-04:00'
   
    joe_events_results = service.events().list(calendarId='joemalone75@gmail.com', timeMin=today, timeMax=tomorrow, singleEvents=True, orderBy='startTime').execute()
    meg_events_results = service.events().list(calendarId='megmalone07@gmail.com', timeMin=today, timeMax=tomorrow, singleEvents=True, orderBy='startTime').execute()
    events = joe_events_results.get('items', []) + meg_events_results.get('items', [])

    return get_display_for_events(events)

def get_sheets_service():
    global SERVICE

    if not SERVICE:
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('resources/token.pickle'):
            with open('resources/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'resources/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('resources/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        SERVICE = build('sheets', 'v4', credentials=creds)

    return SERVICE

def get_calendar_service():
    global CAL_SERVICE

    if not CAL_SERVICE:
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('resources/cal_token.pickle'):
            with open('resources/cal_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'resources/cal_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('resources/cal_token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        CAL_SERVICE = build('calendar', 'v3', credentials=creds)

    return CAL_SERVICE

def get_website_string(chores, evening_routine, morning_routine, daily_reminders, background, hourly_weather):
    return send_file('resources/starting.html')

@app.route("/")
def main():
    service = get_sheets_service()
    cal_service = get_calendar_service()
    get_API_keys()

    weather_data = get_hourly_weather(framingham_lat, framingham_lon)
    data = {
        "chores" : get_daily_chores(service),
        "evening_routine" : get_routine(service, "evening"),
        "morning_routine" : get_routine(service, "morning"),
        "daily_reminders" : get_routine(service, "daily"),
        "events" : get_daily_events(cal_service),
        "cur_weather" : weather_data[0],
        "hourly_weather" : weather_data[1:13:3],
        "workout_location" : get_workout_url()
    }

    return render_template('starting.html', data=data)

@app.route("/css/main.css")
def get_css():
    return app.send_static_file('main.css')

@app.route("/js/main.js")
def get_js():
    return app.send_static_file('main.js')

@app.route("/css/fonts/SSP.ttf")
def get_SSP_font():
    return app.send_static_file('Source_Sans_Pro/SourceSansPro-ExtraLight.ttf')

@app.route("/get_weather")
def get_weather_section():
    hourly_weather = get_hourly_weather(framingham_lat, framingham_lon)
    data = {
        "cur_weather" : hourly_weather[0],
        "hourly_weather" : hourly_weather[1:13:3]
    }
    return json.dumps(render_template('weather_section.html', data=data))

if __name__ == '__main__':
    app.run(debug=True)
