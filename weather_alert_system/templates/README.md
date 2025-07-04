# Smart Event Alert System

A Flask app that checks your events, fetches weather forecasts, and sends SMS alerts for bad weather at outdoor events.

## Features
- Mock Google Calendar events (3 sample events)
- OpenWeatherMap API integration for weather data
- Twilio SMS alerts for bad weather at outdoor events
- Responsive frontend with event cards
- Real-time weather checking and alert system

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys:**
   Create a `.env` file in the root directory:
   ```
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
   TWILIO_SID=your_twilio_account_sid_here
   TWILIO_TOKEN=your_twilio_auth_token_here
   TO_PHONE=+1234567890
   FROM_PHONE=+1098765432
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   Visit [http://localhost:5000](http://localhost:5000)

## API Endpoints

- **GET /** - Main dashboard (renders index.html)
- **GET /check-events** - Returns JSON with events, weather, and alert status

## Project Structure

```
weather_alert_system/
├── app.py              # Main Flask application
├── config.py           # Configuration template
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Frontend template
└── static/
    ├── style.css      # Responsive CSS
    └── script.js      # Frontend JavaScript
```

## How It Works

1. **Mock Events**: 3 sample events (Team Lunch, Board Meeting, Evening Yoga)
2. **Weather Check**: For each event, calls OpenWeatherMap API
3. **SMS Alert**: If outdoor event + bad weather (Rain/Thunderstorm/Snow), sends Twilio SMS
4. **Frontend**: Displays events as cards with weather icons and status badges

## Configuration

- **OpenWeatherMap**: Get free API key at [openweathermap.org](https://openweathermap.org/api)
- **Twilio**: Sign up at [twilio.com](https://www.twilio.com) for SMS capabilities

## Notes

- Events are mocked for demo purposes
- SMS will only send with valid Twilio credentials
- Weather data is cached to avoid API rate limits
- Frontend is responsive and mobile-friendly

## License

MIT 