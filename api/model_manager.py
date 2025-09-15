import os
import joblib
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import pickle
from sklearn.base import BaseEstimator

logger = logging.getLogger(__name__)

class ModelManager:
    """Class to handle loading and interacting with trained ML models"""
    
    def __init__(self, model_dir: str = "../models"):
        self.model_dir = model_dir
        self.models: Dict[str, Any] = {}
        self.model_features: Dict[str, List[str]] = {}
        self.feature_importances: Dict[str, Dict[str, float]] = {}
    
    def load_models(self) -> bool:
        """
        Load URL model from the model directory
        
        Returns:
            bool: True if the model was loaded successfully
        """
        try:
            # Check if model directory exists
            if not os.path.exists(self.model_dir):
                logger.warning(f"Model directory {self.model_dir} does not exist. Creating it.")
                os.makedirs(self.model_dir)
            
            # Load URL model - look for rf_url_model.pkl in the url subdirectory
            url_model_loaded = self._load_model("url_model", "url/rf_url_model.pkl")
            
            # Load feature names
            self._load_feature_names()
            
            # Extract feature importance for interpretability
            self._extract_feature_importances()
            
            return url_model_loaded
            
        except Exception as e:
            logger.error(f"Error loading URL model: {str(e)}")
            return False
    
    def _load_model(self, model_name: str, filename: str) -> bool:
        """
        Load a specific model from file
        
        Args:
            model_name: Key name for the model
            filename: Filename of the model in the model directory
            
        Returns:
            bool: True if model was loaded successfully
        """
        model_path = os.path.join(self.model_dir, filename)
        
        if os.path.exists(model_path):
            try:
                # Try with joblib first
                self.models[model_name] = joblib.load(model_path)
                logger.info(f"Loaded {model_name} from {model_path} using joblib")
                return True
            except Exception as joblib_error:
                logger.warning(f"Failed to load with joblib: {str(joblib_error)}")
                try:
                    # Try with pickle as fallback
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    logger.info(f"Loaded {model_name} from {model_path} using pickle")
                    return True
                except Exception as pickle_error:
                    logger.error(f"Failed to load {model_name}: {str(pickle_error)}")
                    return False
        else:
            logger.warning(f"Model file {model_path} does not exist")
            return False
    
    def _load_feature_names(self):
        """Load feature names for the URL model from the model file or use defaults"""
        # We only care about the URL model now
        model_name = "url_model"
        
        # Check if model exists
        if model_name not in self.models:
            return
            
        model = self.models[model_name]
        
        # Check if the model has feature_names_in_ attribute (scikit-learn >= 1.0)
        if hasattr(model, 'feature_names_in_'):
            self.model_features[model_name] = model.feature_names_in_.tolist()
        # For older scikit-learn versions or other model types
        elif hasattr(model, 'feature_names_'):
            self.model_features[model_name] = model.feature_names_
        else:
            # If feature names not available in model, try to load from separate file
            feature_names_file = os.path.join(self.model_dir, f"{model_name}_features.txt")
            if os.path.exists(feature_names_file):
                with open(feature_names_file, 'r') as f:
                    self.model_features[model_name] = [line.strip() for line in f]
            else:
                # Use default feature list if everything else fails
                logger.warning(f"Could not find feature names for {model_name}")
                from feature_extraction import URL_MODEL_FEATURES
                self.model_features[model_name] = URL_MODEL_FEATURES
    
    def _extract_feature_importances(self):
        """Extract feature importance from the URL model if available"""
        model_name = "url_model"
        
        # Check if model and feature names exist
        if model_name not in self.models or model_name not in self.model_features:
            return
            
        model = self.models[model_name]
        feature_names = self.model_features[model_name]
        importance_dict = {}
        
        # Extract feature importance based on model type
        try:
            # For tree-based models (Random Forest, XGBoost, etc.)
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                for feature_name, importance in zip(feature_names, importances):
                    importance_dict[feature_name] = float(importance)
            
            # For linear models (LogisticRegression, LinearSVC, etc.)
            elif hasattr(model, 'coef_'):
                coefficients = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
                for feature_name, coef in zip(feature_names, coefficients):
                    importance_dict[feature_name] = abs(float(coef))
                    
            # Save the importance dictionary
            if importance_dict:
                self.feature_importances[model_name] = importance_dict
                logger.info(f"Extracted feature importance for {model_name}")
        except Exception as e:
            logger.warning(f"Could not extract feature importance for {model_name}: {e}")
    
    def predict(self, model_name: str, features: List[float], 
               return_probability: bool = True) -> Union[bool, float, Tuple[bool, float]]:
        """
        Make a prediction using the specified model
        
        Args:
            model_name: Name of the model to use
            features: Feature vector to use for prediction
            return_probability: Whether to return prediction probability
            
        Returns:
            If return_probability is True:
                Tuple of (is_phishing (bool), confidence (float))
            Otherwise:
                is_phishing (bool)
            
        Raises:
            ValueError: If model is not loaded or features have wrong dimensions
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")
        
        model = self.models[model_name]
        
        # Convert to numpy array and reshape to 2D if needed
        features_array = np.asarray(features)
        if features_array.ndim == 1:
            features_array = features_array.reshape(1, -1)
        
        try:
            # Get prediction probability
            if hasattr(model, 'predict_proba'):
                # Get raw probabilities for both classes
                probabilities = model.predict_proba(features_array)[0]
                
                # IMPORTANT: The model might consider class 0 as phishing (not class 1)
                # Get probability for class 0 (first element) and use it as phishing probability
                class0_prob = probabilities[0]  # Probability for class 0
                class1_prob = probabilities[1]  # Probability for class 1
                
                logger.info(f"Raw probabilities - Class 0: {class0_prob:.4f}, Class 1: {class1_prob:.4f}")
                
                # Try using class 0 probability as phishing score instead of class 1
                phishing_probability = class0_prob
                logger.info(f"Using Class 0 as phishing probability: {phishing_probability:.4f}")
                
                # Determine if phishing based on the probability and threshold
                is_phishing = phishing_probability > 0.95  # High threshold for class 0
                logger.info(f"Is phishing (class 0 > 0.95): {is_phishing}")
                
                # Return the class 0 probability as our confidence
                probability = phishing_probability
            else:
                # Fall back to binary prediction if predict_proba not available
                prediction = model.predict(features_array)[0]
                # Invert the prediction (0 = phishing, 1 = safe)
                is_phishing = prediction == 0
                probability = 1.0 if is_phishing else 0.0
                logger.info(f"Binary prediction: {prediction}, interpreted as is_phishing={is_phishing}")
            
            if return_probability:
                return is_phishing, probability
            return is_phishing
            
        except Exception as e:
            logger.error(f"Error making prediction with {model_name}: {e}")
            if return_probability:
                return False, 0.5
            return False
    
    def get_feature_contributions(self, model_name: str, features: List[float], 
                                 top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top contributing features for a prediction
        
        Args:
            model_name: Name of the model
            features: Feature vector used for prediction
            top_n: Number of top features to return
            
        Returns:
            List of dictionaries with feature name, value, and importance
        """
        if model_name not in self.models or model_name not in self.model_features or model_name not in self.feature_importances:
            return []
            
        feature_names = self.model_features[model_name]
        feature_importance = self.feature_importances[model_name]
        
        # Create a list of (feature_name, feature_value, importance) tuples
        feature_contributions = []
        for i, feature_value in enumerate(features):
            if i < len(feature_names):
                feature_name = feature_names[i]
                importance = feature_importance.get(feature_name, 0)
                feature_contributions.append((feature_name, feature_value, importance))
        
        # Sort by importance (descending) and take top_n
        feature_contributions.sort(key=lambda x: x[2], reverse=True)
        top_features = feature_contributions[:top_n]
        
        # Convert to list of dictionaries
        result = []
        for name, value, importance in top_features:
            result.append({
                "name": name,
                "value": float(value) if isinstance(value, (int, float, np.number)) else value,
                "importance": float(importance)
            })
            
        return result
    
    def get_loaded_models(self) -> List[str]:
        """Get a list of loaded model names"""
        return list(self.models.keys()) 