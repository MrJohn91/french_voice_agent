import asyncio
import aiohttp
from typing import Optional, AsyncIterator, Union
from livekit import rtc, agents
from livekit.agents.stt import STT, SpeechEvent, SpeechEventType
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class DeepgramSTT(STT):
    """
    French-optimized Deepgram Nova-2 Speech-to-Text implementation
    """
    
    def __init__(
        self,
        *,
        model: str = "nova-2",
        language: str = "fr",
        detect_language: bool = True,  # Auto-detect French/English
        api_key: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        interim_results: bool = True
    ):
        super().__init__(
            capabilities=agents.stt.STTCapabilities(
                streaming=True,
                interim_results=interim_results
            )
        )
        
        self._api_key = api_key or settings.DEEPGRAM_API_KEY
        self._model = model
        self._language = language
        self._detect_language = detect_language
        self._sample_rate = sample_rate
        self._channels = channels
        self._interim_results = interim_results
        
        if not self._api_key:
            raise ValueError("Deepgram API key is required")
    
    def _sanitize_options(self, *, language: Optional[str] = None) -> dict:
        """Prepare Deepgram API options with French optimization"""
        options = {
            "model": self._model,
            "language": language or self._language,
            "channels": self._channels,
            "sample_rate": self._sample_rate,
            "encoding": "linear16",
            "interim_results": self._interim_results,
            "punctuate": True,
            "diarize": False,
            "smart_format": True,
            "profanity_filter": False,
            "redact": [],
            "keywords": [
                # French appointment booking keywords for better recognition
                "rendez-vous:3",
                "rdv:3", 
                "réservation:3",
                "disponible:2",
                "horaire:2",
                "consultation:3",
                "docteur:2",
                "médecin:2"
            ]
        }
        
        # Enable language detection for French/English switching
        if self._detect_language:
            options["detect_language"] = True
            options["language"] = ["fr", "en"]
        
        return options

    async def _recognize_impl(
        self, 
        buffer: rtc.AudioFrame, 
        *, 
        language: Optional[str] = None
    ) -> SpeechEvent:
        """Non-streaming recognition for single audio frame"""
        try:
            options = self._sanitize_options(language=language)
            
            # Convert audio frame to bytes
            audio_data = buffer.data.tobytes()
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Token {self._api_key}",
                    "Content-Type": "audio/wav"
                }
                
                url = "https://api.deepgram.com/v1/listen"
                params = {k: str(v) if not isinstance(v, list) else ",".join(v) 
                         for k, v in options.items()}
                
                async with session.post(
                    url, 
                    headers=headers, 
                    params=params, 
                    data=audio_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("results", {}).get("channels", []):
                            transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                            confidence = result["results"]["channels"][0]["alternatives"][0]["confidence"]
                            detected_language = result.get("results", {}).get("language")
                            
                            logger.info(f"STT Result: '{transcript}' (confidence: {confidence:.2f}, lang: {detected_language})")
                            
                            return SpeechEvent(
                                type=SpeechEventType.FINAL_TRANSCRIPT,
                                transcript=transcript,
                                confidence=confidence,
                                language=detected_language
                            )
                    else:
                        logger.error(f"Deepgram API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"STT recognition error: {e}")
            
        return SpeechEvent(
            type=SpeechEventType.FINAL_TRANSCRIPT,
            transcript="",
            confidence=0.0
        )

    async def _stream_recognize_impl(
        self, 
        audio_stream: AsyncIterator[rtc.AudioFrame],
        *, 
        language: Optional[str] = None
    ) -> AsyncIterator[SpeechEvent]:
        """Streaming recognition with French optimization"""
        try:
            options = self._sanitize_options(language=language)
            
            # Create WebSocket connection to Deepgram
            uri = "wss://api.deepgram.com/v1/listen"
            params = {k: str(v) if not isinstance(v, list) else ",".join(v) 
                     for k, v in options.items()}
            
            import websockets
            import json
            
            headers = {"Authorization": f"Token {self._api_key}"}
            
            async with websockets.connect(
                f"{uri}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
                extra_headers=headers
            ) as websocket:
                
                # Start audio streaming task
                async def send_audio():
                    try:
                        async for frame in audio_stream:
                            await websocket.send(frame.data.tobytes())
                    except Exception as e:
                        logger.error(f"Audio streaming error: {e}")
                    finally:
                        await websocket.send(json.dumps({"type": "CloseStream"}))
                
                # Start receiving transcripts
                audio_task = asyncio.create_task(send_audio())
                
                try:
                    async for message in websocket:
                        result = json.loads(message)
                        
                        if result.get("type") == "Results":
                            channel = result.get("channel", {})
                            alternatives = channel.get("alternatives", [])
                            
                            if alternatives:
                                transcript = alternatives[0].get("transcript", "")
                                confidence = alternatives[0].get("confidence", 0.0)
                                is_final = result.get("is_final", False)
                                detected_language = result.get("language")
                                
                                if transcript.strip():
                                    yield SpeechEvent(
                                        type=SpeechEventType.FINAL_TRANSCRIPT if is_final 
                                             else SpeechEventType.INTERIM_TRANSCRIPT,
                                        transcript=transcript,
                                        confidence=confidence,
                                        language=detected_language
                                    )
                
                finally:
                    if not audio_task.done():
                        audio_task.cancel()
                        
        except Exception as e:
            logger.error(f"Streaming STT error: {e}")
            yield SpeechEvent(
                type=SpeechEventType.FINAL_TRANSCRIPT,
                transcript="",
                confidence=0.0
            )