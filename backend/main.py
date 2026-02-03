from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moderation.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ModerationEvent(Base):
    __tablename__ = "moderation_events"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    label = Column(String)
    confidence = Column(Float)
    status = Column(String)  # "safe" or "flagged"
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_path = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class ModerationResponse(BaseModel):
    id: int
    filename: str
    label: str
    confidence: float
    status: str
    timestamp: datetime

class ModerationHistoryResponse(BaseModel):
    events: List[ModerationResponse]
    total: int

# FastAPI app
app = FastAPI(title="Image Review Portal API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
CLASSIFIER_API_URL = os.getenv("CLASSIFIER_API_URL", "http://localhost:8000/classify")
FLAGGED_CLASSES = os.getenv("FLAGGED_CLASSES", "inappropriate,nsfw,violence").split(",")

def determine_status(label: str, confidence: float) -> str:
    """Determine if image is safe or flagged based on label and rules"""
    label_lower = label.lower()
    for flagged_class in FLAGGED_CLASSES:
        if flagged_class.lower().strip() in label_lower:
            return "flagged"
    return "safe"

@app.post("/moderate", response_model=ModerationResponse)
async def moderate_image(file: UploadFile = File(...)):
    """
    Upload an image for moderation.
    Forwards to classifier API and applies rules to determine safe/flagged status.
    """
    try:
        # Read image file
        image_data = await file.read()
        
        # Forward to classifier API
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"file": (file.filename, image_data, file.content_type)}
            response = await client.post(CLASSIFIER_API_URL, files=files)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Classifier API error: {response.text}"
                )
            
            classifier_result = response.json()
            label = classifier_result.get("label", "unknown")
            confidence = classifier_result.get("confidence", 0.0)
        
        # Determine status based on rules
        status = determine_status(label, confidence)
        
        # Save to database
        with get_db() as db:
            event = ModerationEvent(
                filename=file.filename,
                label=label,
                confidence=confidence,
                status=status,
                timestamp=datetime.utcnow()
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            
            return ModerationResponse(
                id=event.id,
                filename=event.filename,
                label=event.label,
                confidence=event.confidence,
                status=event.status,
                timestamp=event.timestamp
            )
    
    except httpx.RequestError as e:
        logger.error(f"Error calling classifier API: {e}")
        raise HTTPException(status_code=503, detail="Classifier service unavailable")
    except Exception as e:
        logger.error(f"Error moderating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=ModerationHistoryResponse)
async def get_history(limit: int = 50, offset: int = 0):
    """
    Get moderation history with pagination.
    """
    try:
        with get_db() as db:
            events = db.query(ModerationEvent).order_by(ModerationEvent.timestamp.desc()).offset(offset).limit(limit).all()
            total = db.query(ModerationEvent).count()
            
            return ModerationHistoryResponse(
                events=[
                    ModerationResponse(
                        id=event.id,
                        filename=event.filename,
                        label=event.label,
                        confidence=event.confidence,
                        status=event.status,
                        timestamp=event.timestamp
                    )
                    for event in events
                ],
                total=total
            )
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "image-review-portal-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

