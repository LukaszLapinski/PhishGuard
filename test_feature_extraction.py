import sys
import os
import json

# Add API directory to path so we can import from it
sys.path.append('./api')

try:
    # Import the feature extraction functions from API
    from feature_extraction import extract_url_features, convert_features_to_model_input, URL_MODEL_FEATURES
    
    HAS_IMPORTS = True
except ImportError as e:
    print(f"Error importing API modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    HAS_IMPORTS = False

# Test URLs
TEST_URLS = [
    # Known legitimate sites
    "https://www.google.com",
    # Potentially suspicious sites
    "http://google-secure-login.com",
    # Suspicious URL patterns
    "http://paypal.com.signin.myaccount.info",
    # URLs with suspicious components
    "http://login.bank.com@phishing-site.com"
]

def check_feature_integrity(features_dict, url):
    """Check if the extracted features have the expected structure"""
    issues = []
    
    # Check for empty features
    if not features_dict:
        issues.append("Features dictionary is empty")
        return issues
    
    # Check expected feature count
    if hasattr(sys.modules['feature_extraction'], 'URL_MODEL_FEATURES'):
        expected_features = URL_MODEL_FEATURES
        if len(expected_features) != len(features_dict):
            issues.append(f"Feature count mismatch: got {len(features_dict)}, expected {len(expected_features)}")
            
            # Find missing features
            missing = set(expected_features) - set(features_dict.keys())
            if missing:
                issues.append(f"Missing features: {', '.join(list(missing)[:5])}...")
                
            # Find extra features
            extra = set(features_dict.keys()) - set(expected_features)
            if extra:
                issues.append(f"Extra features: {', '.join(list(extra)[:5])}...")
    
    # Check for NaN or None values
    nan_features = [k for k, v in features_dict.items() if v is None or (isinstance(v, float) and str(v).lower() == 'nan')]
    if nan_features:
        issues.append(f"Found NaN or None values in features: {', '.join(nan_features[:5])}...")
    
    return issues

def test_url_features(url):
    """Extract and test features for a single URL"""
    print(f"\nTesting URL: {url}")
    
    try:
        # Extract features
        features_dict = extract_url_features(url)
        
        # Check feature integrity
        issues = check_feature_integrity(features_dict, url)
        
        if issues:
            print("⚠️ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Feature extraction looks good")
        
        # Display some feature values
        print(f"\nSample features:")
        
        important_features = [
            'length_url', 'has_ip', 'has_at_symbol', 'redirect_in_path',
            'prefix_suffix', 'has_sub_domain', 'domain_length', 'tld',
            'has_https', 'has_suspicious_tld', 'has_digits'
        ]
        
        for feature in important_features:
            if feature in features_dict:
                print(f"  {feature}: {features_dict[feature]}")
        
        # Try to convert to model input
        if 'convert_features_to_model_input' in globals() and 'URL_MODEL_FEATURES' in globals():
            vector = convert_features_to_model_input(features_dict, URL_MODEL_FEATURES)
            print(f"\n✅ Successfully converted to model input vector (length: {len(vector)})")
        
        return features_dict
    except Exception as e:
        print(f"❌ Error extracting features: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    if not HAS_IMPORTS:
        print("Cannot run tests without required imports")
        return
    
    print("="*60)
    print("TESTING URL FEATURE EXTRACTION")
    print("="*60)
    
    success_count = 0
    
    for url in TEST_URLS:
        features = test_url_features(url)
        if features:
            success_count += 1
        print("-"*60)
    
    print(f"\nTEST SUMMARY: Successfully extracted features for {success_count}/{len(TEST_URLS)} URLs")
    
    # Save a sample of features to a JSON file for inspection
    if success_count > 0:
        sample_url = TEST_URLS[0]
        sample_features = extract_url_features(sample_url)
        
        with open('sample_features.json', 'w') as f:
            json.dump({
                'url': sample_url,
                'features': sample_features
            }, f, indent=2)
            
        print(f"\nSaved sample features to sample_features.json")

if __name__ == "__main__":
    main() 