import asyncio
import logging
from typing import Optional, Dict, Any
from livekit import rtc, agents
from livekit.agents import JobContext, WorkerOptions, cli, llm, tokenize
from livekit.agents.voice_assistant import VoiceAssistant

from speech.stt import DeepgramSTT
from speech.openai_tts import OpenAITTS
from llm.gpt_handler import FrenchGPTHandler
from tools.calendar import calendar_manager, check_availability_tool, get_available_slots_tool, book_appointment_tool, send_reminder_tool
from config.settings import settings

logger = logging.getLogger(__name__)

class FrenchVoiceAgent:
    """
    French Voice Agent for appointment booking
    """
    
    def __init__(self):
        # Initialize components
        self.stt = DeepgramSTT(
            model="nova-2",
            language="fr", 
            detect_language=True,  # Auto-detect French/English
            api_key=settings.DEEPGRAM_API_KEY
        )
        
        # Use OpenAI TTS (cost-effective and good quality for French)
        self.tts = OpenAITTS(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_TTS_MODEL,
            voice=settings.OPENAI_TTS_VOICE,
            speed=1.0
        )
        logger.info("Using OpenAI TTS for French voice synthesis")
        
        self.llm = FrenchGPTHandler(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.7,
            business_name=settings.BUSINESS_NAME,
            business_hours=settings.BUSINESS_HOURS
        )
        
        # Setup function tools for appointment booking
        self.function_context = agents.llm.FunctionContext()
        self._register_functions()
        
        logger.info("French Voice Agent initialized")

    def _register_functions(self):
        """Register appointment booking functions"""
        
        @self.function_context.ai_callable(
            description="Vérifier si un créneau de rendez-vous est disponible à une date et heure spécifique"
        )
        async def check_availability(
            date: agents.llm.TypeInfo(str, "Date au format YYYY-MM-DD"),
            time: agents.llm.TypeInfo(str, "Heure au format HH:MM")
        ) -> str:
            return await check_availability_tool(date, time)
        
        @self.function_context.ai_callable(
            description="Obtenir tous les créneaux disponibles pour une date donnée"
        )
        async def get_available_slots(
            date: agents.llm.TypeInfo(str, "Date au format YYYY-MM-DD")
        ) -> str:
            return await get_available_slots_tool(date)
            
        @self.function_context.ai_callable(
            description="Réserver un nouveau rendez-vous avec toutes les informations du patient. IMPORTANT: Le patient sera automatiquement notifié par email ET SMS après la réservation."
        )
        async def book_appointment(
            name: agents.llm.TypeInfo(str, "Nom complet du patient"),
            email: agents.llm.TypeInfo(str, "Adresse email du patient pour la confirmation"),
            phone: agents.llm.TypeInfo(str, "Numéro de téléphone du patient pour SMS (format: 0123456789 ou +33123456789)"),
            date: agents.llm.TypeInfo(str, "Date du rendez-vous au format YYYY-MM-DD"),
            time: agents.llm.TypeInfo(str, "Heure du rendez-vous au format HH:MM"),
            service: agents.llm.TypeInfo(str, "Type de service ou consultation demandée"),
            notes: agents.llm.TypeInfo(str, "Notes additionnelles optionnelles") = ""
        ) -> str:
            return await book_appointment_tool(name, email, phone, date, time, service, notes)
        
        @self.function_context.ai_callable(
            description="Envoyer un rappel de rendez-vous par email et SMS"
        )
        async def send_reminder(
            email: agents.llm.TypeInfo(str, "Adresse email du patient"),
            phone: agents.llm.TypeInfo(str, "Numéro de téléphone du patient"),
            name: agents.llm.TypeInfo(str, "Nom du patient"),
            date: agents.llm.TypeInfo(str, "Date du rendez-vous au format YYYY-MM-DD"),
            time: agents.llm.TypeInfo(str, "Heure du rendez-vous au format HH:MM"),
            service: agents.llm.TypeInfo(str, "Type de service")
        ) -> str:
            return await send_reminder_tool(email, phone, name, date, time, service)

    async def entrypoint(self, ctx: JobContext):
        """Main entry point for the voice agent"""
        logger.info(f"French Voice Agent starting for room: {ctx.room.name}")
        
        # Initialize calendar service
        await calendar_manager.initialize()
        
        # Create voice assistant with all components
        assistant = VoiceAssistant(
            vad=agents.silero.VAD.load(),  # Voice Activity Detection
            stt=self.stt,
            llm=self.llm,
            tts=self.tts,
            fnc_ctx=self.function_context,
            chat_ctx=agents.llm.ChatContext().append(
                role="system",
                text=f"""Vous êtes l'assistant vocal de {settings.BUSINESS_NAME}. 
                Accueillez chaleureusement les appelants et aidez-les à prendre rendez-vous en français.
                Soyez professionnel, patient et efficace."""
            )
        )
        
        # Start the assistant
        assistant.start(ctx.room)
        
        # Initial greeting when someone joins
        await assistant.say(
            f"Bonjour ! Bienvenue chez {settings.BUSINESS_NAME}. "
            "Je suis votre assistant vocal. Comment puis-je vous aider à prendre rendez-vous aujourd'hui ?",
            allow_interruptions=True
        )
        
        logger.info("French Voice Agent ready and waiting for calls")
        
        # Keep the agent running
        await asyncio.sleep(float('inf'))


# Entry point for LiveKit Workers
async def entrypoint(ctx: JobContext):
    """Entry point for LiveKit worker"""
    agent = FrenchVoiceAgent()
    await agent.entrypoint(ctx)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=None  # No prewarming needed
        )
    )