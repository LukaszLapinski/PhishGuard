from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import os
import logging
from typing import Dict, List, Optional, Union
import uvicorn

# Import our custom modules
from model_manager import ModelManager
from feature_extraction import extract_url_features, convert_features_to_model_input

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI(
    title="PhishGuard API",
    description="API for PhishGuard browser extension to detect phishing websites",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request and response models
class URLCheckRequest(BaseModel):
    url: HttpUrl

class Feature(BaseModel):
    name: str
    value: Union[float, str, bool]
    importance: Optional[float] = None

class PredictionResponse(BaseModel):
    url: str
    is_phishing: bool
    confidence: float
    features_contribution: Optional[List[Feature]] = None
    message: Optional[str] = None

# Initialize model manager
model_manager = ModelManager(
    model_dir=os.environ.get("MODEL_DIR", "../models")
)

# Routes
@app.get("/")
async def root():
    """Root endpoint that returns API information"""
    return {
        "name": "PhishGuard API", 
        "version": "1.0.0",
        "status": "active",
        "models_loaded": model_manager.get_loaded_models()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "models_loaded": len(model_manager.get_loaded_models())}

@app.post("/api/v1/check", response_model=PredictionResponse)
async def check_url(request: URLCheckRequest):
    """Check if a URL is potentially a phishing website"""
    url = str(request.url)
    logger.info(f"Received check request for URL: {url}")
    
    # If we don't have models loaded, return mock response
    loaded_models = model_manager.get_loaded_models()
    logger.info(f"Loaded models: {loaded_models}")
    
    if len(loaded_models) == 0:
        logger.warning("No models loaded. Returning mock response.")
        return PredictionResponse(
            url=url,
            is_phishing=False,
            confidence=0.5,
            message="Mock response - no models loaded"
        )
    
    try:
        # Extract features from URL
        url_features_dict = extract_url_features(url)
        logger.info(f"Extracted features: {url_features_dict}")
        
        # URL Model Prediction
        url_prediction = None
        url_features_vector = None
        if "url_model" in model_manager.models:
            # Get feature names for the URL model
            url_feature_names = model_manager.model_features.get("url_model", [])
            logger.info(f"Model features: {url_feature_names[:5]}... (showing first 5)")
            
            # Convert features to the format expected by the model
            url_features_vector = convert_features_to_model_input(url_features_dict, url_feature_names)
            logger.info(f"Feature vector length: {len(url_features_vector)}")
            
            # Get prediction
            is_phishing, url_prediction = model_manager.predict("url_model", url_features_vector)
            logger.info(f"URL model prediction: {url_prediction:.4f} (is phishing: {is_phishing})")
        else:
            # No URL model available
            is_phishing = False
            url_prediction = 0.5
            logger.warning("URL model not available. Using default prediction.")
        
        # Get feature importance if available
        features_contribution = []
        if url_features_vector is not None:
            features_contribution = model_manager.get_feature_contributions(
                "url_model", url_features_vector, top_n=5
            )
            logger.info(f"Feature contributions: {features_contribution}")
        
        return PredictionResponse(
            url=url,
            is_phishing=is_phishing,
            confidence=url_prediction,
            features_contribution=features_contribution
        )
    
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        logger.exception("Full exception details:")
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")

@app.post("/api/v1/feedback")
async def submit_feedback(feedback: Dict):
    """Endpoint for users to submit feedback (e.g., false positives)"""
    logger.info(f"Received feedback: {feedback}")
    # TODO: Save feedback data for future model improvements
    return {"status": "received", "message": "Thank you for your feedback"}

# Load models at startup
@app.on_event("startup")
async def startup_event():
    """Load models when the API starts"""
    success = model_manager.load_models()
    if success:
        logger.info(f"Successfully loaded models: {model_manager.get_loaded_models()}")
    else:
        logger.warning("Failed to load any models. API will run with mock responses.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 