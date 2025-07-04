from flask import Flask, render_template, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from twilio.rest import Client

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Config placeholders
GOOGLE_CALENDAR_API_KEY = os.getenv('GOOGLE_CALENDAR_API_KEY', 'mock-key')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', 'demo-key')
TWILIO_SID = os.getenv('TWILIO_SID', 'demo-sid')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN', 'demo-token')
TO_PHONE = os.getenv('TO_PHONE', '+1234567890')
FROM_PHONE = os.getenv('FROM_PHONE', '+1098765432')

# Mock Google Calendar events
MOCK_EVENTS = [
    {
        'id': '1',
        'summary': 'Picnic in the Park',
        'start': {'dateTime': (datetime.now() + timedelta(hours=2)).isoformat()},
        'location': 'Central Park, New York, NY',
        'outdoor': True
    },
    {
        'id': '2',
        'summary': 'Indoor Chess Tournament',
        'start': {'dateTime': (datetime.now() + timedelta(hours=4)).isoformat()},
        'location': 'Chess Club, New York, NY',
        'outdoor': False
    },
    {
        'id': '3',
        'summary': 'Outdoor Yoga',
        'start': {'dateTime': (datetime.now() + timedelta(hours=6)).isoformat()},
        'location': 'Prospect Park, Brooklyn, NY',
        'outdoor': True
    }
]

# Simple local cache for weather responses
WEATHER_CACHE_FILE = 'weather_cache.json'
def load_weather_cache():
    if os.path.exists(WEATHER_CACHE_FILE):
        with open(WEATHER_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}
def save_weather_cache(cache):
    with open(WEATHER_CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_weather_forecast(location, event_time):
    cache = load_weather_cache()
    cache_key = f"{location}_{event_time[:13]}"  # hour granularity
    if cache_key in cache:
        return cache[cache_key]
    # Geocoding (mocked for now)
    if 'Central Park' in location:
        lat, lon = 40.785091, -73.968285
    elif 'Prospect Park' in location:
        lat, lon = 40.660204, -73.968956
    else:
        lat, lon = 40.712776, -74.005974  # Default: NYC
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    data = resp.json()
    # Find closest forecast
    event_dt = datetime.fromisoformat(event_time)
    closest = min(data['list'], key=lambda x: abs(datetime.fromtimestamp(x['dt']) - event_dt))
    cache[cache_key] = closest
    save_weather_cache(cache)
    return closest

def is_bad_weather(weather):
    if not weather:
        return False
    desc = weather['weather'][0]['main'].lower()
    wind = weather['wind']['speed']
    if 'rain' in desc or 'snow' in desc or wind > 10:
        return True
    return False

def send_sms_alert(event, weather):
    from requests.auth import HTTPBasicAuth
    msg = f"Alert: Bad weather expected for '{event['summary']}' at {event['location']}! Weather: {weather['weather'][0]['description']}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    data = {
        'To': TO_PHONE,
        'From': FROM_PHONE,
        'Body': msg
    }
    resp = requests.post(url, data=data, auth=HTTPBasicAuth(TWILIO_SID, TWILIO_TOKEN))
    return resp.status_code == 201 or resp.status_code == 200

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data['weather'][0]['main']
    return None

def send_sms(body):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(
            body=body,
            from_=FROM_PHONE,
            to=TO_PHONE
        )
        return True
    except Exception as e:
        print('Twilio error:', e)
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def api_events():
    checked = []
    for event in MOCK_EVENTS:
        event_time = event['start']['dateTime']
        location = event['location']
        if event.get('outdoor'):
            weather = get_weather_forecast(location, event_time)
            bad = is_bad_weather(weather)
            checked.append({'event': event, 'weather': weather, 'alerted': bad})
        else:
            checked.append({'event': event, 'weather': None, 'alerted': False})
    return {'checked': checked}

@app.route('/check-events')
def check_events():
    # Mock events
    events = [
        {
            "title": "Team Lunch",
            "time": (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:00:00'),
            "location": "Pune",
            "outdoor": True
        },
        {
            "title": "Board Meeting",
            "time": (datetime.now() + timedelta(hours=4)).strftime('%Y-%m-%dT%H:00:00'),
            "location": "Mumbai",
            "outdoor": False
        },
        {
            "title": "Evening Yoga",
            "time": (datetime.now() + timedelta(hours=6)).strftime('%Y-%m-%dT%H:00:00'),
            "location": "Delhi",
            "outdoor": True
        }
    ]
    result = []
    for event in events:
        weather = get_weather(event['location'])
        alert = False
        if event['outdoor'] and weather in ["Rain", "Thunderstorm", "Snow"]:
            sms_text = f"Alert! {weather} expected at your {event['time']} outdoor event: '{event['title']}'. Carry an umbrella!"
            alert = send_sms(sms_text)
        result.append({
            "title": event['title'],
            "time": event['time'],
            "location": event['location'],
            "outdoor": event['outdoor'],
            "weather": weather,
            "alertSent": alert
        })
    return jsonify(result)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True) 