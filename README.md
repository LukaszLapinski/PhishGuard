# PhishGuard

A comprehensive phishing website detection system that combines machine learning models with browser extension capabilities to protect users from malicious websites.

## Features

- Machine Learning Models: Pre-trained models for phishing detection
- Browser Extension: Chrome extension for real-time protection  
- API Service: RESTful API for integration with other applications
- Feature Extraction: Advanced URL and website feature analysis
- Model Testing: Comprehensive testing and evaluation tools
- Documentation: Detailed technical documentation and reports

## Project Structure

```
PhishGuard/
├── api/                 # API service implementation
├── datasets/            # Training and testing datasets
├── extension/           # Browser extension files
├── models/              # Trained ML models
├── notebooks/           # Jupyter notebooks for analysis
├── docs/                # Project documentation
├── check_model.py       # Model validation and analysis
├── test_api.py          # API testing utilities
├── test_feature_extraction.py  # Feature extraction testing
└── sample_features.json # Sample feature data
```

## Installation

### Prerequisites

- Python 3.8+
- Required Python packages (install via pip):
  ```bash
  pip install scikit-learn pandas numpy joblib
  ```

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd PhishGuard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download pre-trained models (if available) or train new ones

## Usage

### Model Testing

Test the trained models:
```bash
python check_model.py
```

### API Testing

Test the API endpoints:
```bash
python test_api.py
```

### Feature Extraction Testing

Test the feature extraction pipeline:
```bash
python test_feature_extraction.py
```

## Configuration

- Model paths can be configured in the respective test files
- API endpoints and settings are configurable in the `api/` directory
- Extension settings can be modified in the `extension/` directory

## Model Performance

The system includes comprehensive evaluation metrics and performance analysis tools. Check the `docs/` directory for detailed performance reports and model comparisons.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Contact

For questions or support, please refer to the project documentation or create an issue in the repository.

---

Note: This project is part of academic research and should be used responsibly. Always verify the security implications before deploying in production environments. 