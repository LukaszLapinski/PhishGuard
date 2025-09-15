import pandas as pd
import numpy as np
import os
import pickle
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import argparse
import tldextract
import urllib.parse
import re
import string
from collections import Counter
import math

# Try to import Levenshtein, install if not available
try:
    import Levenshtein
except ImportError:
    print("Levenshtein package not found. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "python-Levenshtein"])
    import Levenshtein

# Common brands for detecting brand impersonation
COMMON_BRANDS = [
    'google', 'facebook', 'apple', 'microsoft', 'amazon', 'netflix', 'paypal',
    'ebay', 'instagram', 'twitter', 'linkedin', 'yahoo', 'adobe', 'dropbox'
]

def extract_url_parts(url):
    """Extract components from URL"""
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

def calculate_entropy(text):
    """Calculate Shannon entropy of text"""
    if not text:
        return 0
    
    counter = Counter(text)
    entropy = 0
    for count in counter.values():
        p = count / len(text)
        entropy -= p * math.log2(p)
    return entropy

def check_brand_impersonation(domain):
    """Check for similarity to common brand names"""
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

def extract_char_features(text):
    """Extract character-based features from text"""
    if not text:
        return {
            'length': 0,
            'digit_ratio': 0,
            'special_char_ratio': 0,
            'uppercase_ratio': 0,
            'has_ip_pattern': 0,
            'consecutive_digits': 0,
            'entropy': 0
        }
    
    length = len(text)
    digit_count = sum(c.isdigit() for c in text)
    special_chars = sum(c in string.punctuation for c in text)
    uppercase_count = sum(c.isupper() for c in text)
    
    # IP pattern check
    has_ip_pattern = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text) else 0
    
    # Count consecutive digits
    max_consecutive_digits = 0
    current_consecutive_digits = 0
    
    for c in text:
        if c.isdigit():
            current_consecutive_digits += 1
        else:
            current_consecutive_digits = 0
            
        max_consecutive_digits = max(max_consecutive_digits, current_consecutive_digits)
    
    # Calculate entropy
    entropy = calculate_entropy(text)
    
    return {
        'length': length,
        'digit_ratio': digit_count / length if length > 0 else 0,
        'special_char_ratio': special_chars / length if length > 0 else 0,
        'uppercase_ratio': uppercase_count / length if length > 0 else 0,
        'has_ip_pattern': has_ip_pattern,
        'consecutive_digits': max_consecutive_digits,
        'entropy': entropy
    }

def check_suspicious_terms(url):
    """Check for suspicious words in URL"""
    url_lower = url.lower()
    suspicious_terms = [
        'login', 'signin', 'verify', 'secure', 'account', 'update', 'confirm',
        'banking', 'paypal', 'password'
    ]
    
    results = {}
    for term in suspicious_terms:
        results[f'contains_{term}'] = 1 if term in url_lower else 0
    
    return results

def extract_all_features(url):
    """Extract all features from a URL"""
    if not isinstance(url, str) or pd.isna(url) or url == '':
        return {f: 0 for f in range(60)}  # Default values for invalid URLs
    
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
    
    # Check for suspicious terms
    suspicious_terms = check_suspicious_terms(url)
    features.update(suspicious_terms)
    
    return features

def process_dataset(df, label_column='status'):
    """Extract features from URLs in dataset"""
    print(f"Processing dataset with {len(df)} URLs...")
    start_time = time.time()
    
    # Extract features for each URL
    features_list = []
    for idx, row in df.iterrows():
        if idx % 500 == 0:
            print(f"Processing URL {idx}/{len(df)}...")
        
        url = row['url']
        features = extract_all_features(url)
        
        # Add label if available
        if label_column in df.columns:
            features[label_column] = row[label_column]
        
        # Add URL for reference
        features['url'] = url
        
        features_list.append(features)
    
    # Create DataFrame from features
    features_df = pd.DataFrame(features_list)
    
    print(f"Feature extraction completed in {time.time() - start_time:.2f} seconds")
    print(f"Extracted {features_df.shape[1]-2} features for {features_df.shape[0]} URLs")
    
    return features_df

def clean_data_for_training(X, y):
    """Clean data and prepare for training"""
    print("Cleaning data for training...")
    
    # Check for NaN values
    nan_count = X.isna().sum()
    nan_percent = (nan_count / len(X)) * 100
    
    # Drop columns with more than 50% NaN values
    cols_to_drop = nan_percent[nan_percent > 50].index.tolist()
    if cols_to_drop:
        print(f"Dropping {len(cols_to_drop)} columns with >50% NaN values")
        X = X.drop(cols_to_drop, axis=1)
    
    # Fill remaining NaN values with 0
    X = X.fillna(0)
    
    # Verify cleaning was successful
    assert not np.isnan(X).any().any(), "Data still contains NaN values"
    assert not np.isinf(X).any().any(), "Data still contains infinite values"
    assert not np.isnan(y).any(), "Labels still contain NaN values"
    
    print(f"Cleaned data shape: {X.shape}")
    return X, y

def train_model(X_train, y_train, X_test, y_test, output_dir):
    """Train and evaluate Random Forest model"""
    print("Training Random Forest model...")
    start_time = time.time()
    
    # Create directories if they don't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a pipeline with standardization and model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    # Train the model
    pipeline.fit(X_train, y_train)
    print(f"Model training completed in {time.time() - start_time:.2f} seconds")
    
    # Evaluate on test set
    print("\nEvaluating model on test set...")
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    
    # Print metrics
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"AUC: {auc:.4f}")
    
    # Create confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Random Forest Confusion Matrix')
    cm_path = os.path.join(output_dir, 'rf_confusion_matrix.png')
    plt.savefig(cm_path)
    print(f"Saved confusion matrix to {cm_path}")
    
    # Get feature importances
    feature_importances = pipeline.named_steps['model'].feature_importances_
    importance_df = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': feature_importances
    }).sort_values('Importance', ascending=False)
    
    # Plot top 20 feature importances
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance', y='Feature', data=importance_df.head(20))
    plt.title('Top 20 Feature Importances')
    plt.tight_layout()
    importance_path = os.path.join(output_dir, 'rf_feature_importance.png')
    plt.savefig(importance_path)
    print(f"Saved feature importance plot to {importance_path}")
    
    # Save important features list
    importance_df.to_csv(os.path.join(output_dir, 'feature_importances.csv'), index=False)
    
    # Save metrics
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc
    }
    
    with open(os.path.join(output_dir, 'metrics.txt'), 'w') as f:
        for metric, value in metrics.items():
            f.write(f"{metric}: {value:.4f}\n")
    
    # Save the model
    model_path = os.path.join(output_dir, 'rf_url_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"Model saved to {model_path}")
    
    return pipeline, metrics

def main(train_data_path, test_data_path, output_dir, balanced=False, label_column='status'):
    """Main function to train URL phishing model"""
    print(f"Training URL phishing detection model with data from {train_data_path}")
    
    # Load datasets
    print("Loading datasets...")
    
    if balanced:
        train_data_path = train_data_path.replace('.csv', '_balanced_hybrid.csv')
        test_data_path = test_data_path.replace('.csv', '_balanced_hybrid_test.csv')
        label_column = 'label'  # Balanced datasets use 'label'
        
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    print(f"Training set: {len(train_df)} samples")
    print(f"Test set: {len(test_df)} samples")
    
    # Detect the label column
    if label_column not in train_df.columns:
        potential_labels = ['label', 'status', 'phishing', 'is_phishing']
        for col in potential_labels:
            if col in train_df.columns:
                label_column = col
                print(f"Using '{label_column}' as the target column")
                break
        else:
            raise ValueError(f"No suitable label column found. Checked: {potential_labels}")
    
    # Extract features
    train_features = process_dataset(train_df, label_column=label_column)
    test_features = process_dataset(test_df, label_column=label_column)
    
    # Save extracted features
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    train_features.to_csv(os.path.join(output_dir, 'url_features_train.csv'), index=False)
    test_features.to_csv(os.path.join(output_dir, 'url_features_test.csv'), index=False)
    
    # Prepare data for training
    X_train = train_features.drop(['url', label_column], axis=1)
    y_train = train_features[label_column].values
    
    X_test = test_features.drop(['url', label_column], axis=1)
    y_test = test_features[label_column].values
    
    # Clean data
    X_train_clean, y_train_clean = clean_data_for_training(X_train, y_train)
    X_test_clean, y_test_clean = clean_data_for_training(X_test, y_test)
    
    # Ensure same features in train and test
    common_features = list(set(X_train_clean.columns) & set(X_test_clean.columns))
    X_train_clean = X_train_clean[common_features]
    X_test_clean = X_test_clean[common_features]
    
    # Train model
    model, metrics = train_model(X_train_clean, y_train_clean, X_test_clean, y_test_clean, output_dir)
    
    print("\nURL model training complete!")
    return model, metrics
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train URL phishing detection model')
    parser.add_argument('--train', type=str, default='datasets/split/new_url_data_train.csv',
                       help='Path to training data CSV')
    parser.add_argument('--test', type=str, default='datasets/split/new_url_data_test.csv',
                       help='Path to test data CSV')
    parser.add_argument('--output', type=str, default='models/url',
                       help='Output directory for model files')
    parser.add_argument('--balanced', action='store_true',
                       help='Use balanced dataset versions')
    parser.add_argument('--label', type=str, default='status',
                       help='Name of the label column in the dataset')
    
    args = parser.parse_args()
    
    main(args.train, args.test, args.output, args.balanced, args.label) 