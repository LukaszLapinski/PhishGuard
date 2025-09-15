import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

def process_content_dataset(data_path, output_dir, create_splits=True, plot_distributions=True):
    """
    Process the PhiUSIIL_Phishing_URL_Dataset.csv for content-based phishing detection
    
    Args:
        data_path: Path to the PhiUSIIL_Phishing_URL_Dataset.csv file
        output_dir: Directory to save processed data
        create_splits: Whether to create train/val/test splits
        plot_distributions: Whether to generate distribution plots
    """
    # Create output directories
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    split_dir = os.path.join(output_dir, 'split')
    if create_splits and not os.path.exists(split_dir):
        os.makedirs(split_dir)
    
    # Load the dataset
    print(f"Loading the content dataset from {data_path}...")
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
    
    # Check for column names and standardize if needed
    # The dataset seems to have 'URL' column but lowercase 'url' is expected in other code
    column_map = {}
    if 'URL' in df.columns and 'url' not in df.columns:
        column_map['URL'] = 'url'
        print("Standardizing column names: 'URL' -> 'url'")
    
    # Rename columns if needed
    if column_map:
        df = df.rename(columns=column_map)
    
    # Drop irrelevant columns (if needed)
    drop_cols = ['FILENAME', 'Title']  # Add more if needed
    cols_to_drop = [col for col in drop_cols if col in df.columns]
    if cols_to_drop:
        print(f"Dropping columns: {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)
    
    # Check for missing values
    missing_count = df.isnull().sum()
    print("\nMissing values per column:")
    print(missing_count[missing_count > 0])
    
    # Remove duplicates
    if 'url' in df.columns:
        dupes_before = len(df)
        df = df.drop_duplicates(subset=['url'])
        dupes_after = len(df)
        print(f"Removed {dupes_before - dupes_after} duplicate URLs. Remaining rows: {dupes_after}")
    
    # Fix label column if needed
    if 'label' in df.columns:
        # Ensure label is numeric
        if df['label'].dtype != 'int64':
            try:
                df['label'] = pd.to_numeric(df['label'])
                print("Converted label column to numeric")
            except:
                # Try to map text values if numeric conversion fails
                if df['label'].dtype == 'object':
                    label_map = {'phishing': 1, 'legitimate': 0, 'Phishing': 1, 'Legitimate': 0}
                    df['label'] = df['label'].map(label_map)
                    print("Mapped text labels to numeric values")
        
        # Show label distribution
        print("\nLabel distribution:")
        print(df['label'].value_counts())
        print(f"Percentage: {df['label'].value_counts(normalize=True) * 100}")
        
        # Plot distribution if requested
        if plot_distributions:
            plt.figure(figsize=(10, 6))
            sns.countplot(x='label', data=df)
            plt.title('Distribution of Phishing vs Legitimate URLs (Content Dataset)')
            plt.xlabel('Label (0: Legitimate, 1: Phishing)')
            plt.ylabel('Count')
            plt.xticks(ticks=[0, 1], labels=['Legitimate (0)', 'Phishing (1)'])
            plot_path = os.path.join(output_dir, 'content_label_distribution.png')
            plt.savefig(plot_path)
            print(f"Saved distribution plot to {plot_path}")
    else:
        print("Warning: No 'label' column found in the dataset")
    
    # Save the cleaned dataset
    clean_path = os.path.join(output_dir, 'content_data_cleaned.csv')
    df.to_csv(clean_path, index=False)
    print(f"Saved cleaned dataset to {clean_path}")
    
    # Create train/val/test splits if requested
    if create_splits and 'label' in df.columns:
        print("\nSplitting data into train (64%), validation (16%), and test (20%) sets...")
        
        # Extract features and labels
        y = df['label']
        X = df.drop('label', axis=1)
        
        # First split: 80% train+val, 20% test
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Second split: 80% train, 20% val (= 64% train, 16% val overall)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val, y_train_val, test_size=0.2, random_state=42, stratify=y_train_val
        )
        
        # Combine features and labels
        train_df = pd.concat([X_train, y_train.reset_index(drop=True)], axis=1)
        val_df = pd.concat([X_val, y_val.reset_index(drop=True)], axis=1)
        test_df = pd.concat([X_test, y_test.reset_index(drop=True)], axis=1)
        
        # Save the splits
        train_path = os.path.join(split_dir, 'content_data_train.csv')
        val_path = os.path.join(split_dir, 'content_data_val.csv')
        test_path = os.path.join(split_dir, 'content_data_test.csv')
        
        train_df.to_csv(train_path, index=False)
        val_df.to_csv(val_path, index=False)
        test_df.to_csv(test_path, index=False)
        
        print(f"Training set: {len(train_df)} samples ({len(train_df)/len(df):.1%})")
        print(f"Validation set: {len(val_df)} samples ({len(val_df)/len(df):.1%})")
        print(f"Test set: {len(test_df)} samples ({len(test_df)/len(df):.1%})")
        print(f"\nSaved training data to {train_path}")
        print(f"Saved validation data to {val_path}")
        print(f"Saved test data to {test_path}")
    
    print("\nContent dataset processing complete!")
    return df

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process PhiUSIIL_Phishing_URL_Dataset.csv dataset for phishing detection')
    parser.add_argument('--data_path', type=str, default='datasets/PhiUSIIL_Phishing_URL_Dataset.csv',
                        help='Path to the PhiUSIIL_Phishing_URL_Dataset.csv file')
    parser.add_argument('--output_dir', type=str, default='datasets',
                        help='Directory to save processed data')
    parser.add_argument('--no_splits', action='store_false', dest='create_splits',
                        help='Do not create train/val/test splits')
    parser.add_argument('--no_plots', action='store_false', dest='plot_distributions',
                        help='Do not generate distribution plots')
    
    args = parser.parse_args()
    
    process_content_dataset(
        data_path=args.data_path,
        output_dir=args.output_dir,
        create_splits=args.create_splits,
        plot_distributions=args.plot_distributions
    ) 