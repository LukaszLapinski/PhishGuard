# PhishGuard - AI-Powered Phishing Detection Extension

PhishGuard is a browser extension that uses advanced machine learning to detect and protect against phishing websites in real-time.

## Features

- **Real-time URL Analysis**: Automatically scans websites as you browse
- **Visual Warnings**: Clear, non-intrusive alerts when potential threats are detected
- **Detailed Explanations**: See exactly why a site was flagged as suspicious
- **Customizable Settings**: Adjust detection sensitivity and notification preferences
- **Feedback Mechanism**: Report false positives to help improve the model
- **Low Resource Usage**: Efficient design with minimal performance impact

## Installation

### Chrome/Edge/Brave Installation (Developer Mode)

1. Download or clone this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top-right corner
4. Click "Load unpacked" and select the `extension` folder from this repository
5. The PhishGuard extension should now appear in your extensions list and toolbar

### Firefox Installation (Temporary Add-on)

1. Download or clone this repository
2. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`
3. Click "Load Temporary Add-on"
4. Navigate to the repository and select the `manifest.json` file in the `extension` folder
5. The PhishGuard extension should now appear in your toolbar

## Usage

- **Automatic Protection**: PhishGuard works automatically in the background while you browse
- **Status Indicator**: Click the PhishGuard icon to see the safety status of the current site
- **Custom Scanning**: Use the "Scan Page Again" button to force a new analysis of the current page
- **Settings**: Access settings by clicking the extension icon and selecting "Settings"

## How It Works

PhishGuard uses a stacking ensemble of machine learning models to analyze URLs and website content:

1. **URL Analysis**: Examines URL structure, domain characteristics, and suspicious patterns
2. **Content Analysis**: Checks page content and behavior for phishing indicators
3. **Brand Impersonation Detection**: Identifies attempts to mimic legitimate brands
4. **Meta-Model**: Combines all signals to provide a final risk assessment

All analysis happens through a secure API connection to our model servers.

## Privacy

PhishGuard respects your privacy:

- Only URLs and minimal page data are sent to our servers for analysis
- No personal information is collected
- Analysis data is not stored long-term
- All connections are encrypted

You can disable data collection in the settings.

## Development

### Setting up for development

1. Clone the repository
2. Make your changes to the code
3. Load the extension in developer mode as described in the installation section

### Project Structure

- `manifest.json` - Extension configuration
- `js/` - JavaScript files
  - `background.js` - Background service worker
  - `content.js` - Content script for page interaction
  - `popup.js` - Popup UI functionality
  - `options.js` - Settings page functionality
- `pages/` - HTML pages
  - `popup.html` - Extension popup UI
  - `options.html` - Settings page
- `images/` - Extension icons and images
- `css/` - Stylesheets

## Credits

- Built with advanced machine learning using stacking ensemble techniques
- Icons from [Material Design Icons](https://material.io/resources/icons/)
- Special thanks to our beta testers

## License

[MIT License](LICENSE)

---

For questions, feedback, or support, please open an issue on our GitHub repository. 