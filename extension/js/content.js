// Create and inject warning banner into the page
function showPhishingWarning(data) {
  // If a warning is already shown, don't show another
  if (document.getElementById('phishguard-warning')) {
    return;
  }
  
  // Create the warning element
  const warningEl = document.createElement('div');
  warningEl.id = 'phishguard-warning';
  warningEl.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #ff3b30;
    color: white;
    padding: 20px;
    font-family: Arial, sans-serif;
    z-index: 999999;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  `;
  
  // Format the confidence as a percentage
  const confidencePercent = Math.round(data.confidence * 100);
  
  // Create warning content
  warningEl.innerHTML = `
    <div style="display: flex; align-items: center;">
      <div style="margin-right: 15px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1-7v2h2v-2h-2zm0-8v6h2V7h-2z" fill="white"/>
        </svg>
      </div>
      <div>
        <strong style="font-size: 16px;">Warning: Potential Phishing Website Detected</strong>
        <p style="margin: 5px 0 0;">Our AI model has detected this website as potentially dangerous with ${confidencePercent}% confidence.</p>
      </div>
    </div>
    <div>
      <button id="phishguard-details" style="background: white; color: #ff3b30; border: none; padding: 8px 15px; border-radius: 4px; margin-right: 10px; cursor: pointer;">View Details</button>
      <button id="phishguard-dismiss" style="background: rgba(255, 255, 255, 0.2); color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer;">Proceed Anyway</button>
    </div>
  `;
  
  // Add to page
  document.body.prepend(warningEl);
  
  // Add event listeners
  document.getElementById('phishguard-details').addEventListener('click', () => {
    showDetailsPopup(data);
  });
  
  document.getElementById('phishguard-dismiss').addEventListener('click', () => {
    // Ask the user to confirm they want to proceed
    if (confirm("Are you sure you want to proceed? This website has been detected as potentially malicious.")) {
      warningEl.remove();
      
      // Report this as a potential false positive
      chrome.runtime.sendMessage({
        action: 'reportFalsePositive',
        url: window.location.href
      });
    }
  });
}

// Show more detailed information about why this site was flagged
function showDetailsPopup(data) {
  // If a details popup is already shown, don't show another
  if (document.getElementById('phishguard-details-popup')) {
    return;
  }
  
  // Create the details element
  const detailsEl = document.createElement('div');
  detailsEl.id = 'phishguard-details-popup';
  detailsEl.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 500px;
    max-width: 90%;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    padding: 20px;
    z-index: 1000000;
    font-family: Arial, sans-serif;
  `;
  
  // Build reasons list if available
  let reasonsHtml = '';
  if (data.reasons && data.reasons.length) {
    reasonsHtml = `
      <h3 style="margin: 15px 0 10px;">Suspicious elements detected:</h3>
      <ul style="margin: 0; padding-left: 20px;">
        ${data.reasons.map(reason => `<li style="margin-bottom: 5px;">${reason.feature}: ${reason.importance}</li>`).join('')}
      </ul>
    `;
  } else {
    reasonsHtml = `
      <p>Our model detected suspicious patterns in this URL that match known phishing techniques.</p>
    `;
  }
  
  // Create popup content
  detailsEl.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
      <h2 style="margin: 0; color: #ff3b30;">Phishing Detection Details</h2>
      <button id="phishguard-details-close" style="background: none; border: none; font-size: 20px; cursor: pointer;">×</button>
    </div>
    <p><strong>URL:</strong> ${data.url}</p>
    <p><strong>Confidence:</strong> ${Math.round(data.confidence * 100)}%</p>
    ${reasonsHtml}
    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee;">
      <p style="margin-bottom: 15px;">What should you do?</p>
      <ul style="margin: 0; padding-left: 20px;">
        <li>Leave this website immediately</li>
        <li>Do not enter any personal information</li>
        <li>Do not download any files</li>
        <li>If you entered credentials, change your passwords on legitimate sites</li>
      </ul>
    </div>
    <div style="margin-top: 20px; text-align: right;">
      <button id="phishguard-report-false" style="background: #eee; border: none; padding: 8px 15px; border-radius: 4px; margin-right: 10px; cursor: pointer;">Report False Positive</button>
      <button id="phishguard-details-back" style="background: #ff3b30; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer;">Back to Warning</button>
    </div>
  `;
  
  // Add overlay
  const overlayEl = document.createElement('div');
  overlayEl.id = 'phishguard-overlay';
  overlayEl.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 999999;
  `;
  
  // Add to page
  document.body.appendChild(overlayEl);
  document.body.appendChild(detailsEl);
  
  // Add event listeners
  document.getElementById('phishguard-details-close').addEventListener('click', () => {
    detailsEl.remove();
    overlayEl.remove();
  });
  
  document.getElementById('phishguard-details-back').addEventListener('click', () => {
    detailsEl.remove();
    overlayEl.remove();
  });
  
  document.getElementById('phishguard-report-false').addEventListener('click', () => {
    chrome.runtime.sendMessage({
      action: 'reportFalsePositive',
      url: window.location.href
    }, (response) => {
      alert('Thank you for your feedback. This will help improve our detection model.');
      detailsEl.remove();
      overlayEl.remove();
      document.getElementById('phishguard-warning').remove();
    });
  });
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'showWarning') {
    showPhishingWarning(message.data);
    sendResponse({status: 'warning_shown'});
  }
}); 