# PhishGuard API

The PhishGuard API provides machine learning-based detection of phishing websites. It serves as the backend for the PhishGuard browser extension, analyzing URLs to identify potential threats.

## Features

- URL-based phishing detection
- Detailed feature importance explanation
- Feedback collection for model improvement

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Trained URL machine learning model (or API will run in mock mode)

### Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place trained URL model in the `../models` directory:
   - `url_model.joblib`: URL-based detection model

### Running the API

To start the API server:

```bash
cd api
python run.py
```

By default, the server runs on `http://0.0.0.0:8000`. You can customize the host and port using environment variables:

```bash
HOST=127.0.0.1 PORT=5000 python run.py
```

## API Endpoints

### Root Endpoint

```
GET /
```

Returns basic information about the API, including available models.

### Health Check

```
GET /health
```

Returns the health status of the API and the number of loaded models.

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

- `url`: The URL to check

**Response:**

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

## Environment Variables

- `HOST`: Host to run the API server (default: 0.0.0.0)
- `PORT`: Port to run the API server (default: 8000)
- `MODEL_DIR`: Directory containing trained models (default: ../models)

## Deployment Options

### Local Development

Run with the development server:

```bash
python run.py
```

### Production Deployment

For production deployment, consider using:

- Docker for containerization
- Gunicorn as a WSGI server
- Nginx as a reverse proxy

Example Docker deployment:

```bash
docker build -t phishguard-api .
docker run -p 8000:8000 -v /path/to/models:/app/models phishguard-api
```

## Free Hosting Options

The API can be hosted on various free platforms:

1. **Railway**
   - Upload the codebase, set the build command and start command
   - Connect to GitHub for automatic deployments

2. **Render**
   - Create a new Web Service
   - Connect to GitHub or upload directly
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `cd api && uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **Replit**
   - Create a new Python repl
   - Upload the API code
   - Set run command: `cd api && uvicorn app:app --host 0.0.0.0 --port 8080` 