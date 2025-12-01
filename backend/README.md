# French Voice Agent - Backend

Backend voice agent for French appointment booking with Google Calendar integration.

## Features

- **Bilingual Support**: French primary, English secondary with automatic language detection
- **Google Calendar Integration**: Real-time availability checking and booking
- **Email Notifications**: Confirmation emails with .ics calendar attachments
- **Voice Pipeline**: Deepgram STT + OpenAI GPT-4o-mini + OpenAI TTS
- **LiveKit Integration**: Real-time voice streaming

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
# or with uv
uv sync
```

2. **Configure environment variables** (`.env`):
```bash
# OpenAI
OPENAI_API_KEY=your_key

# LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

# Deepgram
DEEPGRAM_API_KEY=your_key

# Google Calendar
GOOGLE_CREDENTIALS_FILE=./google_credential.json
GOOGLE_CALENDAR_ID=primary

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com

# Business
BUSINESS_NAME="Cabinet Médical Dr. Martin"
BUSINESS_HOURS="09:00-17:00"
APPOINTMENT_DURATION=30
```

3. **Setup Google Calendar**:
   - Create service account in Google Cloud Console
   - Enable Calendar API
   - Download credentials as `google_credential.json`
   - Share calendar with service account email

## Running Locally

```bash
python agent.py dev
```

## Deploying to LiveKit Cloud

```bash
lk agent deploy
```

## Agent Functions

- `check_availability(date, time)` - Check if time slot is available
- `get_available_slots(date)` - Get all available slots for a date
- `book_appointment(name, email, phone, date, time, service)` - Book appointment
- `get_current_date()` - Get current date and time

## Language Support

The agent automatically detects and responds in the user's language:
- **French**: Primary language, used for initial greeting
- **English**: Secondary language, switches automatically if user speaks English

## Email Notifications

Users receive:
1. HTML formatted confirmation email
2. .ics calendar file attachment (compatible with all calendar apps)

## Architecture

```
agent.py
├── CalendarManager (Google Calendar integration)
│   ├── check_availability()
│   ├── get_available_slots()
│   ├── book_appointment()
│   └── send_email_confirmation()
└── FrenchMedicalAgent (Voice agent)
    ├── Function tools for booking
    └── Bilingual instructions
```
