import asyncio
import io
from typing import Optional, AsyncIterator
from livekit import rtc, agents
from livekit.agents.tts import TTS, SynthesizedAudio
from openai import AsyncOpenAI
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class OpenAITTS(TTS):
    """
    OpenAI TTS implementation for French voice agent
    More cost-effective alternative to ElevenLabs
    """
    
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = "tts-1",  # tts-1 or tts-1-hd
        voice: str = "alloy",  # alloy, echo, fable, onyx, nova, shimmer
        speed: float = 1.0,  # 0.25 to 4.0
        response_format: str = "mp3"
    ):
        super().__init__(
            capabilities=agents.tts.TTSCapabilities(streaming=False),  # OpenAI TTS is not streaming
            sample_rate=24000,
            num_channels=1
        )
        
        self._client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self._model = model
        self._voice = voice
        self._speed = speed
        self._response_format = response_format
        
        if not api_key and not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
    
    def _preprocess_french_text(self, text: str) -> str:
        """Preprocess text for better French pronunciation with OpenAI TTS"""
        # OpenAI TTS handles French well, but some optimizations help
        replacements = {
            # Common abbreviations that need expansion
            "RDV": "rendez-vous",
            "rdv": "rendez-vous", 
            "Dr": "Docteur",
            "Dre": "Docteure",
            "Mme": "Madame",
            "M.": "Monsieur",
            
            # Time expressions for better pronunciation
            "h00": "heures",
            "h30": "heures trente",
            "h15": "heures quinze", 
            "h45": "heures quarante-cinq",
            
            # Numbers that might be ambiguous
            "1er": "premier",
            "1ère": "première",
            "2e": "deuxième",
            "2ème": "deuxième"
        }
        
        processed_text = text
        for abbrev, full in replacements.items():
            processed_text = processed_text.replace(abbrev, full)
            
        # Add natural pauses for better flow
        processed_text = processed_text.replace(". ", "... ")
        processed_text = processed_text.replace("! ", "! ")
        processed_text = processed_text.replace("? ", "? ")
        
        return processed_text

    async def _synthesize_impl(self, text: str) -> SynthesizedAudio:
        """Synthesize speech from text using OpenAI TTS"""
        try:
            processed_text = self._preprocess_french_text(text)
            
            response = await self._client.audio.speech.create(
                model=self._model,
                voice=self._voice,
                input=processed_text,
                speed=self._speed,
                response_format=self._response_format
            )
            
            # Get audio data
            audio_data = response.content
            
            # Convert to PCM for LiveKit
            audio_frames = await self._convert_to_pcm(audio_data)
            
            return SynthesizedAudio(
                text=text,
                data=rtc.AudioFrame.create(
                    sample_rate=self.sample_rate,
                    num_channels=self.num_channels,
                    samples_per_channel=len(audio_frames) // (self.num_channels * 2)  # 16-bit samples
                ).from_bytes(audio_frames)
            )
            
        except Exception as e:
            logger.error(f"OpenAI TTS synthesis error: {e}")
            raise

    async def _stream_synthesize_impl(
        self, 
        text_stream: AsyncIterator[str]
    ) -> AsyncIterator[SynthesizedAudio]:
        """
        Stream synthesis by buffering text and synthesizing complete sentences
        OpenAI doesn't support true streaming, so we buffer and synthesize chunks
        """
        try:
            text_buffer = ""
            sentence_endings = [".", "!", "?", ";", "\n"]
            
            async for text_chunk in text_stream:
                text_buffer += text_chunk
                
                # Look for complete sentences
                should_synthesize = any(ending in text_buffer for ending in sentence_endings)
                
                if should_synthesize or len(text_buffer) > 150:  # Force synthesis for long text
                    # Find the last complete sentence
                    last_ending = -1
                    for ending in sentence_endings:
                        pos = text_buffer.rfind(ending)
                        if pos > last_ending:
                            last_ending = pos
                    
                    if last_ending > 0:
                        # Synthesize complete sentences
                        to_synthesize = text_buffer[:last_ending + 1].strip()
                        text_buffer = text_buffer[last_ending + 1:]
                        
                        if to_synthesize:
                            audio = await self._synthesize_impl(to_synthesize)
                            yield audio
            
            # Synthesize any remaining text
            if text_buffer.strip():
                audio = await self._synthesize_impl(text_buffer.strip())
                yield audio
                
        except Exception as e:
            logger.error(f"OpenAI TTS streaming error: {e}")
            raise

    async def _convert_to_pcm(self, audio_data: bytes) -> bytes:
        """Convert audio data to PCM format for LiveKit"""
        try:
            import subprocess
            import tempfile
            
            # Determine input format based on response_format
            input_format = self._response_format
            
            with tempfile.NamedTemporaryFile(suffix=f".{input_format}") as input_file:
                input_file.write(audio_data)
                input_file.flush()
                
                # Use ffmpeg to convert to PCM
                process = await asyncio.create_subprocess_exec(
                    "ffmpeg",
                    "-i", input_file.name,
                    "-f", "s16le",  # 16-bit signed PCM little-endian
                    "-ar", str(self.sample_rate),  # Sample rate
                    "-ac", str(self.num_channels),  # Number of channels
                    "-",  # Output to stdout
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    return stdout
                else:
                    logger.error(f"FFmpeg conversion error: {stderr.decode()}")
                    raise Exception("Audio conversion failed")
                    
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            # Fallback: return silence
            duration_seconds = 1
            samples = self.sample_rate * duration_seconds * self.num_channels
            return b"\x00" * (samples * 2)  # 16-bit samples