import asyncio
import json
from typing import Optional, Dict, Any, List, AsyncIterator
from openai import AsyncOpenAI
from livekit.agents.llm import LLM, LLMStream, ChatContext, ChatMessage, ChatRole
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class FrenchGPTHandler(LLM):
    """
    French-optimized GPT-4o-mini implementation for appointment booking
    """
    
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 500,
        business_name: Optional[str] = None,
        business_hours: Optional[str] = None
    ):
        super().__init__()
        
        self._client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._business_name = business_name or settings.BUSINESS_NAME
        self._business_hours = business_hours or settings.BUSINESS_HOURS
        
    def _create_system_prompt(self) -> str:
        """Create French system prompt for appointment booking"""
        return f"""Vous êtes l'assistant vocal intelligent de {self._business_name}, spécialisé dans la prise de rendez-vous en français.

INSTRUCTIONS PRINCIPALES:
• Parlez exclusivement en français avec un ton professionnel et chaleureux
• Aidez les clients à prendre, modifier ou annuler des rendez-vous  
• Posez des questions claires pour obtenir les informations nécessaires
• Confirmez toujours les détails avant de finaliser un rendez-vous
• Restez patient et courtois en toutes circonstances

INFORMATIONS BUSINESS:
• Nom: {self._business_name}
• Horaires: {self._business_hours}
• Durée standard: {settings.APPOINTMENT_DURATION} minutes

GESTION DES RENDEZ-VOUS:
• Demandez: nom, téléphone, email, service souhaité, date/heure préférée
• Vérifiez la disponibilité avant de confirmer
• Proposez des alternatives si le créneau n'est pas libre
• Envoyez une confirmation par email/SMS

RÉPONSES TYPES:
Salutation: "Bonjour ! Je suis l'assistant de {self._business_name}. Comment puis-je vous aider aujourd'hui ?"
Prise de RDV: "Parfait ! J'aimerais vous aider à prendre rendez-vous. Quel service vous intéresse ?"
Confirmation: "Parfait ! J'ai réservé votre rendez-vous le [DATE] à [HEURE]. Vous recevrez une confirmation par email."

RÈGLES STRICTES:
• Ne donnez jamais d'avis médical ou de conseils de santé
• Redirigez les urgences vers les services appropriés
• Respectez la confidentialité des patients
• Utilisez les fonctions disponibles pour vérifier les disponibilités

Si vous ne comprenez pas une demande, demandez poliment des clarifications en français."""

    def _prepare_messages(self, chat_ctx: ChatContext) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI API with French optimization"""
        messages = [{"role": "system", "content": self._create_system_prompt()}]
        
        for msg in chat_ctx.messages:
            role = "user" if msg.role == ChatRole.USER else "assistant"
            messages.append({"role": role, "content": msg.content})
            
        return messages

    async def chat(
        self, 
        *, 
        chat_ctx: ChatContext,
        fnc_ctx: Optional[Any] = None,
        temperature: Optional[float] = None,
        n: int = 1,
        parallel_tool_calls: bool = True
    ) -> "ChatResponse":
        """Generate French response for appointment booking"""
        try:
            messages = self._prepare_messages(chat_ctx)
            
            # Prepare function calls if available
            functions = []
            if fnc_ctx and hasattr(fnc_ctx, 'ai_functions'):
                for func_info in fnc_ctx.ai_functions.values():
                    functions.append({
                        "type": "function",
                        "function": {
                            "name": func_info.name,
                            "description": func_info.description,
                            "parameters": func_info.parameters
                        }
                    })
            
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature or self._temperature,
                max_tokens=self._max_tokens,
                n=n,
                tools=functions if functions else None,
                tool_choice="auto" if functions else None,
                parallel_tool_calls=parallel_tool_calls
            )
            
            choice = response.choices[0]
            content = choice.message.content or ""
            
            # Handle function calls
            tool_calls = []
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                        tool_calls.append({
                            "id": tool_call.id,
                            "function": tool_call.function.name,
                            "arguments": arguments
                        })
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse tool call arguments: {e}")
            
            return ChatResponse(
                content=content,
                tool_calls=tool_calls,
                usage=response.usage.dict() if response.usage else None
            )
            
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            # Fallback response in French
            return ChatResponse(
                content="Je suis désolé, j'ai rencontré un problème technique. Pouvez-vous répéter votre demande ?",
                tool_calls=[],
                usage=None
            )

    async def astream_chat(
        self,
        *,
        chat_ctx: ChatContext,
        fnc_ctx: Optional[Any] = None,
        temperature: Optional[float] = None,
        n: int = 1
    ) -> AsyncIterator["ChatChunk"]:
        """Stream French responses for lower latency"""
        try:
            messages = self._prepare_messages(chat_ctx)
            
            # Prepare functions for streaming
            functions = []
            if fnc_ctx and hasattr(fnc_ctx, 'ai_functions'):
                for func_info in fnc_ctx.ai_functions.values():
                    functions.append({
                        "type": "function", 
                        "function": {
                            "name": func_info.name,
                            "description": func_info.description,
                            "parameters": func_info.parameters
                        }
                    })
            
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature or self._temperature,
                max_tokens=self._max_tokens,
                stream=True,
                tools=functions if functions else None,
                tool_choice="auto" if functions else None
            )
            
            async for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    
                    if delta.content:
                        yield ChatChunk(
                            choices=[{
                                "delta": {"content": delta.content}
                            }],
                            usage=getattr(chunk, 'usage', None)
                        )
                    
                    # Handle streaming function calls
                    if delta.tool_calls:
                        for tool_call in delta.tool_calls:
                            if tool_call.function:
                                yield ChatChunk(
                                    choices=[{
                                        "delta": {
                                            "tool_calls": [{
                                                "id": tool_call.id,
                                                "function": {
                                                    "name": tool_call.function.name,
                                                    "arguments": tool_call.function.arguments
                                                }
                                            }]
                                        }
                                    }],
                                    usage=getattr(chunk, 'usage', None)
                                )
                                
        except Exception as e:
            logger.error(f"Streaming chat error: {e}")
            yield ChatChunk(
                choices=[{
                    "delta": {"content": "Je suis désolé, j'ai rencontré un problème. Pouvez-vous répéter ?"}
                }],
                usage=None
            )


class ChatResponse:
    """Response from French GPT handler"""
    
    def __init__(
        self,
        content: str,
        tool_calls: List[Dict[str, Any]] = None,
        usage: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.tool_calls = tool_calls or []
        self.usage = usage


class ChatChunk:
    """Streaming chunk from French GPT handler"""
    
    def __init__(
        self,
        choices: List[Dict[str, Any]],
        usage: Optional[Dict[str, Any]] = None
    ):
        self.choices = choices
        self.usage = usage