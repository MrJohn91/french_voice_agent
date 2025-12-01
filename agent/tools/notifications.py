import asyncio
import smtplib
import logging
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import aiohttp
from config.settings import settings

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Handle email and SMS notifications for appointment confirmations
    """
    
    def __init__(self):
        # Email configuration
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL or settings.SMTP_USERNAME
        
        # SMS configuration (using Twilio)
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

    async def send_email_confirmation(
        self, 
        email: str, 
        name: str, 
        appointment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email confirmation for appointment booking"""
        try:
            # Create email content
            subject = f"Confirmation de rendez-vous - {settings.BUSINESS_NAME}"
            
            # HTML email template
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .appointment-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                    .button {{ background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{settings.BUSINESS_NAME}</h1>
                    <h2>Confirmation de votre rendez-vous</h2>
                </div>
                
                <div class="content">
                    <p>Bonjour {name},</p>
                    
                    <p>Votre rendez-vous a été confirmé avec succès !</p>
                    
                    <div class="appointment-details">
                        <h3>Détails de votre rendez-vous :</h3>
                        <p><strong>Date :</strong> {appointment_details['date']}</p>
                        <p><strong>Heure :</strong> {appointment_details['time']}</p>
                        <p><strong>Service :</strong> {appointment_details['service']}</p>
                        <p><strong>Durée :</strong> {appointment_details.get('duration', settings.APPOINTMENT_DURATION)} minutes</p>
                        {f"<p><strong>Notes :</strong> {appointment_details.get('notes', '')}</p>" if appointment_details.get('notes') else ""}
                    </div>
                    
                    <p><strong>Informations importantes :</strong></p>
                    <ul>
                        <li>Veuillez arriver 15 minutes avant votre rendez-vous</li>
                        <li>Apportez une pièce d'identité valide</li>
                        <li>En cas d'empêchement, merci de nous prévenir 24h à l'avance</li>
                    </ul>
                    
                    <p>Vous recevrez un rappel automatique 24h avant votre rendez-vous.</p>
                    
                    <p>Cordialement,<br>L'équipe de {settings.BUSINESS_NAME}</p>
                </div>
                
                <div class="footer">
                    <p>{settings.BUSINESS_NAME} - {settings.BUSINESS_HOURS}</p>
                    <p>Cet email a été envoyé automatiquement par notre système de réservation.</p>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_body = f"""
            {settings.BUSINESS_NAME}
            Confirmation de votre rendez-vous
            
            Bonjour {name},
            
            Votre rendez-vous a été confirmé avec succès !
            
            Détails de votre rendez-vous :
            - Date : {appointment_details['date']}
            - Heure : {appointment_details['time']}
            - Service : {appointment_details['service']}
            - Durée : {appointment_details.get('duration', settings.APPOINTMENT_DURATION)} minutes
            {f"- Notes : {appointment_details.get('notes', '')}" if appointment_details.get('notes') else ""}
            
            Informations importantes :
            - Veuillez arriver 15 minutes avant votre rendez-vous
            - Apportez une pièce d'identité valide
            - En cas d'empêchement, merci de nous prévenir 24h à l'avance
            
            Vous recevrez un rappel automatique 24h avant votre rendez-vous.
            
            Cordialement,
            L'équipe de {settings.BUSINESS_NAME}
            
            {settings.BUSINESS_NAME} - {settings.BUSINESS_HOURS}
            """
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = email
            
            # Add both parts
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            if self.smtp_server and self.smtp_username and self.smtp_password:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, email, message.as_string())
                
                logger.info(f"Email confirmation sent to {email}")
                return {
                    "success": True,
                    "message": f"Email de confirmation envoyé à {email}"
                }
            else:
                logger.warning("Email configuration incomplete - confirmation not sent")
                return {
                    "success": False,
                    "message": "Configuration email incomplète"
                }
                
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erreur lors de l'envoi de l'email de confirmation"
            }

    async def send_sms_confirmation(
        self, 
        phone: str, 
        name: str, 
        appointment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send SMS confirmation for appointment booking"""
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
                return {
                    "success": False,
                    "message": "Configuration SMS non disponible"
                }
            
            # Format phone number (ensure it starts with +)
            if not phone.startswith('+'):
                # Assume French number if no country code
                if phone.startswith('0'):
                    phone = '+33' + phone[1:]
                else:
                    phone = '+33' + phone
            
            # Create SMS message
            message_body = f"""
            🏥 {settings.BUSINESS_NAME}
            
            Bonjour {name} ! Votre RDV est confirmé :
            
            📅 {appointment_details['date']} à {appointment_details['time']}
            🩺 {appointment_details['service']}
            ⏱️ {appointment_details.get('duration', settings.APPOINTMENT_DURATION)} min
            
            Rappel automatique 24h avant.
            
            En cas d'empêchement, prévenez 24h à l'avance.
            Merci !
            """
            
            # Send via Twilio API
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            
            auth = aiohttp.BasicAuth(self.twilio_account_sid, self.twilio_auth_token)
            data = {
                'From': self.twilio_phone_number,
                'To': phone,
                'Body': message_body
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, auth=auth, data=data) as response:
                    if response.status == 201:
                        logger.info(f"SMS confirmation sent to {phone}")
                        return {
                            "success": True,
                            "message": f"SMS de confirmation envoyé au {phone}"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Twilio API error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "message": "Erreur lors de l'envoi du SMS"
                        }
                        
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erreur lors de l'envoi du SMS de confirmation"
            }

    async def send_reminder(
        self, 
        email: str, 
        phone: str, 
        name: str, 
        appointment_details: Dict[str, Any],
        hours_before: int = 24
    ) -> Dict[str, Any]:
        """Send appointment reminder via email and SMS"""
        results = {
            "email": {"success": False},
            "sms": {"success": False}
        }
        
        try:
            # Email reminder
            subject = f"Rappel de rendez-vous - {settings.BUSINESS_NAME}"
            
            email_body = f"""
            Bonjour {name},
            
            Nous vous rappelons votre rendez-vous prévu demain :
            
            📅 Date : {appointment_details['date']}
            🕐 Heure : {appointment_details['time']}
            🏥 Service : {appointment_details['service']}
            
            N'oubliez pas d'arriver 15 minutes en avance avec votre pièce d'identité.
            
            À bientôt !
            L'équipe de {settings.BUSINESS_NAME}
            """
            
            # SMS reminder
            sms_body = f"""
            🔔 Rappel RDV {settings.BUSINESS_NAME}
            
            Bonjour {name}, votre RDV est demain :
            📅 {appointment_details['date']} à {appointment_details['time']}
            
            Arrivez 15 min en avance avec votre ID.
            À bientôt !
            """
            
            # Send both notifications
            email_result = await self.send_email_confirmation(email, name, appointment_details)
            sms_result = await self.send_sms_confirmation(phone, name, appointment_details)
            
            return {
                "success": email_result["success"] or sms_result["success"],
                "email": email_result,
                "sms": sms_result,
                "message": "Rappel envoyé"
            }
            
        except Exception as e:
            logger.error(f"Reminder sending error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erreur lors de l'envoi du rappel"
            }

    async def send_cancellation_notice(
        self, 
        email: str, 
        phone: str, 
        name: str, 
        appointment_details: Dict[str, Any],
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send appointment cancellation notification"""
        try:
            # Email cancellation notice
            subject = f"Annulation de rendez-vous - {settings.BUSINESS_NAME}"
            
            email_body = f"""
            Bonjour {name},
            
            Votre rendez-vous du {appointment_details['date']} à {appointment_details['time']} a été annulé.
            
            {f"Raison : {reason}" if reason else ""}
            
            Pour reprendre un nouveau rendez-vous, n'hésitez pas à nous contacter.
            
            Cordialement,
            L'équipe de {settings.BUSINESS_NAME}
            """
            
            # SMS cancellation notice
            sms_body = f"""
            ❌ {settings.BUSINESS_NAME}
            
            Bonjour {name}, votre RDV du {appointment_details['date']} à {appointment_details['time']} a été annulé.
            
            Contactez-nous pour un nouveau RDV.
            """
            
            # Send notifications
            email_result = await self.send_email_confirmation(email, name, appointment_details)
            sms_result = await self.send_sms_confirmation(phone, name, appointment_details)
            
            return {
                "success": email_result["success"] or sms_result["success"],
                "email": email_result,
                "sms": sms_result,
                "message": "Avis d'annulation envoyé"
            }
            
        except Exception as e:
            logger.error(f"Cancellation notice error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erreur lors de l'envoi de l'avis d'annulation"
            }


# Global notification manager instance
notification_manager = NotificationManager()