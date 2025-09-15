import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import tldextract
import urllib.parse
import re
import string
from collections import Counter
import math
import time

try:
    import Levenshtein
except ImportError:
    print("Levenshtein package not found. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "python-Levenshtein"])
    import Levenshtein

# FEATURE ENGINEERING FUNCTIONS
# Common brands for detecting brand impersonation
COMMON_BRANDS = [
    'google', 'facebook', 'apple', 'microsoft', 'amazon', 'netflix', 'paypal',
    'ebay', 'instagram', 'twitter', 'linkedin', 'yahoo', 'adobe', 'dropbox',
    'spotify', 'steam', 'github', 'chase', 'wellsfargo', 'bankofamerica', 
    'citi', 'americanexpress', 'mastercard', 'visa', 'discover', 'walmart'
]

# Function to extract TLD, domain, and subdomain
def extract_url_parts(url):
    try:
        # Handle missing protocol
        if not url.startswith('http'):
            url = 'http://' + url
            
        # Extract domain info
        extracted = tldextract.extract(url)
        subdomain = extracted.subdomain
        domain = extracted.domain
        suffix = extracted.suffix
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        
        return {
            'subdomain': subdomain,
            'domain': domain,
            'tld': suffix,
            'path': path,
            'query': query,
            'full_domain': f"{subdomain}.{domain}.{suffix}" if subdomain else f"{domain}.{suffix}"
        }
    except:
        return {
            'subdomain': '',
            'domain': '',
            'tld': '',
            'path': '',
            'query': '',
            'full_domain': ''
        }

# Calculate Shannon entropy
def calculate_entropy(text):
    if not text:
        return 0
    
    counter = Counter(text)
    entropy = 0
    for count in counter.values():
        p = count / len(text)
        entropy -= p * math.log2(p)
    return entropy

# Check for brand impersonation
def check_brand_impersonation(domain):
    domain = domain.lower()
    min_distance = float('inf')
    closest_brand = None
    
    for brand in COMMON_BRANDS:
        distance = Levenshtein.distance(domain, brand)
        if 0 < distance < min_distance and distance <= 3:  # Close but not exact match
            min_distance = distance
            closest_brand = brand
    
    if closest_brand:
        return 1, min_distance, closest_brand
    return 0, 0, None

# Extract character-based features
def extract_char_features(text):
    if not text:
        return {
            'length': 0,
            'digit_ratio': 0,
            'special_char_ratio': 0,
            'uppercase_ratio': 0,
            'has_ip_pattern': 0,
            'consecutive_digits': 0,
            'consecutive_consonants': 0,
            'entropy': 0
        }
    
    length = len(text)
    digit_count = sum(c.isdigit() for c in text)
    special_chars = sum(c in string.punctuation for c in text)
    uppercase_count = sum(c.isupper() for c in text)
    
    # IP pattern (basic check)
    has_ip_pattern = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text) else 0
    
    # Count consecutive digits and consonants
    max_consecutive_digits = 0
    current_consecutive_digits = 0
    max_consecutive_consonants = 0
    current_consecutive_consonants = 0
    consonants = 'bcdfghjklmnpqrstvwxyz'
    
    for c in text.lower():
        if c.isdigit():
            current_consecutive_digits += 1
            current_consecutive_consonants = 0
        elif c in consonants:
            current_consecutive_consonants += 1
            current_consecutive_digits = 0
        else:
            current_consecutive_digits = 0
            current_consecutive_consonants = 0
            
        max_consecutive_digits = max(max_consecutive_digits, current_consecutive_digits)
        max_consecutive_consonants = max(max_consecutive_consonants, current_consecutive_consonants)
    
    # Calculate entropy
    entropy = calculate_entropy(text)
    
    return {
        'length': length,
        'digit_ratio': digit_count / length if length > 0 else 0,
        'special_char_ratio': special_chars / length if length > 0 else 0,
        'uppercase_ratio': uppercase_count / length if length > 0 else 0,
        'has_ip_pattern': has_ip_pattern,
        'consecutive_digits': max_consecutive_digits,
        'consecutive_consonants': max_consecutive_consonants,
        'entropy': entropy
    }

# Check for suspicious terms in URL
def check_suspicious_terms(url):
    url_lower = url.lower()
    suspicious_terms = [
        'login', 'signin', 'verify', 'secure', 'account', 'update', 'confirm',
        'banking', 'paypal', 'password', 'credential', 'wallet', 'alert',
        'purchase', 'transaction'
    ]
    
    results = {}
    for term in suspicious_terms:
        results[f'contains_{term}'] = 1 if term in url_lower else 0
    
    return results

# Extract all features from a URL
def extract_all_features(url):
    if not isinstance(url, str) or pd.isna(url) or url == '':
        # Return default values for invalid URLs
        return {f: 0 for f in range(60)}  # Assuming 60 features total
    
    features = {}
    
    # Get URL parts
    url_parts = extract_url_parts(url)
    
    # Basic URL features
    features['url_length'] = len(url)
    features['domain_length'] = len(url_parts['domain'])
    features['tld_length'] = len(url_parts['tld'])
    features['subdomain_length'] = len(url_parts['subdomain'])
    features['path_length'] = len(url_parts['path'])
    features['query_length'] = len(url_parts['query'])
    
    # Count components
    features['dots_count'] = url.count('.')
    features['digits_count'] = sum(c.isdigit() for c in url)
    features['hyphens_count'] = url.count('-')
    features['at_count'] = url.count('@')
    features['underscore_count'] = url.count('_')
    features['slash_count'] = url.count('/')
    features['questionmark_count'] = url.count('?')
    features['equal_count'] = url.count('=')
    features['ampersand_count'] = url.count('&')
    features['exclamation_count'] = url.count('!')
    features['space_count'] = url.count(' ')
    features['tilde_count'] = url.count('~')
    features['comma_count'] = url.count(',')
    features['plus_count'] = url.count('+')
    features['asterisk_count'] = url.count('*')
    features['hash_count'] = url.count('#')
    features['dollar_count'] = url.count('$')
    features['percent_count'] = url.count('%')
    
    # Domain analysis
    features['has_subdomain'] = 1 if url_parts['subdomain'] else 0
    features['subdomain_depth'] = url_parts['subdomain'].count('.') + 1 if url_parts['subdomain'] else 0
    features['tld_is_common'] = 1 if url_parts['tld'] in ['com', 'org', 'net', 'edu', 'gov', 'co'] else 0
    
    # Path analysis
    features['path_depth'] = url_parts['path'].count('/') if url_parts['path'] else 0
    features['has_query'] = 1 if url_parts['query'] else 0
    features['query_param_count'] = url_parts['query'].count('&') + 1 if url_parts['query'] else 0
    
    # Protocol and security
    features['has_http'] = 1 if url.startswith('http://') else 0
    features['has_https'] = 1 if url.startswith('https://') else 0
    
    # Suspicious patterns
    features['has_www'] = 1 if '.www.' in url or url.startswith('www.') else 0
    features['has_decimal_ip'] = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url) else 0
    features['has_hex_chars'] = 1 if re.search(r'0x[0-9a-fA-F]+', url) else 0
    
    # Brand impersonation
    brand_check = check_brand_impersonation(url_parts['domain'])
    features['brand_impersonation'] = brand_check[0]
    features['brand_edit_distance'] = brand_check[1]
    
    # Character distribution for domain
    domain_chars = extract_char_features(url_parts['domain'])
    for key, value in domain_chars.items():
        features[f'domain_{key}'] = value
    
    # Character distribution for URL
    url_chars = extract_char_features(url)
    for key, value in url_chars.items():
        features[f'url_{key}'] = value
    
    # Entropy for different parts
    features['domain_entropy'] = calculate_entropy(url_parts['domain'])
    features['subdomain_entropy'] = calculate_entropy(url_parts['subdomain'])
    features['path_entropy'] = calculate_entropy(url_parts['path'])
    features['query_entropy'] = calculate_entropy(url_parts['query'])
    features['full_url_entropy'] = calculate_entropy(url)
    
    # Check for suspicious terms
    suspicious_terms = check_suspicious_terms(url)
    features.update(suspicious_terms)
    
    return features

# Process a dataset and extract features
def process_dataset(df, set_name):
    print(f"Processing {set_name} dataset ({len(df)} samples)...")
    start_time = time.time()
    
    # Save original URL and label
    urls = df['url'].values
    
    # Check label column (should be 'status' in new dataset)
    if 'status' in df.columns:
        labels = df['status'].values
    else:
        print("Label column 'status' not found. Available columns:", df.columns.tolist())
        return None
    
    # Extract features for each URL
    print("Extracting features from URLs...")
    features_list = []
    for i, url in enumerate(urls):
        if i % 1000 == 0 and i > 0:
            print(f"Processed {i}/{len(urls)} URLs...")
        
        features = extract_all_features(url)
        features_list.append(features)
    
    # Convert to DataFrame
    features_df = pd.DataFrame(features_list)
    
    # Add original URL and label
    features_df['url'] = urls
    features_df['label'] = labels
    
    # Report on the extracted features
    print(f"Extracted {features_df.shape[1]-2} features from {len(features_df)} URLs")
    print(f"Processing completed in {time.time() - start_time:.2f} seconds")
    
    return features_df

# MAIN PREPROCESSING FUNCTION
def preprocess_url_dataset(data_path, output_dir, create_splits=True, plot_distributions=True):
    """
    Preprocess URL dataset: clean data, extract features, and split into train/val/test sets
    
    Args:
        data_path: Path to the input CSV file (final_url_dataset.csv)
        output_dir: Directory to save processed data
        create_splits: Whether to create train/val/test splits
        plot_distributions: Whether to generate distribution plots
    """
    # Create output directories
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    split_dir = os.path.join(output_dir, 'split')
    engineered_dir = os.path.join(output_dir, 'engineered')
    
    if not os.path.exists(split_dir):
        os.makedirs(split_dir)
    if not os.path.exists(engineered_dir):
        os.makedirs(engineered_dir)
    
    # Load the dataset
    print("Loading the URL dataset...")
    df = pd.read_csv(data_path)
    
    # Display basic information
    print(f"Dataset shape: {df.shape}")
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Check for missing values
    print("\nMissing values:")
    print(df.isnull().sum())
    
    # Check the distribution of labels
    print("\nLabel distribution:")
    label_counts = df['status'].value_counts(normalize=True) * 100
    print(f"Phishing (0): {label_counts.get(0, 0):.2f}%")
    print(f"Legitimate (1): {label_counts.get(1, 0):.2f}%")
    print("\nRaw counts:")
    print(df['status'].value_counts())
    
    # Check for duplicate URLs
    print(f"\nNumber of duplicate URLs: {df.duplicated(subset=['url']).sum()}")
    
    # Remove duplicates if any
    if df.duplicated(subset=['url']).sum() > 0:
        df = df.drop_duplicates(subset=['url'])
        print(f"After removing duplicates: {df.shape[0]} rows")
    
    # Validate URLs (simple check for valid format)
    def is_valid_url(url):
        return isinstance(url, str) and len(url) > 0
    
    valid_urls = df['url'].apply(is_valid_url)
    print(f"\nNumber of invalid URLs: {(~valid_urls).sum()}")
    
    # Filter out invalid URLs if any
    if (~valid_urls).sum() > 0:
        df = df[valid_urls]
        print(f"After removing invalid URLs: {df.shape[0]} rows")
    
    # Plot label distribution if requested
    if plot_distributions:
        plt.figure(figsize=(10, 6))
        sns.countplot(x='status', data=df)
        plt.title('Distribution of Phishing vs Legitimate URLs')
        plt.xlabel('Label (0: Phishing, 1: Legitimate)')
        plt.ylabel('Count')
        plt.xticks([0, 1], ['Phishing (0)', 'Legitimate (1)'])
        plot_path = os.path.join(output_dir, 'label_distribution.png')
        plt.savefig(plot_path)
        print(f"Saved distribution plot to {plot_path}")
    
    # Create clean dataset with raw URLs
    clean_path = os.path.join(output_dir, 'url_data_cleaned.csv')
    df.to_csv(clean_path, index=False)
    print(f"Saved cleaned dataset to {clean_path}")
    
    # If requested, split into train/val/test sets
    if create_splits:
        print("\nSplitting data into train, validation, and test sets (64/16/20)...")
        train_df, temp_df = train_test_split(df, test_size=0.36, random_state=42, stratify=df['status'])
        val_df, test_df = train_test_split(temp_df, test_size=0.55, random_state=42, stratify=temp_df['status'])
        
        print(f"Training set: {len(train_df)} samples")
        print(f"Validation set: {len(val_df)} samples")
        print(f"Test set: {len(test_df)} samples")
        
        # Save the split datasets
        train_path = os.path.join(split_dir, 'url_data_train.csv')
        val_path = os.path.join(split_dir, 'url_data_val.csv')
        test_path = os.path.join(split_dir, 'url_data_test.csv')
        
        train_df.to_csv(train_path, index=False)
        val_df.to_csv(val_path, index=False)
        test_df.to_csv(test_path, index=False)
        
        print(f"\nSaved training data to {train_path}")
        print(f"Saved validation data to {val_path}")
        print(f"Saved test data to {test_path}")
        
        # Extract features from train, val, and test sets
        print("\nExtracting features from train, val, and test sets...")
        train_features = process_dataset(train_df, "training")
        val_features = process_dataset(val_df, "validation")
        test_features = process_dataset(test_df, "test")
        
        # Save engineered feature datasets
        train_features_path = os.path.join(engineered_dir, 'url_features_train.csv')
        val_features_path = os.path.join(engineered_dir, 'url_features_val.csv')
        test_features_path = os.path.join(engineered_dir, 'url_features_test.csv')
        
        train_features.to_csv(train_features_path, index=False)
        val_features.to_csv(val_features_path, index=False)
        test_features.to_csv(test_features_path, index=False)
        
        print(f"\nSaved engineered training features to {train_features_path}")
        print(f"Saved engineered validation features to {val_features_path}")
        print(f"Saved engineered test features to {test_features_path}")
    
    print("\nYour URL dataset has been processed and is ready for model training!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Preprocess URL dataset for phishing detection')
    parser.add_argument('--data_path', type=str, default='datasets/final_url_dataset.csv',
                        help='Path to the input dataset CSV file')
    parser.add_argument('--output_dir', type=str, default='datasets',
                        help='Directory to save processed data')
    parser.add_argument('--no_splits', action='store_false', dest='create_splits',
                        help='Do not create train/val/test splits')
    parser.add_argument('--no_plots', action='store_false', dest='plot_distributions',
                        help='Do not generate distribution plots')
    
    args = parser.parse_args()
    
    preprocess_url_dataset(
        data_path=args.data_path,
        output_dir=args.output_dir,
        create_splits=args.create_splits,
        plot_distributions=args.plot_distributions
    )