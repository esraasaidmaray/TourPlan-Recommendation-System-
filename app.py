"""
AI Travel Planner - Production API Server
========================================
FastAPI-based REST API for mobile app integration
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import sys
import os
from datetime import datetime
import traceback

# Add the TourPlan_Recommender module to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'TourPlan_Recommender'))

try:
    from TourPlan_Recommender.itinerary import build_itinerary, TOUR_THEMES
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Travel Planner API",
    description="Intelligent travel planning API for generating personalized tour itineraries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for mobile app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ItineraryRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    start_time: str = Field("09:00", pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="Start time (HH:MM)")
    end_time: str = Field("22:00", pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="End time (HH:MM)")
    language: str = Field("en", min_length=2, max_length=5, description="Language code")

class ActivitySlot(BaseModel):
    start: str
    end: str
    name: str
    category: str
    score: float

class ItineraryResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]
    timestamp: str
    request_id: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    database_status: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    timestamp: str
    request_id: str

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            timestamp=datetime.now().isoformat(),
            request_id=str(id(request))
        ).dict()
    )

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        import sqlite3
        conn = sqlite3.connect("poi.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM pois")
        count = cur.fetchone()[0]
        conn.close()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            database_status=f"connected ({count} POIs)"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            database_status="disconnected"
        )

# Get available locations
@app.get("/locations")
async def get_available_locations():
    """Get list of available cities and countries with POI counts"""
    try:
        from TourPlan_Recommender.data_preprocessor import initialize_data, get_available_locations
        
        # Initialize data if not already done
        if not initialize_data():
            return {
                "success": False,
                "message": "Failed to load location data",
                "locations": []
            }
        
        locations = get_available_locations()
        return {
            "success": True,
            "message": f"Found {len(locations)} locations",
            "locations": [
                {
                    "city": city,
                    "country": country,
                    "poi_count": count
                }
                for city, country, count in locations
            ]
        }
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "locations": []
        }

# Main itinerary generation endpoint
@app.post("/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(request: ItineraryRequest):
    """Generate a personalized travel itinerary"""
    request_id = str(id(request))
    
    try:
        logger.info(f"Generating itinerary for {request.city}, {request.country}")
        
        
        # Generate itinerary
        result = build_itinerary(
            city=request.city,
            country=request.country,
            lang=request.language,
            plan_size=None,
            start_time=request.start_time,
            end_time=request.end_time,
            theme=None
        )
        
        # Support new structure with 'days' (fallback to old 'slots' if present)
        has_days = isinstance(result, dict) and bool(result.get("days"))
        has_slots = isinstance(result, dict) and bool(result.get("slots"))
        if not (has_days or has_slots):
            return ItineraryResponse(
                success=False,
                message=f"No places found for {request.city}, {request.country}",
                data={"days": []},
                timestamp=datetime.now().isoformat(),
                request_id=request_id
            )
        
        # Build message
        if has_days:
            num_days = len(result.get("days", []))
            num_places = sum(len(d.get("places", [])) for d in result.get("days", []))
            msg = f"Generated {num_days} days / {num_places} places for {request.city}"
        else:
            msg = f"Generated {len(result['slots'])} activities for {request.city}"

        return ItineraryResponse(
            success=True,
            message=msg,
            data=result,
            timestamp=datetime.now().isoformat(),
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Error generating itinerary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate itinerary: {str(e)}"
        )

# Quick itinerary endpoint with query parameters
@app.get("/itinerary/quick")
async def quick_itinerary(
    city: str = Query(..., description="City name"),
    country: str = Query(..., description="Country name")
):
    """Quick itinerary generation with query parameters"""
    request_id = str(id(city + country))
    
    try:
        result = build_itinerary(
            city=city,
            country=country,
            theme=None,
            plan_size=None
        )
        
        has_days = isinstance(result, dict) and bool(result.get("days"))
        has_slots = isinstance(result, dict) and bool(result.get("slots"))
        if not (has_days or has_slots):
            return {
                "success": False,
                "message": f"No places found for {city}, {country}",
                "data": {"days": []},
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id
            }

        if has_days:
            num_days = len(result.get("days", []))
            num_places = sum(len(d.get("places", [])) for d in result.get("days", []))
            msg = f"Generated {num_days} days / {num_places} places for {city}"
        else:
            msg = f"Generated {len(result['slots'])} activities for {city}"

        return {
            "success": True,
            "message": msg,
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id
        }
        
    except Exception as e:
        logger.error(f"Quick itinerary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI Travel Planner API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "generate_itinerary": "POST /itinerary",
            "quick_itinerary": "GET /itinerary/quick",
            "get_themes": "GET /themes",
            "health_check": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
