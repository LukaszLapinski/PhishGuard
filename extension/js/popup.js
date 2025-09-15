// Elements
const loadingEl = document.getElementById('loading');
const contentEl = document.getElementById('content');
const urlEl = document.getElementById('url');
const safeSectionEl = document.getElementById('status-safe');
const dangerSectionEl = document.getElementById('status-danger');
const unknownSectionEl = document.getElementById('status-unknown');
const confidenceEl = document.getElementById('confidence');
const confidenceFillEl = document.getElementById('confidence-fill');
const confidenceTextEl = document.getElementById('confidence-text');
const detailsButtonEl = document.getElementById('details-button');
const reportButtonEl = document.getElementById('report-button');
const scanButtonEl = document.getElementById('scan-button');
const optionsButtonEl = document.getElementById('options-button');

// Default state
let currentUrl = '';
let analysisResult = null;

// Initialize the popup
document.addEventListener('DOMContentLoaded', async () => {
  try {
    // Get the current tab's URL
    const tabs = await chrome.tabs.query({active: true, currentWindow: true});
    if (tabs.length === 0) {
      showUnknownStatus('No active tab found');
      return;
    }
    
    const tab = tabs[0];
    currentUrl = tab.url;
    
    // Skip non-http URLs
    if (!currentUrl.startsWith('http')) {
      showUnknownStatus('Non-web page (browser page or local file)');
      return;
    }
    
    // Display the URL
    urlEl.textContent = currentUrl;
    
    // Check if we have a cached result
    chrome.runtime.sendMessage(
      {action: 'checkCurrentUrl'},
      (response) => {
        if (response) {
          // Show the result
          analysisResult = response;
          updateResultDisplay(analysisResult);
        } else {
          // Unknown status
          showUnknownStatus('Analysis in progress or not available');
        }
      }
    );
  } catch (error) {
    showUnknownStatus(`Error: ${error.message}`);
  }
});

// Function to update the display based on the analysis result
function updateResultDisplay(result) {
  // Hide loading indicator, show content
  loadingEl.style.display = 'none';
  contentEl.style.display = 'block';
  
  // Reset previous state
  safeSectionEl.style.display = 'none';
  dangerSectionEl.style.display = 'none';
  unknownSectionEl.style.display = 'none';
  confidenceEl.style.display = 'none';
  detailsButtonEl.style.display = 'none';
  reportButtonEl.style.display = 'none';
  
  // If there's no result or error
  if (!result) {
    showUnknownStatus('No analysis result available');
    return;
  }
  
  // If there's an error in the result
  if (result.error) {
    showUnknownStatus(result.error);
    return;
  }
  
  // Set confidence display if available
  if (typeof result.confidence === 'number') {
    const confidencePercent = Math.round(result.confidence * 100);
    confidenceFillEl.style.width = `${confidencePercent}%`;
    confidenceTextEl.textContent = `${confidencePercent}%`;
    confidenceEl.style.display = 'block';
  }
  
  // Determine status display based on result
  if (result.is_phishing && result.confidence > 0.7) {
    // High confidence phishing
    dangerSectionEl.style.display = 'flex';
    detailsButtonEl.style.display = 'flex';
  } else if (result.is_phishing && result.confidence > 0.3) {
    // Medium confidence phishing
    dangerSectionEl.querySelector('h2').textContent = 'Suspicious Website';
    dangerSectionEl.querySelector('p').textContent = 'This site has some suspicious characteristics';
    dangerSectionEl.style.display = 'flex';
    detailsButtonEl.style.display = 'flex';
    reportButtonEl.style.display = 'flex';
  } else if (result.is_phishing) {
    // Low confidence phishing
    dangerSectionEl.querySelector('h2').textContent = 'Potentially Suspicious';
    dangerSectionEl.querySelector('p').textContent = 'Some minor suspicious patterns detected';
    dangerSectionEl.style.display = 'flex';
    reportButtonEl.style.display = 'flex';
  } else {
    // Not phishing
    safeSectionEl.style.display = 'flex';
    reportButtonEl.style.display = 'flex';
  }
}

// Function to show unknown status
function showUnknownStatus(reason) {
  loadingEl.style.display = 'none';
  contentEl.style.display = 'block';
  
  // Reset previous state
  safeSectionEl.style.display = 'none';
  dangerSectionEl.style.display = 'none';
  confidenceEl.style.display = 'none';
  detailsButtonEl.style.display = 'none';
  reportButtonEl.style.display = 'none';
  
  // Set the unknown status reason
  unknownSectionEl.querySelector('p').textContent = reason || 'Unable to analyze this website';
  unknownSectionEl.style.display = 'flex';
  
  // Get the current tab's URL if not already set
  if (!currentUrl) {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      if (tabs.length > 0) {
        currentUrl = tabs[0].url;
        urlEl.textContent = currentUrl;
      }
    });
  } else {
    urlEl.textContent = currentUrl;
  }
}

// Button event listeners
scanButtonEl.addEventListener('click', () => {
  // Reset the display
  loadingEl.style.display = 'flex';
  contentEl.style.display = 'none';
  
  // Request a new scan
  chrome.runtime.sendMessage(
    {action: 'checkCurrentUrl'},
    (response) => {
      if (response) {
        // Show the new result
        analysisResult = response;
        updateResultDisplay(analysisResult);
      } else {
        // Unknown status
        showUnknownStatus('Analysis in progress or not available');
      }
    }
  );
});

detailsButtonEl.addEventListener('click', () => {
  // Request to show the full details in the page
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    if (tabs.length > 0) {
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'showWarning',
        data: analysisResult
      });
    }
  });
  
  // Close the popup
  window.close();
});

reportButtonEl.addEventListener('click', () => {
  // Determine if this is a false positive or false negative
  const isFalsePositive = analysisResult && analysisResult.is_phishing;
  const userNote = prompt('Please provide any additional information about this site:');
  
  if (userNote !== null) {  // User didn't cancel the prompt
    chrome.runtime.sendMessage({
      action: 'submitFeedback',
      url: currentUrl,
      isFalsePositive: isFalsePositive,
      userNote: userNote
    }, (response) => {
      if (response && response.error) {
        alert(`Error submitting feedback: ${response.error}`);
      } else {
        alert('Thank you for your feedback. This will help improve our detection model.');
      }
    });
  }
});

optionsButtonEl.addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
}); 