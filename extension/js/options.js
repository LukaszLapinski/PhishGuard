// Default settings
const defaultSettings = {
  confidenceThreshold: 95, // 0-100, changed to 95 to match the 0.95 threshold
  autoScan: true,
  scanLinks: true,
  showWarnings: true,
  blockNavigation: true,
  warningStyle: 'banner',
  apiUrl: '',
  enableCache: true
};

// DOM elements
const confidenceThresholdEl = document.getElementById('confidence-threshold');
const autoScanEl = document.getElementById('auto-scan');
const scanLinksEl = document.getElementById('scan-links');
const showWarningsEl = document.getElementById('show-warnings');
const blockNavigationEl = document.getElementById('block-navigation');
const warningStyleEl = document.getElementById('warning-style');
const apiUrlEl = document.getElementById('api-url');
const enableCacheEl = document.getElementById('enable-cache');
const saveButtonEl = document.getElementById('save-button');
const resetButtonEl = document.getElementById('reset-button');
const notificationEl = document.getElementById('notification');

// Load settings when the page loads
document.addEventListener('DOMContentLoaded', loadSettings);

// Save settings when the save button is clicked
saveButtonEl.addEventListener('click', saveSettings);

// Reset settings when the reset button is clicked
resetButtonEl.addEventListener('click', resetSettings);

// Function to load settings from storage
function loadSettings() {
  chrome.storage.sync.get(defaultSettings, (settings) => {
    // Apply loaded settings to form elements
    confidenceThresholdEl.value = settings.confidenceThreshold;
    autoScanEl.checked = settings.autoScan;
    scanLinksEl.checked = settings.scanLinks;
    showWarningsEl.checked = settings.showWarnings;
    blockNavigationEl.checked = settings.blockNavigation;
    warningStyleEl.value = settings.warningStyle;
    apiUrlEl.value = settings.apiUrl || '';
    enableCacheEl.checked = settings.enableCache;
  });
}

// Function to save settings to storage
function saveSettings() {
  const settings = {
    confidenceThreshold: parseInt(confidenceThresholdEl.value, 10),
    autoScan: autoScanEl.checked,
    scanLinks: scanLinksEl.checked,
    showWarnings: showWarningsEl.checked,
    blockNavigation: blockNavigationEl.checked,
    warningStyle: warningStyleEl.value,
    apiUrl: apiUrlEl.value.trim(),
    enableCache: enableCacheEl.checked
  };
  
  chrome.storage.sync.set(settings, () => {
    // Notify background script of settings change
    chrome.runtime.sendMessage({
      action: 'settingsUpdated',
      settings: settings
    });
    
    // Show success notification
    notificationEl.style.display = 'block';
    setTimeout(() => {
      notificationEl.style.display = 'none';
    }, 3000);
  });
}

// Function to reset settings to defaults
function resetSettings() {
  if (confirm('Are you sure you want to reset all settings to their default values?')) {
    // Apply default settings to form elements
    confidenceThresholdEl.value = defaultSettings.confidenceThreshold;
    autoScanEl.checked = defaultSettings.autoScan;
    scanLinksEl.checked = defaultSettings.scanLinks;
    showWarningsEl.checked = defaultSettings.showWarnings;
    blockNavigationEl.checked = defaultSettings.blockNavigation;
    warningStyleEl.value = defaultSettings.warningStyle;
    apiUrlEl.value = defaultSettings.apiUrl;
    enableCacheEl.checked = defaultSettings.enableCache;
    
    // Save the default settings
    saveSettings();
  }
} 