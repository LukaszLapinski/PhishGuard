import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from urllib.parse import urlparse
import re

def extract_domain_features(url):
    """Extract domain related features from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        return {
            'domain_length': len(domain),
            'subdomain_count': domain.count('.'),
            'is_ip': 1 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain) else 0,
            'has_suspicious_tld': 1 if not domain.endswith(('.com', '.org', '.net', '.edu', '.gov')) else 0
        }
    except:
        return {
            'domain_length': 0,
            'subdomain_count': 0,
            'is_ip': 0,
            'has_suspicious_tld': 0
        }

def extract_url_features(url):
    """Extract features from URL"""
    try:
        return {
            'url_length': len(url),
            'protocol_https': 1 if url.startswith('https://') else 0,
            'has_www': 1 if '.www.' in url or url.startswith('www.') else 0,
            'digit_ratio': sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0,
            'special_char_ratio': sum(not c.isalnum() for c in url) / len(url) if len(url) > 0 else 0,
            'num_dots': url.count('.'),
            'num_hyphens': url.count('-'),
            'num_at': url.count('@'),
            'num_percent': url.count('%'),
            'num_ampersand': url.count('&'),
            'num_underscore': url.count('_'),
            'has_suspicious_words': 1 if any(word in url.lower() for word in [
                'login', 'secure', 'account', 'verify', 'signin', 'bank', 'update',
                'confirm', 'password', 'wallet', 'alert'
            ]) else 0
        }
    except:
        return {
            'url_length': 0,
            'protocol_https': 0,
            'has_www': 0,
            'digit_ratio': 0,
            'special_char_ratio': 0,
            'num_dots': 0,
            'num_hyphens': 0,
            'num_at': 0,
            'num_percent': 0,
            'num_ampersand': 0,
            'num_underscore': 0,
            'has_suspicious_words': 0
        }

def process_metadata_dataset(data_path, output_dir, create_splits=True, plot_distributions=True, create_validation=True, scale_features=True):
    """
    Process the interim_metadata_39000.csv for metadata-based phishing detection
    
    Args:
        data_path: Path to the interim_metadata_39000.csv file
        output_dir: Directory to save processed data
        create_splits: Whether to create train/val/test splits
        plot_distributions: Whether to generate distribution plots
        create_validation: Whether to create a validation set or just train/test
        scale_features: Whether to create scaled versions of the features
    """
    # Create output directories
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    processed_dir = os.path.join(output_dir, 'processed')
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    
    # Load the dataset
    print(f"Loading metadata dataset from {data_path}...")
    try:
        df = pd.read_csv(data_path)
        print(f"Loaded dataset with shape: {df.shape}")
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nColumns:")
        print(df.columns.tolist())
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
    # Check for missing values and assess the data
    missing_count = df.isnull().sum()
    print("\nMissing values per column:")
    print(missing_count[missing_count > 0])
    
    # Drop rows with missing labels
    if 'label' in df.columns:
        # Save original count
        original_count = len(df)
        
        # Drop rows with NaN labels
        df = df.dropna(subset=['label'])
        print(f"\nAfter dropping rows with missing labels: {len(df)} rows (removed {original_count - len(df)} rows)")
        
        # Convert labels to numeric if needed
        if df['label'].dtype != 'int64':
            try:
                df['label'] = pd.to_numeric(df['label'], errors='coerce')
                df = df.dropna(subset=['label'])
                print(f"Converted labels to numeric: {len(df)} rows")
            except:
                print("Warning: Could not convert all labels to numeric.")
        
        # Show label distribution
        print("\nLabel distribution:")
        label_counts = df['label'].value_counts()
        print(label_counts)
        print(f"Percentage: {df['label'].value_counts(normalize=True) * 100}")
        
        # Plot distribution if requested
        if plot_distributions:
            plt.figure(figsize=(10, 6))
            sns.countplot(x='label', data=df)
            plt.title('Distribution of Phishing vs Legitimate URLs (Metadata Dataset)')
            plt.xlabel('Label (0: Legitimate, 1: Phishing)')
            plt.ylabel('Count')
            plt.xticks(ticks=[0, 1], labels=['Legitimate (0)', 'Phishing (1)'])
            plot_path = os.path.join(output_dir, 'metadata_label_distribution.png')
            plt.savefig(plot_path)
            print(f"Saved distribution plot to {plot_path}")
    else:
        print("Warning: No 'label' column found in the dataset")
        return None
    
    # Extract URL-based features
    print("\nExtracting features from URLs...")
    
    # Initialize new columns
    domain_features = ['domain_length', 'subdomain_count', 'is_ip', 'has_suspicious_tld']
    url_features = ['url_length', 'protocol_https', 'has_www', 'digit_ratio', 
                   'special_char_ratio', 'num_dots', 'num_hyphens', 'num_at',
                   'num_percent', 'num_ampersand', 'num_underscore', 'has_suspicious_words']
    
    for feature in domain_features + url_features:
        df[feature] = 0
    
    # Extract features for each URL
    for idx, row in df.iterrows():
        if idx % 5000 == 0:
            print(f"Processing row {idx}...")
        
        if 'url' in row and pd.notna(row['url']):
            url = row['url']
            
            # Extract domain features
            domain_feat = extract_domain_features(url)
            for key, value in domain_feat.items():
                df.loc[idx, key] = value
            
            # Extract URL features
            url_feat = extract_url_features(url)
            for key, value in url_feat.items():
                df.loc[idx, key] = value
    
    # Handle existing metadata columns - convert to numeric where possible
    metadata_columns = [
        'ssl_version', 'ssl_cipher', 'cert_expires', 'cert_issuer',
        'server', 'content_type', 'last_modified', 'response_time',
        'status_code', 'redirect_count', 'meta_tags_count',
        'social_links_count', 'contact_info_count', 'has_copyright'
    ]
    
    for col in metadata_columns:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"Converted {col} to numeric")
            except:
                print(f"Could not convert {col} to numeric")
    
    # Calculate additional features
    if 'ssl_version' in df.columns:
        df['has_ssl'] = df['ssl_version'].notna().astype(int)
        print("Added 'has_ssl' feature")
    
    if 'cert_expires' in df.columns:
        df['has_cert'] = df['cert_expires'].notna().astype(int)
        print("Added 'has_cert' feature")
    
    # Define core feature columns
    feature_columns = [
        # Metadata columns
        'response_time', 'status_code', 'redirect_count', 
        'meta_tags_count', 'social_links_count', 'contact_info_count', 
        'has_copyright', 
        # URL features
        'url_length', 'protocol_https', 'has_www', 'digit_ratio', 
        'special_char_ratio', 'num_dots', 'num_hyphens', 'num_at',
        'num_percent', 'num_ampersand', 'num_underscore', 'has_suspicious_words',
        # Domain features
        'domain_length', 'subdomain_count', 'is_ip', 'has_suspicious_tld'
    ]
    
    # Add calculated features if they exist
    if 'has_ssl' in df.columns:
        feature_columns.append('has_ssl')
    if 'has_cert' in df.columns:
        feature_columns.append('has_cert')
    
    # Keep only feature columns that exist in the data
    feature_columns = [col for col in feature_columns if col in df.columns]
    print(f"\nUsing {len(feature_columns)} features: {feature_columns}")
    
    # Create a copy of the features dataframe and reset index
    df = df.reset_index(drop=True)  # Reset the index to avoid indexing issues in splitting
    features_df = df[feature_columns + ['label', 'url']]
    
    # Fill missing values in feature columns
    print("\nImputing missing values...")
    
    # Select only numeric columns for imputation
    numeric_features = features_df[feature_columns].select_dtypes(include=[np.number])
    
    if not numeric_features.empty:
        imputer = SimpleImputer(strategy='mean')
        features_array = imputer.fit_transform(numeric_features)
        
        # Replace original values with imputed values
        features_df[numeric_features.columns] = features_array
    
    # Create scaled version if requested
    if scale_features:
        print("\nNormalizing features...")
        numeric_features = features_df[feature_columns].select_dtypes(include=[np.number])
        
        if not numeric_features.empty:
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(numeric_features)
            
            # Create new DataFrame with scaled features
            features_scaled_df = features_df.copy()
            features_scaled_df[numeric_features.columns] = features_scaled
            
            print(f"Created scaled features dataset with shape: {features_scaled_df.shape}")
    
    # Save the cleaned and processed dataset
    clean_path = os.path.join(output_dir, 'metadata_data_cleaned.csv')
    features_df.to_csv(clean_path, index=False)
    print(f"Saved cleaned dataset to {clean_path}")
    
    # Create train/test splits (and validation if requested)
    if create_splits:
        if create_validation:
            print("\nSplitting data into train (64%), validation (16%), and test (20%) sets...")
            
            # Extract features and labels
            X = features_df.drop('label', axis=1) 
            y = features_df['label']
            
            # First split: separate test set (80% train+val, 20% test)
            X_train_val, X_test, y_train_val, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Second split: separate validation set (80% train, 20% val = 64% train, 16% val overall)
            X_train, X_val, y_train, y_val = train_test_split(
                X_train_val, y_train_val, test_size=0.2, random_state=42, stratify=y_train_val
            )
            
            # Combine features and labels
            train_df = pd.concat([X_train, y_train.reset_index(drop=True)], axis=1)
            val_df = pd.concat([X_val, y_val.reset_index(drop=True)], axis=1)
            test_df = pd.concat([X_test, y_test.reset_index(drop=True)], axis=1)
            
            # Save the splits
            train_path = os.path.join(processed_dir, 'metadata_train.csv')
            val_path = os.path.join(processed_dir, 'metadata_val.csv')
            test_path = os.path.join(processed_dir, 'metadata_test.csv')
            
            train_df.to_csv(train_path, index=False)
            val_df.to_csv(val_path, index=False)
            test_df.to_csv(test_path, index=False)
            
            print(f"Training set: {len(train_df)} samples ({len(train_df)/len(features_df):.1%})")
            print(f"Validation set: {len(val_df)} samples ({len(val_df)/len(features_df):.1%})")
            print(f"Test set: {len(test_df)} samples ({len(test_df)/len(features_df):.1%})")
            
            # Also save scaled versions if available
            if scale_features:
                # Apply the same scaling to the split datasets
                X_train_scaled = pd.DataFrame(
                    scaler.transform(X_train[numeric_features.columns]), 
                    columns=numeric_features.columns
                )
                
                X_val_scaled = pd.DataFrame(
                    scaler.transform(X_val[numeric_features.columns]),
                    columns=numeric_features.columns
                )
                
                X_test_scaled = pd.DataFrame(
                    scaler.transform(X_test[numeric_features.columns]),
                    columns=numeric_features.columns
                )
                
                # Add non-numeric columns back
                for col in X_train.columns:
                    if col not in numeric_features.columns:
                        X_train_scaled[col] = X_train[col].values
                        X_val_scaled[col] = X_val[col].values
                        X_test_scaled[col] = X_test[col].values
                
                # Add labels
                train_scaled_df = pd.concat([X_train_scaled, y_train.reset_index(drop=True)], axis=1)
                val_scaled_df = pd.concat([X_val_scaled, y_val.reset_index(drop=True)], axis=1)
                test_scaled_df = pd.concat([X_test_scaled, y_test.reset_index(drop=True)], axis=1)
                
                # Save scaled versions
                train_scaled_path = os.path.join(processed_dir, 'metadata_train_scaled.csv')
                val_scaled_path = os.path.join(processed_dir, 'metadata_val_scaled.csv')
                test_scaled_path = os.path.join(processed_dir, 'metadata_test_scaled.csv')
                
                train_scaled_df.to_csv(train_scaled_path, index=False)
                val_scaled_df.to_csv(val_scaled_path, index=False)
                test_scaled_df.to_csv(test_scaled_path, index=False)
                
                print(f"Saved scaled training data to {train_scaled_path}")
                print(f"Saved scaled validation data to {val_scaled_path}")
                print(f"Saved scaled test data to {test_scaled_path}")
        else:
            # Just train/test split without validation
            print("\nSplitting data into train (80%) and test (20%) sets...")
            
            # Extract features and labels
            X = features_df.drop('label', axis=1)
            y = features_df['label']
            
            # Create train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Combine features and labels
            train_df = pd.concat([X_train, y_train.reset_index(drop=True)], axis=1)
            test_df = pd.concat([X_test, y_test.reset_index(drop=True)], axis=1)
            
            # Save the splits
            train_path = os.path.join(processed_dir, 'metadata_train.csv')
            test_path = os.path.join(processed_dir, 'metadata_test.csv')
            
            train_df.to_csv(train_path, index=False)
            test_df.to_csv(test_path, index=False)
            
            print(f"Training set: {len(train_df)} samples ({len(train_df)/len(features_df):.1%})")
            print(f"Test set: {len(test_df)} samples ({len(test_df)/len(features_df):.1%})")
            
            # Also save scaled versions if available
            if scale_features:
                # Apply the same scaling to the split datasets
                X_train_scaled = pd.DataFrame(
                    scaler.transform(X_train[numeric_features.columns]),
                    columns=numeric_features.columns
                )
                
                X_test_scaled = pd.DataFrame(
                    scaler.transform(X_test[numeric_features.columns]),
                    columns=numeric_features.columns
                )
                
                # Add non-numeric columns back
                for col in X_train.columns:
                    if col not in numeric_features.columns:
                        X_train_scaled[col] = X_train[col].values
                        X_test_scaled[col] = X_test[col].values
                
                # Add labels
                train_scaled_df = pd.concat([X_train_scaled, y_train.reset_index(drop=True)], axis=1)
                test_scaled_df = pd.concat([X_test_scaled, y_test.reset_index(drop=True)], axis=1)
                
                # Save scaled versions
                train_scaled_path = os.path.join(processed_dir, 'metadata_train_scaled.csv')
                test_scaled_path = os.path.join(processed_dir, 'metadata_test_scaled.csv')
                
                train_scaled_df.to_csv(train_scaled_path, index=False)
                test_scaled_df.to_csv(test_scaled_path, index=False)
                
                print(f"Saved scaled training data to {train_scaled_path}")
                print(f"Saved scaled test data to {test_scaled_path}")
    
    # Save feature names
    with open(os.path.join(processed_dir, 'metadata_features.txt'), 'w') as f:
        for feature in feature_columns:
            f.write(f"{feature}\n")
    
    print("\nMetadata dataset processing complete!")
    return features_df

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process metadata dataset for phishing detection')
    parser.add_argument('--data_path', type=str, default='datasets/interim_metadata_39000.csv',
                        help='Path to the metadata dataset CSV file')
    parser.add_argument('--output_dir', type=str, default='datasets',
                        help='Directory to save processed data')
    parser.add_argument('--no_splits', action='store_false', dest='create_splits',
                        help='Do not create dataset splits')
    parser.add_argument('--no_validation', action='store_false', dest='create_validation',
                        help='Create only train/test split without validation set')
    parser.add_argument('--no_scaling', action='store_false', dest='scale_features',
                        help='Do not create scaled versions of the features')
    parser.add_argument('--no_plots', action='store_false', dest='plot_distributions',
                        help='Do not generate distribution plots')
    
    args = parser.parse_args()
    
    process_metadata_dataset(
        data_path=args.data_path,
        output_dir=args.output_dir,
        create_splits=args.create_splits,
        create_validation=args.create_validation,
        scale_features=args.scale_features,
        plot_distributions=args.plot_distributions
    )