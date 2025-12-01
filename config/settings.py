import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # LiveKit Configuration
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "wss://your-livekit-server.livekit.cloud")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")
    
    # Deepgram Configuration
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    
    # OpenAI Configuration  
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # OpenAI TTS Configuration (Primary TTS)
    OPENAI_TTS_MODEL: str = os.getenv("OPENAI_TTS_MODEL", "tts-1")
    OPENAI_TTS_VOICE: str = os.getenv("OPENAI_TTS_VOICE", "alloy")
    
    # Google Calendar Configuration
    GOOGLE_CREDENTIALS_FILE: Optional[str] = os.getenv("GOOGLE_CREDENTIALS_FILE")
    GOOGLE_TOKEN_FILE: Optional[str] = os.getenv("GOOGLE_TOKEN_FILE")
    GOOGLE_CALENDAR_ID: Optional[str] = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    
    # Business Configuration
    BUSINESS_NAME: str = os.getenv("BUSINESS_NAME", "Cabinet Médical")
    BUSINESS_HOURS: str = os.getenv("BUSINESS_HOURS", "09:00-17:00")
    APPOINTMENT_DURATION: int = int(os.getenv("APPOINTMENT_DURATION", "30"))  # minutes
    
    # Email Configuration (for appointment confirmations)
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL: Optional[str] = os.getenv("FROM_EMAIL")
    
    # SMS Configuration (Twilio - for appointment confirmations)
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    
    class Config:
        env_file = ".env"

settings = Settings()