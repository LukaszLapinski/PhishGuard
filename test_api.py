import requests
import json
import time
import sys

# API endpoint
API_URL = "http://localhost:8000/api/v1/check"

# Test URLs
TEST_URLS = [
    # Known legitimate sites
    "https://www.google.com",
    "https://www.microsoft.com",
    "https://www.apple.com",
    "https://www.amazon.com",
    
    # Potentially suspicious sites
    "http://google-secure-login.com",
    "http://gooogle.com",
    "http://secure-bank-login.randomdomain.com",
    "http://bit.ly/3exampleonly",
    
    # Suspicious URL patterns
    "http://paypal.com.signin.myaccount.info",
    "http://login.microsoftonline.com.verification.securitycheck.domain.com",
    "http://bankofamerica-secure-login.com",
    "http://amazn.com/signin",
    
    # URLs with suspicious components
    "http://www.secure-bank-access.com/login?token=123&redirect=https://bank.com",
    "http://download.free-security-scan.exe.domain.com",
    "http://login.php?user=test&password=test",
    "http://login.bank.com@phishing-site.com"
]

def test_api_health():
    """Test if the API is up and running"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy. Loaded models: {data.get('models_loaded', 0)}")
            return True
        else:
            print(f"❌ API returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_url(url):
    """Test a single URL against the API"""
    try:
        print(f"\nTesting URL: {url}")
        
        start_time = time.time()
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json={"url": url}
        )
        elapsed_time = time.time() - start_time
        
        print(f"Response time: {elapsed_time:.2f} seconds")
        
        if response.status_code != 200:
            print(f"❌ API returned status code {response.status_code}: {response.text}")
            return None
        
        result = response.json()
        
        # Format and print result
        is_phishing = result.get("is_phishing", False)
        confidence = result.get("confidence", 0)
        
        if is_phishing:
            status = "🚨 PHISHING"
        else:
            status = "✅ SAFE"
            
        print(f"Result: {status} (Confidence: {confidence:.2%})")
        
        # Print feature contributions if available
        features = result.get("features_contribution", [])
        if features:
            print("\nSuspicious features:")
            for feature in features:
                print(f"  - {feature['name']}: {feature['value']} (importance: {feature['importance']:.4f})")
        
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def run_all_tests():
    """Run tests for all URLs"""
    if not test_api_health():
        print("API is not healthy. Cannot run tests.")
        return
    
    print("\n" + "="*60)
    print(f"Running tests for {len(TEST_URLS)} URLs")
    print("="*60)
    
    results = {}
    success_count = 0
    phishing_count = 0
    
    for url in TEST_URLS:
        result = test_url(url)
        if result:
            results[url] = result
            success_count += 1
            if result.get("is_phishing", False):
                phishing_count += 1
        
        print("-"*60)  # Separator between tests
    
    # Summary
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {success_count}/{len(TEST_URLS)} successful, {phishing_count} detected as phishing")
    print("="*60)
    
    # Check if all confidence values are the same
    confidence_values = [r.get("confidence", 0) for r in results.values()]
    if all(c == confidence_values[0] for c in confidence_values):
        print(f"\n⚠️ WARNING: All confidence values are the same ({confidence_values[0]:.2f}).")
        print("This suggests the model might not be properly detecting differences between URLs.")

if __name__ == "__main__":
    run_all_tests() 