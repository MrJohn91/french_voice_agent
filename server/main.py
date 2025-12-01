import asyncio
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn

from config.settings import settings
from agent.tools.calendar import calendar_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="French Voice Agent API",
    description="API for managing French voice agent appointment booking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AppointmentRequest(BaseModel):
    name: str
    email: str
    phone: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    service: str
    notes: Optional[str] = ""

class AvailabilityRequest(BaseModel):
    date: str  # YYYY-MM-DD
    time: Optional[str] = None  # HH:MM, optional for checking specific time

class AppointmentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting French Voice Agent API")
    
    # Initialize calendar service
    calendar_initialized = await calendar_manager.initialize()
    if calendar_initialized:
        logger.info("Google Calendar service initialized successfully")
    else:
        logger.warning("Google Calendar service initialization failed")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "French Voice Agent API",
        "version": "1.0.0",
        "business": settings.BUSINESS_NAME
    }

# Get business information
@app.get("/business-info")
async def get_business_info():
    """Get business configuration information"""
    return {
        "name": settings.BUSINESS_NAME,
        "hours": settings.BUSINESS_HOURS,
        "appointment_duration": settings.APPOINTMENT_DURATION,
        "calendar_available": calendar_manager.service is not None
    }

# Check availability
@app.post("/availability/check", response_model=AppointmentResponse)
async def check_availability(request: AvailabilityRequest):
    """Check if a specific time slot is available"""
    try:
        if request.time:
            # Check specific time slot
            result = await calendar_manager.check_availability(request.date, request.time)
            return AppointmentResponse(
                success=result["available"],
                message=result["message"],
                data=result
            )
        else:
            # Get all available slots for the date
            result = await calendar_manager.get_available_slots(request.date)
            return AppointmentResponse(
                success=len(result["slots"]) > 0,
                message=result["message"],
                data=result
            )
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return AppointmentResponse(
            success=False,
            message="Erreur lors de la vérification des disponibilités",
            error=str(e)
        )

# Get available slots
@app.get("/availability/{date}")
async def get_available_slots(date: str):
    """Get all available time slots for a specific date"""
    try:
        result = await calendar_manager.get_available_slots(date)
        return AppointmentResponse(
            success=True,
            message=result["message"],
            data=result
        )
    except Exception as e:
        logger.error(f"Error getting available slots: {e}")
        return AppointmentResponse(
            success=False,
            message="Erreur lors de la récupération des créneaux",
            error=str(e)
        )

# Book appointment
@app.post("/appointments/book", response_model=AppointmentResponse)
async def book_appointment(request: AppointmentRequest):
    """Book a new appointment"""
    try:
        result = await calendar_manager.book_appointment(
            name=request.name,
            email=request.email,
            phone=request.phone,
            date=request.date,
            time=request.time,
            service=request.service,
            notes=request.notes
        )
        
        return AppointmentResponse(
            success=result["success"],
            message=result["message"],
            data=result.get("details", {}),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        return AppointmentResponse(
            success=False,
            message="Erreur lors de la réservation du rendez-vous",
            error=str(e)
        )

# Cancel appointment
@app.delete("/appointments/{event_id}")
async def cancel_appointment(event_id: str, reason: Optional[str] = None):
    """Cancel an existing appointment"""
    try:
        result = await calendar_manager.cancel_appointment(event_id, reason)
        return AppointmentResponse(
            success=result["success"],
            message=result["message"],
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Error canceling appointment: {e}")
        return AppointmentResponse(
            success=False,
            message="Erreur lors de l'annulation du rendez-vous",
            error=str(e)
        )

# Get agent stats (for monitoring)
@app.get("/stats")
async def get_agent_stats():
    """Get voice agent statistics"""
    return {
        "total_calls": 0,  # Would implement call tracking
        "successful_bookings": 0,  # Would implement booking tracking
        "average_call_duration": 0,  # Would implement timing tracking
        "languages_detected": ["fr", "en"],
        "uptime": "Available"
    }

# LiveKit room management endpoints
@app.post("/rooms/create")
async def create_room(room_name: str):
    """Create a new LiveKit room for voice calls"""
    try:
        # This would integrate with LiveKit API to create rooms
        # For now, return success
        return {
            "success": True,
            "room_name": room_name,
            "message": f"Salle {room_name} créée avec succès"
        }
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la salle")

@app.get("/rooms/{room_name}/status")
async def get_room_status(room_name: str):
    """Get status of a LiveKit room"""
    return {
        "room_name": room_name,
        "status": "active",
        "participants": 0,
        "agent_connected": True
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )