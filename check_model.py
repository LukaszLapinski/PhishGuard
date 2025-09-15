import os
import sys
import pickle
import joblib
import numpy as np

def try_load_model(model_path):
    """Attempts to load a model using different methods"""
    print(f"Trying to load model from: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file not found at {model_path}")
        return None
    
    # File exists, get size
    file_size = os.path.getsize(model_path) / (1024 * 1024)  # Size in MB
    print(f"File size: {file_size:.2f} MB")
    
    # Try loading with pickle
    try:
        print("Attempting to load with pickle...")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print("✅ Successfully loaded model with pickle")
        return model, "pickle"
    except Exception as e:
        print(f"❌ Pickle loading failed: {e}")
    
    # Try loading with joblib
    try:
        print("Attempting to load with joblib...")
        model = joblib.load(model_path)
        print("✅ Successfully loaded model with joblib")
        return model, "joblib"
    except Exception as e:
        print(f"❌ Joblib loading failed: {e}")
    
    print("❌ All loading methods failed")
    return None, None

def analyze_model(model):
    """Analyze model properties and structure"""
    print("\n== Model Information ==")
    
    # Basic model type
    model_type = type(model).__name__
    print(f"Model type: {model_type}")
    
    # Check if it's a scikit-learn model
    is_sklearn = hasattr(model, 'predict') and callable(getattr(model, 'predict'))
    print(f"Scikit-learn compatible: {'Yes' if is_sklearn else 'No'}")
    
    # Check for common properties
    if hasattr(model, 'classes_'):
        print(f"Classes: {model.classes_}")
    
    if hasattr(model, 'n_classes_'):
        print(f"Number of classes: {model.n_classes_}")
    
    if hasattr(model, 'n_features_in_'):
        print(f"Number of features: {model.n_features_in_}")
    
    # Check for feature names
    if hasattr(model, 'feature_names_in_'):
        feature_names = model.feature_names_in_
        print(f"Has feature names: Yes ({len(feature_names)} features)")
        print("Sample feature names: ", feature_names[:5].tolist())
    else:
        print("Has feature names: No")
    
    # Check for feature importances
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        print(f"Has feature importances: Yes")
        
        # Print top 5 most important features
        if hasattr(model, 'feature_names_in_'):
            indices = np.argsort(importances)[::-1]
            print("\nTop 5 most important features:")
            for i in range(min(5, len(indices))):
                idx = indices[i]
                if idx < len(model.feature_names_in_):
                    print(f"  {i+1}. {model.feature_names_in_[idx]}: {importances[idx]:.6f}")
    else:
        print("Has feature importances: No")
    
    # Test prediction
    if is_sklearn:
        try:
            # Create a dummy feature vector of zeros
            if hasattr(model, 'n_features_in_'):
                n_features = model.n_features_in_
            else:
                # Guess a large number if we don't know
                n_features = 100  
            
            dummy_features = np.zeros((1, n_features))
            
            print("\nTesting prediction with dummy data...")
            if hasattr(model, 'predict_proba'):
                result = model.predict_proba(dummy_features)
                print(f"predict_proba output shape: {result.shape}")
                print(f"predict_proba result: {result}")
            
            result = model.predict(dummy_features)
            print(f"predict result: {result}")
            print("✅ Prediction successful")
        except Exception as e:
            print(f"❌ Prediction failed: {e}")

def main():
    # Define paths to try
    model_paths = [
        "../models/url/rf_url_model.pkl",
        "../models/rf_url_model.pkl",
        "models/url/rf_url_model.pkl",
        "models/rf_url_model.pkl"
    ]
    
    # Try each path
    for path in model_paths:
        result = try_load_model(path)
        if result:
            model, method = result
            print(f"Model loaded successfully using {method} from {path}")
            analyze_model(model)
            return
    
    print("\n❌ Could not load model from any of the expected paths.")
    print("Please check that the model file exists and is in the correct format.")

if __name__ == "__main__":
    main() 