import pandas as pd
import numpy as np
import os
from sklearn.utils import resample
from imblearn.over_sampling import SMOTE
import argparse

def balance_by_undersampling(df, target_column='label', random_state=42):
    """
    Balance dataset by undersampling the majority class
    """
    # Separate majority and minority classes
    df_majority = df[df[target_column] == 0.0]
    df_minority = df[df[target_column] == 1.0]
    
    # Undersample majority class
    df_majority_undersampled = resample(
        df_majority, 
        replace=False,
        n_samples=len(df_minority),
        random_state=random_state
    )
    
    # Combine minority class with undersampled majority class
    df_balanced = pd.concat([df_majority_undersampled, df_minority])
    
    return df_balanced.sample(frac=1, random_state=random_state).reset_index(drop=True)

def balance_by_oversampling(df, target_column='label', random_state=42):
    """
    Balance dataset by oversampling the minority class using random duplication
    """
    # Separate majority and minority classes
    df_majority = df[df[target_column] == 0.0]
    df_minority = df[df[target_column] == 1.0]
    
    # Oversample minority class
    df_minority_oversampled = resample(
        df_minority, 
        replace=True,
        n_samples=len(df_majority),
        random_state=random_state
    )
    
    # Combine oversampled minority class with majority class
    df_balanced = pd.concat([df_majority, df_minority_oversampled])
    
    return df_balanced.sample(frac=1, random_state=random_state).reset_index(drop=True)

def balance_by_smote(df, target_column='label', random_state=42):
    """
    Balance dataset using SMOTE (Synthetic Minority Over-sampling Technique)
    """
    # Separate features and target
    X = df.drop(target_column, axis=1)
    y = df[target_column]
    
    # Remove non-numeric columns for SMOTE
    non_numeric_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
    numeric_X = X.drop(non_numeric_cols, axis=1)
    
    # Apply SMOTE
    smote = SMOTE(random_state=random_state)
    X_smote, y_smote = smote.fit_resample(numeric_X, y)
    
    # Create a new balanced dataframe
    df_balanced = pd.DataFrame(X_smote, columns=numeric_X.columns)
    df_balanced[target_column] = y_smote
    
    # Add back non-numeric columns (for columns like 'url')
    # This is a simplification - in production you might need a more sophisticated approach
    if non_numeric_cols:
        # For each non-numeric column, we need to map back the original values
        # But since SMOTE creates synthetic samples, we'll use the original values for now
        minority_samples = df[df[target_column] == 1.0]
        majority_samples = df[df[target_column] == 0.0]
        
        for col in non_numeric_cols:
            # For original samples, use their original non-numeric values
            # For synthetic samples, randomly sample from minority class
            original_count = len(majority_samples)
            synthetic_count = len(df_balanced) - original_count
            
            majority_values = majority_samples[col].values
            minority_values = np.random.choice(
                minority_samples[col].values, 
                size=synthetic_count, 
                replace=True
            )
            
            df_balanced[col] = np.concatenate([majority_values, minority_values])
    
    return df_balanced.sample(frac=1, random_state=random_state).reset_index(drop=True)

def balance_by_hybrid(df, target_column='label', undersample_ratio=0.5, random_state=42):
    """
    Balance dataset using a hybrid approach:
    1. Undersample the majority class to a specified ratio
    2. Oversample the minority class to match the undersampled majority
    """
    # Separate majority and minority classes
    df_majority = df[df[target_column] == 0.0]
    df_minority = df[df[target_column] == 1.0]
    
    # Undersample majority class to a certain ratio
    new_majority_count = int(len(df_majority) * undersample_ratio)
    df_majority_undersampled = resample(
        df_majority, 
        replace=False,
        n_samples=new_majority_count,
        random_state=random_state
    )
    
    # Oversample minority class to match the undersampled majority
    df_minority_oversampled = resample(
        df_minority, 
        replace=True,
        n_samples=new_majority_count,
        random_state=random_state
    )
    
    # Combine undersampled majority and oversampled minority
    df_balanced = pd.concat([df_majority_undersampled, df_minority_oversampled])
    
    return df_balanced.sample(frac=1, random_state=random_state).reset_index(drop=True)

def main(input_file, output_dir, method='hybrid', target_column='label', random_state=42):
    """
    Main function to balance the dataset
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load the dataset
    print(f"Loading dataset from {input_file}...")
    df = pd.read_csv(input_file)
    
    # Display class distribution before balancing
    print("\nClass distribution before balancing:")
    print(df[target_column].value_counts())
    print(f"Class distribution percentage: {df[target_column].value_counts(normalize=True) * 100}")
    
    # Balance the dataset based on the chosen method
    print(f"\nBalancing dataset using {method} method...")
    if method == 'undersample':
        balanced_df = balance_by_undersampling(df, target_column, random_state)
    elif method == 'oversample':
        balanced_df = balance_by_oversampling(df, target_column, random_state)
    elif method == 'smote':
        balanced_df = balance_by_smote(df, target_column, random_state)
    elif method == 'hybrid':
        balanced_df = balance_by_hybrid(df, target_column, 0.5, random_state)
    else:
        raise ValueError(f"Unknown balancing method: {method}")
    
    # Display class distribution after balancing
    print("\nClass distribution after balancing:")
    print(balanced_df[target_column].value_counts())
    print(f"Class distribution percentage: {balanced_df[target_column].value_counts(normalize=True) * 100}")
    
    # Save the balanced dataset
    output_file = os.path.join(output_dir, f"metadata_balanced_{method}.csv")
    balanced_df.to_csv(output_file, index=False)
    print(f"\nSaved balanced dataset to {output_file}")
    
    # Split the balanced dataset into train/val/test
    from sklearn.model_selection import train_test_split
    
    # Extract features and target
    X = balanced_df.drop(target_column, axis=1)
    y = balanced_df[target_column]
    
    # Split into train+val and test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    
    # Split train+val into train and validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.2, random_state=random_state, stratify=y_train_val
    )
    
    # Create dataframes
    train_df = pd.concat([X_train, pd.Series(y_train, name=target_column)], axis=1)
    val_df = pd.concat([X_val, pd.Series(y_val, name=target_column)], axis=1)
    test_df = pd.concat([X_test, pd.Series(y_test, name=target_column)], axis=1)
    
    # Save the splits
    train_df.to_csv(os.path.join(output_dir, f"metadata_balanced_{method}_train.csv"), index=False)
    val_df.to_csv(os.path.join(output_dir, f"metadata_balanced_{method}_val.csv"), index=False)
    test_df.to_csv(os.path.join(output_dir, f"metadata_balanced_{method}_test.csv"), index=False)
    
    print(f"Saved train split with {len(train_df)} samples")
    print(f"Saved validation split with {len(val_df)} samples")
    print(f"Saved test split with {len(test_df)} samples")
    
    return balanced_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Balance metadata dataset for phishing detection")
    parser.add_argument(
        "--input_file", 
        type=str, 
        default="datasets/metadata_data_cleaned.csv",
        help="Path to the input dataset CSV file"
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="datasets/balanced",
        help="Directory to save balanced data"
    )
    parser.add_argument(
        "--method", 
        type=str, 
        default="hybrid",
        choices=["undersample", "oversample", "smote", "hybrid"],
        help="Method to use for balancing the dataset"
    )
    parser.add_argument(
        "--target_column", 
        type=str, 
        default="label",
        help="Column containing the target variable"
    )
    parser.add_argument(
        "--random_state", 
        type=int, 
        default=42,
        help="Random state for reproducibility"
    )
    
    args = parser.parse_args()
    
    main(
        args.input_file,
        args.output_dir,
        args.method,
        args.target_column,
        args.random_state
    )