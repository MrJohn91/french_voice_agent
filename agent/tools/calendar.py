import asyncio
import datetime
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
from config.settings import settings
from .notifications import notification_manager

logger = logging.getLogger(__name__)

class CalendarManager:
    """
    Google Calendar integration for appointment booking
    """
    
    def __init__(self):
        self.service = None
        self.calendar_id = settings.GOOGLE_CALENDAR_ID
        
    async def initialize(self):
        """Initialize Google Calendar service"""
        try:
            if settings.GOOGLE_CREDENTIALS_FILE:
                creds = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_CREDENTIALS_FILE,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
            else:
                # Use OAuth2 flow for user credentials
                creds = None
                if settings.GOOGLE_TOKEN_FILE:
                    creds = Credentials.from_authorized_user_file(
                        settings.GOOGLE_TOKEN_FILE,
                        ['https://www.googleapis.com/auth/calendar']
                    )
                    
                if not creds or not creds.valid:
                    logger.warning("Google Calendar credentials not available")
                    return False
                    
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar service initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar: {e}")
            return False

    async def check_availability(self, date: str, time: str) -> Dict[str, Any]:
        """
        Check if a specific date/time slot is available
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
        Returns:
            Dict with availability status and details
        """
        try:
            if not self.service:
                await self.initialize()
                
            if not self.service:
                return {
                    "available": False,
                    "error": "Calendar service not available",
                    "message": "Impossible de vérifier les disponibilités pour le moment."
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
                    "conflicting_events": len(events),
                    "message": f"Désolé, ce créneau n'est pas disponible. Il y a déjà {len(events)} rendez-vous à cette heure."
                }
            else:
                return {
                    "available": True,
                    "message": f"Parfait ! Le créneau du {date} à {time} est disponible."
                }
                
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {
                "available": False,
                "error": str(e),
                "message": "Impossible de vérifier les disponibilités. Veuillez réessayer."
            }

    async def get_available_slots(self, date: str) -> Dict[str, Any]:
        """
        Get all available time slots for a specific date
        Args:
            date: Date in YYYY-MM-DD format
        Returns:
            Dict with available slots
        """
        try:
            if not self.service:
                await self.initialize()
                
            if not self.service:
                return {
                    "slots": [],
                    "error": "Calendar service not available",
                    "message": "Impossible de récupérer les créneaux disponibles."
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
            
            return {
                "date": date,
                "slots": available_slots,
                "count": len(available_slots),
                "message": f"Il y a {len(available_slots)} créneaux disponibles le {date}."
            }
            
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return {
                "slots": [],
                "error": str(e),
                "message": "Impossible de récupérer les créneaux. Veuillez réessayer."
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
        """
        Book a new appointment
        Args:
            name: Patient name
            email: Patient email
            phone: Patient phone
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            service: Type of service/consultation
            notes: Optional notes
        Returns:
            Dict with booking confirmation details
        """
        try:
            if not self.service:
                await self.initialize()
                
            if not self.service:
                return {
                    "success": False,
                    "error": "Calendar service not available",
                    "message": "Impossible de réserver le rendez-vous pour le moment."
                }
            
            # Check availability first
            availability = await self.check_availability(date, time)
            if not availability["available"]:
                return {
                    "success": False,
                    "message": availability["message"],
                    "reason": "time_slot_unavailable"
                }
            
            # Create event
            start_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + datetime.timedelta(minutes=settings.APPOINTMENT_DURATION)
            
            event = {
                'summary': f'{service} - {name}',
                'description': f"""Rendez-vous avec {name}
Service: {service}
Téléphone: {phone}
Email: {email}
""" + (f"Notes: {notes}" if notes else ""),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(), 
                    'timeZone': 'Europe/Paris',
                },
                'attendees': [
                    {'email': email, 'displayName': name}
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24h before
                        {'method': 'popup', 'minutes': 30},        # 30min before
                    ],
                },
                'extendedProperties': {
                    'private': {
                        'patient_name': name,
                        'patient_phone': phone,
                        'service_type': service
                    }
                }
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=event,
                sendUpdates='all'  # Send email confirmations
            ).execute()
            
            # Send custom notifications (email + SMS)
            appointment_details = {
                "date": date,
                "time": time,
                "service": service,
                "duration": f"{settings.APPOINTMENT_DURATION} minutes",
                "notes": notes
            }
            
            # Send email confirmation
            email_result = await notification_manager.send_email_confirmation(
                email=email,
                name=name,
                appointment_details=appointment_details
            )
            
            # Send SMS confirmation (if phone number provided)
            sms_result = {"success": False, "message": "SMS non configuré"}
            if phone:
                sms_result = await notification_manager.send_sms_confirmation(
                    phone=phone,
                    name=name,
                    appointment_details=appointment_details
                )
            
            # Determine notification status
            notifications_sent = []
            if email_result["success"]:
                notifications_sent.append("email")
            if sms_result["success"]:
                notifications_sent.append("SMS")
            
            notification_message = ""
            if notifications_sent:
                notification_message = f" Confirmations envoyées par {' et '.join(notifications_sent)}."
            else:
                notification_message = " Rendez-vous créé (notifications à configurer)."
            
            return {
                "success": True,
                "event_id": created_event['id'],
                "event_link": created_event.get('htmlLink', ''),
                "message": f"Parfait ! Votre rendez-vous est confirmé le {date} à {time}.{notification_message}",
                "details": {
                    "name": name,
                    "date": date,
                    "time": time,
                    "service": service,
                    "duration": f"{settings.APPOINTMENT_DURATION} minutes"
                },
                "notifications": {
                    "email": email_result,
                    "sms": sms_result
                }
            }
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Désolé, impossible de réserver ce rendez-vous. Veuillez réessayer."
            }

    async def cancel_appointment(self, event_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an existing appointment"""
        try:
            if not self.service:
                await self.initialize()
                
            if not self.service:
                return {
                    "success": False,
                    "message": "Service calendrier non disponible."
                }
            
            # Delete the event
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='all'  # Notify attendees
            ).execute()
            
            return {
                "success": True,
                "message": "Votre rendez-vous a été annulé avec succès. Vous recevrez une confirmation par email."
            }
            
        except Exception as e:
            logger.error(f"Error canceling appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Impossible d'annuler ce rendez-vous. Veuillez contacter notre équipe."
            }


# Global calendar manager instance
calendar_manager = CalendarManager()


# Function tools for the voice agent
async def check_availability_tool(date: str, time: str) -> str:
    """
    Check if appointment slot is available
    Args:
        date: Date in YYYY-MM-DD format (e.g., "2024-12-15")
        time: Time in HH:MM format (e.g., "14:30")
    """
    result = await calendar_manager.check_availability(date, time)
    return result["message"]


async def get_available_slots_tool(date: str) -> str:
    """
    Get available appointment slots for a date
    Args:
        date: Date in YYYY-MM-DD format (e.g., "2024-12-15")
    """
    result = await calendar_manager.get_available_slots(date)
    if result["slots"]:
        slots_text = ", ".join(result["slots"])
        return f"Créneaux disponibles le {date}: {slots_text}. Vous serez notifié par email et SMS lors de la réservation."
    else:
        return f"Aucun créneau disponible le {date}. Souhaitez-vous essayer une autre date ?"


async def book_appointment_tool(
    name: str, 
    email: str, 
    phone: str,
    date: str, 
    time: str, 
    service: str,
    notes: str = ""
) -> str:
    """
    Book a new appointment with automatic notifications
    Args:
        name: Full name of the patient
        email: Email address for confirmations
        phone: Phone number for SMS confirmations (format: +33123456789 or 0123456789)
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format
        service: Type of service/consultation
        notes: Optional additional notes
    """
    result = await calendar_manager.book_appointment(name, email, phone, date, time, service, notes)
    
    # Enhanced response with notification details
    base_message = result["message"]
    
    if result["success"] and "notifications" in result:
        notifications = result["notifications"]
        notification_details = []
        
        if notifications.get("email", {}).get("success"):
            notification_details.append(f"✉️ Email de confirmation envoyé à {email}")
        
        if notifications.get("sms", {}).get("success"):
            notification_details.append(f"📱 SMS de confirmation envoyé au {phone}")
        
        if notification_details:
            base_message += f"\n\nNotifications:\n" + "\n".join(notification_details)
            base_message += f"\n\n🔔 Vous recevrez également un rappel automatique 24h avant votre rendez-vous."
    
    return base_message


async def send_reminder_tool(email: str, phone: str, name: str, date: str, time: str, service: str) -> str:
    """
    Send appointment reminder to patient
    """
    appointment_details = {
        "date": date,
        "time": time,
        "service": service,
        "duration": f"{settings.APPOINTMENT_DURATION} minutes"
    }
    
    result = await notification_manager.send_reminder(email, phone, name, appointment_details)
    return result["message"]