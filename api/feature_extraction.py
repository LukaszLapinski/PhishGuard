import re
import tldextract
import math
import string
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

def extract_url_features(url: str) -> Dict[str, Any]:
    """
    Extract comprehensive features from a URL
    Based on the URL feature engineering used during model training
    
    Args:
        url: The URL to extract features from
        
    Returns:
        Dictionary of features
    """
    try:
        features = {}
        
        # Parse URL components
        parsed_url = urlparse(url)
        extracted = tldextract.extract(url)
        
        # Basic component extraction
        domain = extracted.domain
        subdomain = extracted.subdomain
        tld = extracted.suffix
        path = parsed_url.path
        query = parsed_url.query
        fragment = parsed_url.fragment
        
        # 1. URL Structure Features
        features["url_length"] = len(url)
        features["domain_length"] = len(domain) if domain else 0
        features["subdomain_length"] = len(subdomain) if subdomain else 0
        features["tld_length"] = len(tld) if tld else 0
        features["path_length"] = len(path) if path else 0
        features["query_length"] = len(query) if query else 0
        features["fragment_length"] = len(fragment) if fragment else 0
        
        # 2. Special character counts
        features["dots_count"] = url.count('.')
        features["hyphens_count"] = url.count('-')
        features["underscores_count"] = url.count('_')
        features["slashes_count"] = url.count('/')
        features["question_marks_count"] = url.count('?')
        features["equal_signs_count"] = url.count('=')
        features["at_symbols_count"] = url.count('@')
        features["ampersands_count"] = url.count('&')
        features["exclamations_count"] = url.count('!')
        features["spaces_count"] = url.count(' ')
        features["tildes_count"] = url.count('~')
        features["commas_count"] = url.count(',')
        features["plus_count"] = url.count('+')
        features["asterisk_count"] = url.count('*')
        features["hashtag_count"] = url.count('#')
        features["dollar_sign_count"] = url.count('$')
        features["percent_count"] = url.count('%')
        
        # 3. Domain Analysis Features
        features["has_subdomain"] = len(subdomain) > 0
        features["subdomain_depth"] = subdomain.count('.') + 1 if subdomain else 0
        features["has_https"] = url.startswith("https://")
        features["has_http"] = url.startswith("http://")
        features["has_www"] = subdomain == "www" or subdomain.startswith("www.")
        
        # 4. Path Analysis
        features["path_depth"] = path.count('/') if path else 0
        features["has_query"] = len(query) > 0
        features["query_param_count"] = len(parse_qs(query))
        
        # 5. IP Patterns and Suspicious Elements
        features["has_ip_pattern"] = bool(re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url))
        features["has_hex_chars"] = bool(re.search(r'%[0-9a-fA-F]{2}', url))
        
        # 6. TLD Analysis
        common_tlds = ["com", "org", "net", "edu", "gov", "io", "co", "info", "biz", "eu"]
        features["tld_is_common"] = tld in common_tlds
        
        # 7. Character Distribution Ratios
        full_domain = f"{subdomain}.{domain}.{tld}" if subdomain else f"{domain}.{tld}"
        features["domain_digit_ratio"] = calculate_digit_ratio(full_domain)
        features["url_digit_ratio"] = calculate_digit_ratio(url)
        features["domain_special_char_ratio"] = calculate_special_char_ratio(full_domain)
        features["url_special_char_ratio"] = calculate_special_char_ratio(url)
        
        # 8. Entropy Calculations (measure of randomness - higher for phishing)
        features["domain_entropy"] = calculate_entropy(domain)
        features["subdomain_entropy"] = calculate_entropy(subdomain) if subdomain else 0
        features["path_entropy"] = calculate_entropy(path) if path else 0
        features["query_entropy"] = calculate_entropy(query) if query else 0
        features["url_entropy"] = calculate_entropy(url)
        
        # 9. Suspicious terms detection
        suspicious_terms = [
            "login", "signin", "verify", "secure", "account", "update", "confirm",
            "banking", "paypal", "password", "credential", "wallet", "alert",
            "purchase", "transaction"
        ]
        
        url_lower = url.lower()
        for term in suspicious_terms:
            features[f"contains_{term}"] = term in url_lower
        
        # 10. Additional Pattern Analysis
        features["consecutive_digits_count"] = len(max(re.findall(r'\d+', url), key=len, default=""))
        features["consecutive_letters_count"] = len(max(re.findall(r'[a-zA-Z]+', url), key=len, default=""))
        
        # Add more feature extraction as needed to match the training features
        
        logger.debug(f"Extracted {len(features)} features from URL: {url}")
        return features
        
    except Exception as e:
        logger.error(f"Error extracting features from URL {url}: {e}")
        # Return basic empty features to avoid runtime errors
        return {"url_length": len(url), "error": str(e)}

def calculate_digit_ratio(text: str) -> float:
    """Calculate the ratio of digits to total characters"""
    if not text:
        return 0
    digit_count = sum(c.isdigit() for c in text)
    return digit_count / len(text)

def calculate_special_char_ratio(text: str) -> float:
    """Calculate the ratio of special characters to total characters"""
    if not text:
        return 0
    # Consider all non-alphanumeric as special
    special_count = sum(not c.isalnum() for c in text)
    return special_count / len(text)

def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of text"""
    if not text:
        return 0
    
    # Calculate frequency of each character
    char_count = {}
    for char in text:
        char_count[char] = char_count.get(char, 0) + 1
    
    # Calculate entropy
    entropy = 0
    text_len = len(text)
    for count in char_count.values():
        probability = count / text_len
        entropy -= probability * math.log2(probability)
    
    return entropy

def fetch_content_features(url: str) -> Dict[str, Any]:
    """
    Fetch and extract features from website content
    
    Args:
        url: The URL to fetch content from
        
    Returns:
        Dictionary of content-based features
    """
    # Note: This is a placeholder. The actual implementation would:
    # 1. Fetch the webpage content (HTML)
    # 2. Extract relevant features like:
    #    - HTML attributes (forms, inputs, iframes)
    #    - JavaScript usage
    #    - External links and redirects
    #    - SSL/TLS certificate information
    #    - Text content analysis
    
    # For now, return empty features
    logger.warning(f"Content feature extraction not fully implemented for {url}")
    return {
        "has_password_input": False,
        "has_external_scripts": False,
        "has_iframe": False,
        "has_form": False,
        "redirect_count": 0,
        "external_resource_count": 0
    }

def convert_features_to_model_input(features: Dict[str, Any], 
                                   feature_names: List[str]) -> List[float]:
    """
    Convert feature dictionary to the format expected by the trained model
    
    Args:
        features: Dictionary of features
        feature_names: List of feature names in the order expected by the model
        
    Returns:
        List of feature values in the correct order
    """
    # Create a vector with the features in the correct order
    feature_vector = []
    for name in feature_names:
        # Use 0.0 as default for missing features
        feature_vector.append(float(features.get(name, 0.0)))
    
    return feature_vector

# List of feature names in the order expected by the model
# This will be replaced with the actual feature names from the trained model
URL_MODEL_FEATURES = [
    "url_length", "domain_length", "subdomain_length", "tld_length",
    "path_length", "query_length", "domain_digit_ratio", "url_digit_ratio",
    "domain_special_char_ratio", "url_special_char_ratio", "domain_entropy",
    "subdomain_entropy", "path_entropy", "query_entropy", "url_entropy"
] 