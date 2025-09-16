# PhishGuard Browser Extension

PhishGuard is a browser extension that uses machine learning to detect and protect against phishing websites in real-time. It works with Chrome, Edge, and Brave browsers.

## Features

- **Real-time URL Analysis**: Automatically scans websites as you browse
- **Visual Warnings**: Clear, non-intrusive alerts when potential threats are detected
- **Confidence Scoring**: Shows detection confidence with visual indicators
- **Feature Explanations**: Displays why a site was flagged as suspicious
- **Customizable Settings**: Adjust detection sensitivity and notification preferences
- **Feedback Mechanism**: Report false positives to help improve the model
- **Caching System**: Efficient design with minimal performance impact
- **Multiple Icon States**: Visual indicators for safe, warning, danger, and unknown states

## Installation

### Chrome/Edge/Brave Installation (Developer Mode)

1. **Download or clone this repository**
2. **Open Chrome/Edge/Brave** and navigate to:
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`
   - Brave: `brave://extensions/`
3. **Enable "Developer mode"** in the top-right corner
4. **Click "Load unpacked"** and select the `extension` folder from this repository
5. **The PhishGuard extension** should now appear in your extensions list and toolbar

### Firefox Installation (Temporary Add-on)

1. **Download or clone this repository**
2. **Open Firefox** and navigate to `about:debugging#/runtime/this-firefox`
3. **Click "Load Temporary Add-on"**
4. **Navigate to the repository** and select the `manifest.json` file in the `extension` folder
5. **The PhishGuard extension** should now appear in your toolbar

## Usage

### Automatic Protection
- PhishGuard works automatically in the background while you browse
- URLs are checked against the machine learning model via API calls
- Results are cached to avoid redundant checks

### Manual Interaction
- **Click the PhishGuard icon** to see the safety status of the current site
- **Use "Scan Page Again"** button to force a new analysis
- **Access settings** by clicking the extension icon and selecting "Settings"

### Visual Indicators
- **Green icon**: Site appears safe
- **Yellow icon**: Site has some suspicious characteristics
- **Red icon**: High confidence phishing detection
- **Gray icon**: Unable to analyze or error state

## How It Works

PhishGuard uses a Random Forest machine learning model to analyze URLs:

1. **URL Monitoring**: Automatically detects when you navigate to a new page
2. **Feature Extraction**: Analyzes URL structure, domain characteristics, and suspicious patterns
3. **ML Prediction**: Sends URL to the API for analysis
4. **Risk Assessment**: Receives confidence score and feature explanations
5. **User Notification**: Shows appropriate warnings based on confidence threshold

All analysis happens through a secure API connection to the PhishGuard model server.

## Configuration

### Settings Page

Access settings through the extension popup:
- **Enable/Disable Auto Check**: Turn automatic scanning on/off
- **Detection Threshold**: Adjust sensitivity (default: 0.95)
- **Notification Preferences**: Customize warning behavior

### API Configuration

The extension connects to the PhishGuard API at:
- **Default**: `http://localhost:8000/api/v1/check`
- **Configurable**: Update `API_ENDPOINT` in `js/background.js`

## Privacy

PhishGuard respects your privacy:

- **Only URLs** are sent to the API for analysis
- **No personal information** is collected
- **No page content** is accessed or transmitted
- **Analysis data** is not stored long-term
- **All connections** are encrypted (HTTPS)
- **Local caching** reduces API calls

You can disable data collection in the settings.

## Project Structure

```
extension/
├── manifest.json          # Extension configuration (Manifest V3)
├── js/                    # JavaScript files
│   ├── background.js      # Background service worker
│   ├── popup.js          # Popup UI functionality
│   └── options.js        # Settings page functionality
├── pages/                 # HTML pages
│   ├── popup.html        # Extension popup UI
│   └── options.html      # Settings page
├── images/               # Extension icons and images
│   ├── icon16.png        # 16x16 icon (safe state)
│   ├── icon48.png        # 48x48 icon (safe state)
│   ├── icon128.png       # 128x128 icon (safe state)
│   ├── icon16_danger.png # 16x16 icon (danger state)
│   ├── icon48_danger.png # 48x48 icon (danger state)
│   └── icon128_danger.png # 128x128 icon (danger state)
└── css/                  # Stylesheets (if any)
```

## Development

### Setting up for Development

1. **Clone the repository**
2. **Make your changes** to the code
3. **Load the extension** in developer mode as described in the installation section
4. **Test your changes** by navigating to different websites

### Key Files

- **`manifest.json`**: Extension configuration, permissions, and metadata
- **`js/background.js`**: Handles URL monitoring, API calls, and icon updates
- **`js/popup.js`**: Manages the popup UI and user interactions
- **`js/options.js`**: Handles settings page functionality
- **`pages/popup.html`**: Popup UI layout and styling
- **`pages/options.html`**: Settings page layout

### API Integration

The extension communicates with the PhishGuard API:
- **URL checking**: `POST /api/v1/check`
- **Feedback submission**: `POST /api/v1/feedback`
- **Error handling**: Graceful fallback when API is unavailable

### Caching System

- **URL cache**: Stores results for 24 hours to avoid redundant API calls
- **Error cache**: Prevents repeated failed requests
- **Cache expiration**: Automatic cleanup of old entries

## Troubleshooting

### Common Issues

1. **Extension not loading**: Check that you're in developer mode
2. **No API responses**: Verify the API server is running at `localhost:8000`
3. **Icons not updating**: Check browser console for JavaScript errors
4. **Settings not saving**: Verify storage permissions in manifest.json

### Debug Mode

Enable debug logging by opening browser developer tools:
- **Chrome**: F12 → Console tab
- **Edge**: F12 → Console tab
- **Brave**: F12 → Console tab

## Permissions

The extension requires these permissions:
- **`activeTab`**: Access current tab information
- **`storage`**: Save user settings and cache
- **`webNavigation`**: Monitor URL changes
- **`scripting`**: Inject content scripts (if needed)
- **`<all_urls>`**: Check all websites

## Browser Compatibility

- **Chrome**: Version 88+ (Manifest V3 support)
- **Edge**: Version 88+ (Chromium-based)
- **Brave**: Version 1.20+ (Chromium-based)
- **Firefox**: Limited support (Manifest V2 compatibility)

## Credits

- Built with machine learning using Random Forest classification
- Icons from [Material Design Icons](https://material.io/resources/icons/)
- API integration with FastAPI backend

## License

This extension is part of the PhishGuard project. See the main project license for details.

---

For questions, feedback, or support, please open an issue on the GitHub repository.
