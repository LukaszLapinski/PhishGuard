# PhishGuard

A comprehensive phishing website detection system that combines machine learning models with browser extension capabilities to protect users from malicious websites.

## Features

- **Machine Learning Models**: Pre-trained Random Forest model for URL-based phishing detection
- **Browser Extension**: Chrome/Edge/Brave extension for real-time protection  
- **REST API**: FastAPI-based backend service for integration
- **Advanced Feature Extraction**: 65+ engineered URL features including entropy analysis and brand impersonation detection
- **Model Testing**: Comprehensive testing and validation tools
- **Academic Research**: Complete ML pipeline with performance analysis

## Project Structure

```
PhishGuard/
├── api/                    # FastAPI backend service
│   ├── app.py             # Main API application
│   ├── model_manager.py   # ML model loading and prediction
│   ├── feature_extraction.py # URL feature engineering
│   └── run.py             # API server runner
├── extension/              # Browser extension (Chrome/Edge/Brave)
│   ├── manifest.json      # Extension configuration
│   ├── js/                # JavaScript files
│   ├── pages/             # HTML pages (popup, options)
│   └── images/            # Extension icons
├── models/                 # Trained ML models
│   └── url/               # URL detection model
│       ├── rf_url_model.pkl # Random Forest model
│       ├── metrics.txt    # Model performance metrics
│       └── feature_importances.csv
├── datasets/               # Training and testing datasets
│   ├── balanced/          # Balanced dataset versions
│   ├── processed/         # Processed feature datasets
│   └── split/             # Train/validation/test splits
├── notebooks/              # Data processing and training scripts
│   ├── train_url_model.py # Main model training script
│   └── preprocess_*.py    # Data preprocessing scripts
├── check_model.py         # Model validation and analysis
├── test_api.py            # API testing utilities
├── test_feature_extraction.py # Feature extraction testing
└── sample_features.json   # Sample feature data
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome, Edge, or Brave browser (for extension)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PhishGuard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the trained model:**
   The system includes a pre-trained Random Forest model at `models/url/rf_url_model.pkl` (34MB). This model is ready to use immediately. If you want to train your own model, you can use the provided training scripts with the included sample datasets.

## Usage

### 1. API Service

Start the API server:
```bash
cd api
python run.py
```

The API will be available at `http://localhost:8000` by default.

**API Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `POST /api/v1/check` - Check URL for phishing
- `POST /api/v1/feedback` - Submit feedback

### 2. Browser Extension

1. Open Chrome/Edge/Brave and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension` folder
4. The PhishGuard extension will appear in your toolbar

The extension automatically scans URLs as you browse and shows warnings for suspicious sites.

### 3. Model Training

Train a new model using the included sample datasets:
```bash
python notebooks/train_url_model.py --train datasets/split/url_data_train.csv --test datasets/split/url_data_test.csv --output models/url
```

**Note**: The repository includes smaller sample datasets for training. For full-scale training with larger datasets, you may need to download additional data sources.

### 4. Testing

Test the API:
```bash
python test_api.py
```

Test feature extraction:
```bash
python test_feature_extraction.py
```

Validate model:
```bash
python check_model.py
```

## Model Performance

The trained Random Forest model achieves:
- **Accuracy**: 93.47%
- **Precision**: 91.17%
- **Recall**: 97.05%
- **F1-Score**: 94.02%
- **AUC**: 98.14%

## Technical Details

### Feature Engineering

The system extracts 65+ features from URLs including:
- URL structure analysis (length, components, special characters)
- Domain analysis (entropy, brand impersonation detection)
- Suspicious pattern detection
- Character distribution ratios
- Entropy calculations for randomness detection

### API Configuration

Environment variables:
- `HOST`: API host (default: 0.0.0.0)
- `PORT`: API port (default: 8000)
- `MODEL_DIR`: Model directory (default: ../models)

### Extension Configuration

The extension can be configured through the options page:
- Enable/disable automatic checking
- Adjust detection sensitivity
- Configure notification preferences

## Development

### Adding New Features

1. **New URL features**: Add to `api/feature_extraction.py`
2. **New models**: Extend `api/model_manager.py`
3. **Extension features**: Modify files in `extension/js/`

### Training New Models

1. Prepare your dataset in CSV format with `url` and `status` columns
2. Use `notebooks/train_url_model.py` to train
3. Place the trained model at `models/url/rf_url_model.pkl`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of academic research and should be used responsibly. Always verify the security implications before deploying in production environments.

## Contact

For questions or support, please refer to the project documentation or create an issue in the repository.
