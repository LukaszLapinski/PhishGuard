// API endpoint where our model is hosted
const API_ENDPOINT = 'http://localhost:8000/api/v1/check';
const API_FEEDBACK_ENDPOINT = 'http://localhost:8000/api/v1/feedback';

// Threshold for phishing detection - now using class 0 probability which is high for phishing sites
const DEFAULT_THRESHOLD = 0.95;  // Changed to match high class 0 probability

// Cache for already checked URLs (with expiration)
const urlCache = {};
const CACHE_EXPIRATION = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

// Listen for navigation events to check URLs
chrome.webNavigation.onCommitted.addListener(async (details) => {
  // Only process main frame navigation (not iframes, etc)
  if (details.frameId !== 0) return;
  
  const url = details.url;
  
  // Skip browser internal pages, extension pages, etc.
  if (!url.startsWith('http')) return;
  
  // Check if user has opted out of automatic checking
  const settings = await chrome.storage.sync.get({
    enableAutoCheck: true,
    checkingThreshold: DEFAULT_THRESHOLD
  });
  
  if (!settings.enableAutoCheck) {
    console.log('Automatic checking disabled by user');
    return;
  }
  
  // Check if we've already analyzed this URL recently
  if (urlCache[url] && urlCache[url].timestamp > Date.now() - CACHE_EXPIRATION) {
    handleResult(url, urlCache[url].data, settings.checkingThreshold);
    return;
  }
  
  // Check the URL against our phishing detection API
  try {
    await checkUrl(url, settings.checkingThreshold);
  } catch (error) {
    console.error('Error checking URL:', error);
  }
});

// Function to call our API
async function checkUrl(url, threshold = DEFAULT_THRESHOLD) {
  try {
    // Prepare the request body
    const requestData = {
      url: url
    };
    
    console.log(`Checking URL: ${url}`);
    
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });
    
    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Cache the result with timestamp
    urlCache[url] = {
      data: result,
      timestamp: Date.now()
    };
    
    // Handle the result (show warnings if needed)
    handleResult(url, result, threshold);
    
    return result;
    
  } catch (error) {
    console.error('Error in API call:', error);
    // Cache the error to avoid repeated failed requests
    urlCache[url] = {
      data: { 
        is_phishing: false, 
        confidence: 0, 
        error: error.message,
        url: url
      },
      timestamp: Date.now()
    };
    return urlCache[url].data;
  }
}

// Function to handle the phishing detection result
function handleResult(url, result, threshold = DEFAULT_THRESHOLD) {
  // Add debug logging
  console.log('Phishing detection result:', {
    url: url,
    is_phishing: result.is_phishing,
    confidence: result.confidence,
    threshold: threshold,
    willShowWarning: result.is_phishing && result.confidence > threshold
  });
  
  // Set icon based on result
  updateIcon(url, result);
  
  // If the site is potentially dangerous
  if (result.is_phishing && result.confidence > threshold) {
    // Show a warning to the user
    chrome.tabs.query({url: url}, (tabs) => {
      if (tabs.length > 0) {
        // Send message to content script to show warning
        console.log('Sending warning to content script for tab:', tabs[0].id);
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'showWarning',
          data: {
            confidence: result.confidence,
            reasons: result.features_contribution || [], // If API provides feature importance
            url: url
          }
        });
      }
    });
  }
}

// Update the extension icon based on the result
function updateIcon(url, result) {
  chrome.tabs.query({url: url}, (tabs) => {
    if (tabs.length === 0) return;
    
    let iconPath;
    
    if (result.error) {
      // Error state (couldn't check)
      iconPath = {
        16: '../images/icon16_unknown.png',
        48: '../images/icon48_unknown.png',
        128: '../images/icon128_unknown.png'
      };
    } else if (result.is_phishing) {
      if (result.confidence > 0.9) {
        // High confidence phishing
        iconPath = {
          16: '../images/icon16_danger.png',
          48: '../images/icon48_danger.png',
          128: '../images/icon128_danger.png'
        };
      } else {
        // Medium confidence phishing
        iconPath = {
          16: '../images/icon16_warning.png',
          48: '../images/icon48_warning.png',
          128: '../images/icon128_warning.png'
        };
      }
    } else {
      // Safe site
      iconPath = {
        16: '../images/icon16.png',
        48: '../images/icon48.png',
        128: '../images/icon128.png'
      };
    }
    
    // Update the icon
    chrome.action.setIcon({
      path: iconPath,
      tabId: tabs[0].id
    });
  });
}

// Function to submit feedback about false positives
async function submitFeedback(url, isFalsePositive, userNote = '') {
  try {
    const response = await fetch(API_FEEDBACK_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: url,
        is_false_positive: isFalsePositive,
        user_note: userNote
      }),
    });
    
    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Feedback submitted successfully', result);
    
    // Clear the cache for this URL to force a recheck next time
    if (urlCache[url]) {
      delete urlCache[url];
    }
    
    return result;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw error;
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'checkCurrentUrl') {
    // Get the current tab URL
    chrome.tabs.query({active: true, currentWindow: true}, async (tabs) => {
      if (tabs.length === 0) {
        sendResponse({error: 'No active tab found'});
        return;
      }
      
      const currentUrl = tabs[0].url;
      const tabId = tabs[0].id;
      
      try {
        // Check if we have a cached result
        if (urlCache[currentUrl] && urlCache[currentUrl].timestamp > Date.now() - CACHE_EXPIRATION) {
          sendResponse(urlCache[currentUrl].data);
          return;
        }
        
        // Otherwise, check the URL
        const result = await checkUrl(currentUrl);
        sendResponse(result);
      } catch (error) {
        sendResponse({error: error.message, url: currentUrl});
      }
    });
    
    // Return true to indicate that the response will be sent asynchronously
    return true;
  }
  
  if (message.action === 'submitFeedback') {
    submitFeedback(message.url, message.isFalsePositive, message.userNote)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({error: error.message}));
    
    // Return true to indicate that the response will be sent asynchronously
    return true;
  }
});

// Listen for extension installation or update
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // Set default settings on install
    chrome.storage.sync.set({
      enableAutoCheck: true,
      checkingThreshold: DEFAULT_THRESHOLD
    });
    
    // Maybe open a welcome page
    chrome.tabs.create({
      url: 'pages/welcome.html'
    });
  }
}); 