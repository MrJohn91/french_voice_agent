"""
English Voice Agent - Complete Standalone Appointment Booking System
"""
import asyncio
import logging
import os
import datetime
import smtplib
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RunContext, WorkerOptions, cli, JobProcess
from livekit.agents.llm import function_tool
from livekit.plugins import deepgram, openai, silero

# Google Calendar imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
class Settings:
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")
    GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE")
    GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Dr. Martin Medical Office")
    BUSINESS_HOURS = os.getenv("BUSINESS_HOURS", "09:00-17:00")
    APPOINTMENT_DURATION = int(os.getenv("APPOINTMENT_DURATION", "30"))
    
    # Email settings (optional)
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL", os.getenv("SMTP_USERNAME", ""))

settings = Settings()

class CalendarManager:
    """Google Calendar integration for appointment booking"""
    
    def __init__(self):
        self.service = None
        self.calendar_id = settings.GOOGLE_CALENDAR_ID
        
    async def initialize(self):
        """Initialize Google Calendar service"""
        if not GOOGLE_AVAILABLE:
            logger.warning("Google Calendar libraries not available")
            return False
            
        try:
            if settings.GOOGLE_CREDENTIALS_FILE and os.path.exists(settings.GOOGLE_CREDENTIALS_FILE):
                creds = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_CREDENTIALS_FILE,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
                self.service = build('calendar', 'v3', credentials=creds)
                logger.info("Google Calendar service initialized successfully")
                return True
            else:
                logger.warning("Google Calendar credentials file not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar: {e}")
            return False

    async def check_availability(self, date: str, time: str) -> Dict[str, Any]:
        """Check if a specific date/time slot is available"""
        try:
            if not self.service:
                return {
                    "available": True,
                    "message": f"The slot on {date} at {time} is available! (Demo mode - calendar not configured)"
                }
            
            # Parse date and time
            start_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + datetime.timedelta(minutes=settings.APPOINTMENT_DURATION)
            
            # Convert to RFC3339 format for Google Calendar API
            start_time = start_datetime.isoformat() + 'Z'
            end_time = end_datetime.isoformat() + 'Z'
            
            # Query for existing events
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if events:
                return {
                    "available": False,
                    "message": f"Sorry, that time slot is not available. There are {len(events)} appointments already scheduled."
                }
            else:
                return {
                    "available": True,
                    "message": f"Perfect! The slot on {date} at {time} is available."
                }
                
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {
                "available": True,
                "message": f"The slot on {date} at {time} appears available. (Unable to verify - {str(e)})"
            }

    async def get_available_slots(self, date: str) -> Dict[str, Any]:
        """Get all available time slots for a specific date"""
        try:
            if not self.service:
                return {
                    "slots": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"],
                    "message": f"Available slots for {date}: 09:00, 09:30, 10:00, 10:30, 11:00, 11:30, 14:00, 14:30, 15:00, 15:30, 16:00, 16:30 (Demo mode)"
                }
            
            # Parse business hours
            start_hour, end_hour = settings.BUSINESS_HOURS.split('-')
            start_hour = int(start_hour.split(':')[0])
            end_hour = int(end_hour.split(':')[0])
            
            # Generate all possible slots
            all_slots = []
            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:  # 30-minute intervals
                    if hour == end_hour - 1 and minute == 30:
                        break  # Don't go past business hours
                    all_slots.append(f"{hour:02d}:{minute:02d}")
            
            # Check each slot for availability
            available_slots = []
            for time_slot in all_slots:
                availability = await self.check_availability(date, time_slot)
                if availability["available"]:
                    available_slots.append(time_slot)
            
            slots_text = ", ".join(available_slots) if available_slots else "No slots available"
            return {
                "slots": available_slots,
                "message": f"Available slots for {date}: {slots_text}"
            }
            
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return {
                "slots": ["09:00", "10:30", "14:00", "15:30"],
                "message": f"Available slots for {date}: 09:00, 10:30, 14:00, 15:30 (Error checking calendar: {str(e)})"
            }

    async def book_appointment(
        self, 
        name: str, 
        email: str, 
        phone: str,
        date: str, 
        time: str, 
        service: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Book a new appointment"""
        try:
            if not self.service:
                return {
                    "success": True,
                    "message": f"Perfect! I've booked your {service} appointment for {date} at {time}. You'll receive a confirmation email at {email}. (Demo mode - not actually booked)"
                }
            
            # Check availability first
            availability = await self.check_availability(date, time)
            if not availability["available"]:
                return {
                    "success": False,
                    "message": availability["message"]
                }
            
            # Create event
            start_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + datetime.timedelta(minutes=settings.APPOINTMENT_DURATION)
            
            event = {
                'summary': f'{service} - {name}',
                'description': f"""Appointment with {name}
Service: {service}
Phone: {phone}
Email: {email}
""" + (f"Notes: {notes}" if notes else ""),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(), 
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24h before
                        {'method': 'popup', 'minutes': 30},        # 30min before
                    ],
                },
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event,
                sendUpdates='none'  # Don't send via Google (we send custom email)
            ).execute()
            
            # Send custom email confirmation if SMTP configured
            email_sent = await self.send_email_confirmation(name, email, date, time, service)
            email_status = " Email confirmation sent!" if email_sent else ""
            
            return {
                "success": True,
                "event_id": created_event['id'],
                "message": f"Perfect! Your {service} appointment is confirmed for {date} at {time}.{email_status} See you then!"
            }
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Sorry, I couldn't book that appointment. Please try again or contact us directly."
            }

    async def send_email_confirmation(self, name: str, email: str, date: str, time: str, service: str) -> bool:
        """Send email confirmation with calendar attachment"""
        try:
            if not all([settings.SMTP_SERVER, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
                logger.info("Email not configured - skipping email confirmation")
                return False
                
            msg = MIMEMultipart('mixed')
            msg['Subject'] = f"Appointment Confirmation - {settings.BUSINESS_NAME}"
            msg['From'] = settings.FROM_EMAIL
            msg['To'] = email
            
            # Create email content
            text_content = f"""
Dear {name},

Your appointment has been confirmed!

Details:
- Date: {date}
- Time: {time}
- Service: {service}
- Location: {settings.BUSINESS_NAME}

If you need to reschedule or cancel, please contact us as soon as possible.

Thank you!
{settings.BUSINESS_NAME}
"""
            
            html_content = f"""
<html>
<body>
<h2>Appointment Confirmation</h2>
<p>Dear {name},</p>
<p>Your appointment has been confirmed!</p>
<h3>Details:</h3>
<ul>
<li><strong>Date:</strong> {date}</li>
<li><strong>Time:</strong> {time}</li>
<li><strong>Service:</strong> {service}</li>
<li><strong>Location:</strong> {settings.BUSINESS_NAME}</li>
</ul>
<p>If you need to reschedule or cancel, please contact us as soon as possible.</p>
<p>Thank you!<br>{settings.BUSINESS_NAME}</p>
</body>
</html>
"""
            
            msg_alt = MIMEMultipart('alternative')
            msg_alt.attach(MIMEText(text_content, 'plain'))
            msg_alt.attach(MIMEText(html_content, 'html'))
            msg.attach(msg_alt)
            
            # Create .ics calendar file
            start_dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + datetime.timedelta(minutes=settings.APPOINTMENT_DURATION)
            
            ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//{settings.BUSINESS_NAME}//Appointment//EN
BEGIN:VEVENT
UID:{start_dt.strftime('%Y%m%d%H%M%S')}@{settings.BUSINESS_NAME.replace(' ', '')}
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{service} - {settings.BUSINESS_NAME}
DESCRIPTION:Appointment for {service}
LOCATION:{settings.BUSINESS_NAME}
STATUS:CONFIRMED
BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
DESCRIPTION:Reminder: Appointment tomorrow
END:VALARM
END:VEVENT
END:VCALENDAR"""
            
            ics_part = MIMEBase('text', 'calendar', method='REQUEST', name='appointment.ics')
            ics_part.set_payload(ics_content.encode('utf-8'))
            encoders.encode_base64(ics_part)
            ics_part.add_header('Content-Disposition', 'attachment', filename='appointment.ics')
            msg.attach(ics_part)
            
            # Send email
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Confirmation email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email confirmation: {e}")
            return False

def prewarm(proc: JobProcess):
    """Prewarm VAD model for faster startup."""
    proc.userdata["vad"] = silero.VAD.load()

# Global calendar manager instance
calendar_manager = CalendarManager()

class FrenchMedicalAgent(Agent):
    """French Medical Appointment Agent"""

    def __init__(self):
        super().__init__(
            instructions=f"""You are Alex, a professional appointment scheduling specialist for {settings.BUSINESS_NAME}.

IMPORTANT: The current date is December 1, 2025. Use get_current_date() to get the exact current date and time when needed.

Help users schedule appointments by collecting: name, email, phone, date, time, and service type.

Process:
1. When discussing dates, first call get_current_date() to get the current date
2. Use check_availability to verify time slots are available
3. Use get_available_slots to show available times for a date
4. When booking, collect all required information then use book_appointment to create the appointment with email confirmations

Be friendly, professional, and thorough in collecting patient information.
Always confirm all details before booking.
Respond in English."""
        )

    @function_tool
    async def check_availability(
        self,
        context: RunContext,
        date: str,
        time: str
    ) -> str:
        """Check if an appointment slot is available (date: YYYY-MM-DD, time: HH:MM)"""
        logger.info(f"Checking availability for {date} at {time}")
        result = await calendar_manager.check_availability(date, time)
        return result["message"]

    @function_tool
    async def get_available_slots(
        self,
        context: RunContext,
        date: str
    ) -> str:
        """Get available appointment slots for a date (date: YYYY-MM-DD)"""
        logger.info(f"Getting available slots for {date}")
        result = await calendar_manager.get_available_slots(date)
        return result["message"]

    @function_tool
    async def book_appointment(
        self,
        context: RunContext,
        name: str,
        email: str,
        phone: str,
        date: str,
        time: str,
        service: str,
        notes: str = ""
    ) -> str:
        """Book an appointment with all patient details"""
        logger.info(f"Booking appointment for {name} on {date} at {time}")
        result = await calendar_manager.book_appointment(name, email, phone, date, time, service, notes)
        return result["message"]

    @function_tool
    async def get_current_date(
        self,
        context: RunContext
    ) -> str:
        """Get the current date and time to help with appointment scheduling"""
        from datetime import datetime
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")
        return f"Today is {current_date}. The current time is {current_time}."

    async def on_enter(self):
        """Called when agent becomes active in the conversation."""
        logger.info("French Medical Agent session started")
        
        # Initialize calendar
        await calendar_manager.initialize()

        # Generate initial greeting
        await self.session.generate_reply(
            instructions="""Give a friendly and professional greeting exactly like this:
            "Hello! Welcome to Dr. Martin Medical Office. I'm Alex, your scheduling specialist. I can check appointment availability, show you open time slots, and book your appointments with email confirmations. How can I help you today?"

            Keep it warm and professional."""
        )

async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the voice agent"""
    
    logger.info(f"French Medical Agent started in room: {ctx.room.name}")

    # Configure the voice pipeline
    session = AgentSession(
        # Speech-to-Text - Deepgram for English
        stt=deepgram.STT(
            model="nova-2",
            language="en-US",
        ),

        # Large Language Model - GPT-4o-mini
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
        ),

        # Text-to-Speech - OpenAI
        tts=openai.TTS(
            voice="alloy",
        ),

        # Voice Activity Detection
        vad=silero.VAD.load(),
    )

    # Start agent session
    await session.start(
        room=ctx.room,
        agent=FrenchMedicalAgent()
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm
    ))