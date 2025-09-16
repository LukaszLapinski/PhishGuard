# PhishGuard API

The PhishGuard API provides machine learning-based detection of phishing websites. It serves as the backend for the PhishGuard browser extension, analyzing URLs to identify potential threats.

## Features

- URL-based phishing detection using Random Forest model
- Detailed feature importance explanation
- Feedback collection for model improvement
- Mock mode when no model is available
- Comprehensive logging and error handling

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Trained Random Forest model (or API will run in mock mode)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Set up the trained model:**
   Place your trained Random Forest model at:
   ```
   ../models/url/rf_url_model.pkl
   ```
   
   The model should be a scikit-learn RandomForestClassifier saved with either pickle or joblib.

### Running the API

Start the API server:
```bash
cd api
python run.py
```

**Default configuration:**
- Host: `0.0.0.0`
- Port: `8000`
- URL: `http://localhost:8000`

**Custom configuration:**
```bash
HOST=127.0.0.1 PORT=5000 python run.py
```

## API Endpoints

### Root Endpoint

```
GET /
```

Returns basic information about the API.

**Response:**
```json
{
  "name": "PhishGuard API",
  "version": "1.0.0",
  "status": "active",
  "models_loaded": ["url_model"]
}
```

### Health Check

```
GET /health
```

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": 1
}
```

### URL Check

```
POST /api/v1/check
```

Checks if a URL is potentially a phishing website.

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

**Response (Normal):**
```json
{
  "url": "https://example.com",
  "is_phishing": false,
  "confidence": 0.12,
  "features_contribution": [
    {
      "name": "url_length",
      "value": 22,
      "importance": 0.15
    },
    {
      "name": "has_https",
      "value": 1,
      "importance": 0.25
    }
  ]
}
```

**Response (Mock Mode - No Model):**
```json
{
  "url": "https://example.com",
  "is_phishing": false,
  "confidence": 0.5,
  "message": "Mock response - no models loaded"
}
```

### Feedback

```
POST /api/v1/feedback
```

Submit feedback about a prediction (e.g., false positive reports).

**Request Body:**
```json
{
  "url": "https://example.com",
  "is_false_positive": true,
  "user_note": "This is a legitimate site"
}
```

**Response:**
```json
{
  "status": "received",
  "message": "Thank you for your feedback"
}
```

## Model Requirements

### Model File Structure

The API expects the following model structure:
```
models/
└── url/
    └── rf_url_model.pkl  # Random Forest model
```

### Model Compatibility

The model should be:
- A scikit-learn RandomForestClassifier
- Saved with either `pickle` or `joblib`
- Trained with the same features as defined in `feature_extraction.py`

### Feature Names

The model should have feature names available through:
- `model.feature_names_in_` (scikit-learn >= 1.0)
- `model.feature_names_` (older versions)
- Or a separate `url_model_features.txt` file

## Environment Variables

- `HOST`: Host to run the API server (default: 0.0.0.0)
- `PORT`: Port to run the API server (default: 8000)
- `MODEL_DIR`: Directory containing trained models (default: ../models)

## Feature Extraction

The API extracts 65+ features from URLs including:

### URL Structure Features
- URL length, domain length, path length
- Special character counts (dots, hyphens, etc.)
- Protocol detection (HTTP/HTTPS)

### Domain Analysis
- Subdomain analysis
- TLD (Top Level Domain) analysis
- Entropy calculations for randomness detection
- Brand impersonation detection using Levenshtein distance

### Suspicious Patterns
- IP address patterns
- Suspicious terms detection
- Character distribution ratios

## Error Handling

The API includes comprehensive error handling:
- Invalid URLs return HTTP 422
- Processing errors return HTTP 500
- Missing models trigger mock mode
- All errors are logged with details

## Logging

The API uses Python's logging module with INFO level by default. Logs include:
- Request details
- Feature extraction results
- Model predictions
- Error details

## Testing

Test the API endpoints:
```bash
# From project root
python test_api.py
```

## Deployment

### Local Development
```bash
python run.py
```

### Production Deployment

For production, consider using:
- **Gunicorn** as WSGI server
- **Nginx** as reverse proxy
- **Docker** for containerization

**Example Docker deployment:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "api/run.py"]
```

### Free Hosting Options

1. **Railway**: Upload codebase, set build/start commands
2. **Render**: Create Web Service, connect to GitHub
3. **Replit**: Create Python repl, upload API code

**Render start command:**
```bash
cd api && uvicorn app:app --host 0.0.0.0 --port $PORT
```
