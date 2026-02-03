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
from io import BytesIO
from PIL import Image
import numpy as np
from ml_classifier import get_classifier

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
MOCK_CLASSIFIER = os.getenv("MOCK_CLASSIFIER", "false").lower() == "true"

def determine_status(label: str, confidence: float) -> str:
    """Determine if image is safe or flagged based on label and rules"""
    label_lower = label.lower()
    
    # Explicitly safe labels (always safe, regardless of other checks)
    safe_labels = ["safe_animal", "safe_landscape", "safe_portrait", "safe_food", "safe_object", "safe_image"]
    if any(safe_label in label_lower for safe_label in safe_labels):
        return "safe"
    
    # Check for flagged classes
    for flagged_class in FLAGGED_CLASSES:
        if flagged_class.lower().strip() in label_lower:
            return "flagged"
    
    # Default to safe (better to be conservative)
    return "safe"

def analyze_image_content(image_data: bytes, filename: str) -> tuple[str, float]:
    """
    Analyze image content using heuristics to determine label and confidence.
    This is a mock classifier that actually looks at image properties.
    """
    try:
        # Load image
        image = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get image properties
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1.0
        total_pixels = width * height
        
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        # Calculate color statistics
        mean_color = np.mean(img_array, axis=(0, 1))
        std_color = np.std(img_array, axis=(0, 1))
        
        # Calculate brightness (average of RGB)
        brightness = np.mean(img_array)
        
        # Calculate color distribution
        red_mean, green_mean, blue_mean = mean_color
        
        # Heuristic 1: Check for very dark images (might be inappropriate)
        if brightness < 30:
            # Very dark image - could be inappropriate
            if red_mean > green_mean * 1.2 and red_mean > blue_mean * 1.2:
                # Reddish dark image - higher chance of inappropriate
                return "inappropriate_content", 0.75
            return "dark_image", 0.65
        
        # Heuristic 2: Check for portraits/people - these should be SAFE
        # Skin tones typically have: R > G > B and R/G ratio around 1.1-1.5
        skin_tone_ratio = red_mean / green_mean if green_mean > 0 else 1.0
        if 1.1 <= skin_tone_ratio <= 1.5 and red_mean > 100 and blue_mean < red_mean * 0.9:
            # High percentage of skin-like colors
            skin_pixels = np.sum(
                (img_array[:, :, 0] > img_array[:, :, 1] * 1.1) & 
                (img_array[:, :, 1] > img_array[:, :, 2] * 0.9) &
                (img_array[:, :, 0] > 100)
            )
            skin_percentage = skin_pixels / total_pixels if total_pixels > 0 else 0
            
            # Normal portraits with skin tones should be SAFE
            # Only flag if it's clearly inappropriate (very unusual aspect ratio + very dark + low variation)
            if skin_percentage > 0.3:  # Has skin tones
                # Normal portrait characteristics = SAFE
                if 0.6 <= aspect_ratio <= 1.5:  # Normal aspect ratio
                    if brightness > 60:  # Not too dark
                        if std_color.mean() > 15:  # Has some color variation (normal portrait)
                            return "safe_portrait", 0.90  # High confidence safe
                
                # Only flag if EXTREMELY suspicious (very dark, unusual format, no variation)
                if brightness < 40 and (aspect_ratio > 2.0 or aspect_ratio < 0.5) and std_color.mean() < 10:
                    return "inappropriate_content", 0.75  # Low confidence, very suspicious
                else:
                    # Default to safe portrait
                    return "safe_portrait", 0.85
        
        # Heuristic 3: Check for weapons (guns, knives) - but exclude common safe objects first
        # First, check if this looks like a safe object (animal, nature, etc.)
        # Animals and nature have more color variation and organic patterns
        
        # Check for nature/animal patterns (high color variation, organic shapes)
        if std_color.mean() > 50:  # High color variation suggests nature/animal
            # Likely safe - skip weapon detection
            pass
        elif green_mean > 80 and std_color.mean() > 35:  # Green with variation = nature
            # Likely nature - skip weapon detection
            pass
        else:
            # Only check for weapons if it doesn't look like nature/animal
            # Check for metallic/silver colors (balanced RGB, medium brightness)
            metallic_pixels = np.sum(
                (np.abs(img_array[:, :, 0] - img_array[:, :, 1]) < 25) &  # R and G similar
                (np.abs(img_array[:, :, 1] - img_array[:, :, 2]) < 25) &  # G and B similar
                (np.abs(img_array[:, :, 0] - img_array[:, :, 2]) < 25) &  # R and B similar
                (img_array[:, :, 0] > 60) & (img_array[:, :, 0] < 180)  # Medium brightness (metallic range)
            )
            metallic_percentage = metallic_pixels / total_pixels if total_pixels > 0 else 0
            
            # Check for dark/black objects (weapons are often black/dark gray)
            dark_pixels = np.sum(
                (img_array[:, :, 0] < 50) &  # Very dark red
                (img_array[:, :, 1] < 50) &  # Very dark green
                (img_array[:, :, 2] < 50)    # Very dark blue
            )
            dark_percentage = dark_pixels / total_pixels if total_pixels > 0 else 0
            
            # Weapon detection requires MULTIPLE conditions to reduce false positives
            weapon_score = 0
            
            # Condition 1: Significant uniform dark areas (weapons have uniform dark colors)
            if dark_percentage > 0.15:  # At least 15% very dark pixels
                dark_regions = img_array[
                    (img_array[:, :, 0] < 50) & 
                    (img_array[:, :, 1] < 50) & 
                    (img_array[:, :, 2] < 50)
                ]
                if len(dark_regions) > 0:
                    dark_std = np.std(dark_regions)
                    if dark_std < 15:  # Very uniform dark areas
                        weapon_score += 1
            
            # Condition 2: Metallic content (guns have metallic parts)
            if metallic_percentage > 0.20 and std_color.mean() < 30:  # High metallic, low variation
                weapon_score += 1
            
            # Condition 3: Dark gray/black objects with very uniform color
            dark_gray_pixels = np.sum(
                (img_array[:, :, 0] < 70) &  # Dark
                (img_array[:, :, 1] < 70) &
                (img_array[:, :, 2] < 70) &
                (np.abs(img_array[:, :, 0] - img_array[:, :, 1]) < 20) &  # Balanced (gray)
                (np.abs(img_array[:, :, 1] - img_array[:, :, 2]) < 20) &
                (std_color.mean() < 25)  # Low overall variation
            )
            dark_gray_percentage = dark_gray_pixels / total_pixels if total_pixels > 0 else 0
            
            if dark_gray_percentage > 0.20:  # At least 20% uniform dark gray
                weapon_score += 1
            
            # Only flag as weapon if MULTIPLE conditions are met (reduces false positives)
            if weapon_score >= 2:  # Need at least 2 conditions
                # Additional check: exclude if it looks like an animal (high organic variation)
                # Animals have more texture and variation even in dark areas
                if std_color.mean() < 20:  # Very low variation = more likely weapon
                    return "violence_weapon", 0.82
                elif weapon_score >= 3:  # All conditions met = high confidence
                    return "violence_weapon", 0.88
        
        # Heuristic 3b: Check for violent/red content (blood-like colors)
        # High red, low green/blue
        if red_mean > 150 and green_mean < red_mean * 0.6 and blue_mean < red_mean * 0.6:
            red_dominant_pixels = np.sum(
                (img_array[:, :, 0] > 150) & 
                (img_array[:, :, 1] < img_array[:, :, 0] * 0.6) &
                (img_array[:, :, 2] < img_array[:, :, 0] * 0.6)
            )
            if red_dominant_pixels / total_pixels > 0.3:
                return "violence_content", 0.85
        
        # Heuristic 4: Check for nature/landscape (greens and blues dominant)
        if green_mean > 100 and blue_mean > 80:
            green_blue_pixels = np.sum(
                (img_array[:, :, 1] > 100) & (img_array[:, :, 2] > 80)
            )
            if green_blue_pixels / total_pixels > 0.4:
                return "safe_landscape", 0.92
        
        # Heuristic 5: Check for bright, colorful images (likely safe)
        if brightness > 180 and std_color.mean() > 40:
            # Bright and colorful - likely safe content
            return "safe_image", 0.88
        
        # Heuristic 6: Check aspect ratio for portraits
        if 0.7 <= aspect_ratio <= 1.3:  # Square-ish or portrait
            if 100 < brightness < 200:  # Moderate brightness
                return "safe_portrait", 0.85
        
        # Heuristic 7: Very high brightness (likely safe, well-lit)
        if brightness > 200:
            return "safe_image", 0.90
        
        # Heuristic 8: Check filename as additional signal (before defaulting to safe)
        # This helps catch weapons even if image analysis doesn't detect them clearly
        filename_lower = filename.lower()
        weapon_keywords = ["gun", "weapon", "knife", "rifle", "pistol", "firearm", "blade", "sword", "ammo", "ammunition"]
        if any(word in filename_lower for word in weapon_keywords):
            # Filename suggests weapon - combine with image analysis
            # dark_percentage and metallic_percentage are already calculated above
            if dark_percentage > 0.10 or metallic_percentage > 0.15:
                return "violence_weapon", 0.90  # High confidence if both filename and image match
            else:
                return "violence_weapon", 0.75  # Medium confidence from filename alone
        
        # Default: moderate confidence safe
        return "safe_image", 0.75
        
    except Exception as e:
        logger.warning(f"Error analyzing image content: {e}, falling back to filename check")
        # Fallback to filename-based classification
        filename_lower = filename.lower()
        if any(word in filename_lower for word in ["inappropriate", "nsfw", "violence", "explicit", "adult", "porn"]):
            return "inappropriate_content", 0.70
        elif any(word in filename_lower for word in ["weapon", "gun", "knife", "violence", "blood", "rifle", "pistol", "firearm", "blade", "sword"]):
            return "violence_weapon", 0.75  # Changed to violence_weapon for consistency
        else:
            return "safe_image", 0.65

@app.post("/moderate", response_model=ModerationResponse)
async def moderate_image(file: UploadFile = File(...)):
    """
    Upload an image for moderation.
    Forwards to classifier API and applies rules to determine safe/flagged status.
    """
    try:
        # Read image file
        image_data = await file.read()
        
        # ML-based classifier (when MOCK_CLASSIFIER is enabled)
        if MOCK_CLASSIFIER:
            logger.info("Using ML classifier (MOCK_CLASSIFIER=true)")
            try:
                classifier = get_classifier()
                label, confidence = classifier.predict(image_data)
                logger.info(f"ML classifier result: {label} (confidence: {confidence:.2f})")
            except Exception as e:
                logger.error(f"ML classifier error: {e}, falling back to heuristic analysis")
                # Fallback to heuristic-based analysis if ML model fails
                label, confidence = analyze_image_content(image_data, file.filename)
                logger.info(f"Fallback classifier result: {label} (confidence: {confidence:.2f})")
        else:
            # Forward to classifier API
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    files = {"file": (file.filename, image_data, file.content_type)}
                    response = await client.post(CLASSIFIER_API_URL, files=files)
                    
                    if response.status_code != 200:
                        error_msg = f"Classifier API returned {response.status_code}: {response.text[:200]}"
                        logger.error(error_msg)
                        raise HTTPException(
                            status_code=503,
                            detail=f"Classifier API error: {error_msg}"
                        )
                    
                    classifier_result = response.json()
                    label = classifier_result.get("label", "unknown")
                    confidence = classifier_result.get("confidence", 0.0)
            except httpx.ConnectError as e:
                error_msg = f"Cannot connect to classifier API at {CLASSIFIER_API_URL}. Set MOCK_CLASSIFIER=true for development."
                logger.error(f"{error_msg} Error: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=error_msg
                )
            except httpx.TimeoutException as e:
                error_msg = "Classifier API request timed out"
                logger.error(f"{error_msg}: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=error_msg
                )
            except httpx.RequestError as e:
                error_msg = f"Error calling classifier API: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=503,
                    detail=f"Classifier service unavailable: {str(e)}"
                )
        
        # Determine status based on rules
        status = determine_status(label, confidence)
        
        # Save to database
        try:
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
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save moderation event: {str(db_error)}"
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except Exception as e:
        logger.exception(f"Unexpected error moderating image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

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

