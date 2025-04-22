"""
Feature Engineering Pipeline for Lumina AI Enhanced Learning System

This module provides a comprehensive feature engineering pipeline for transforming
raw data into features suitable for machine learning models.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_regression
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
import joblib
import os


@dataclass
class FeatureTransformation:
    """Configuration for a feature transformation."""
    name: str
    transformer_type: str
    columns: List[str]
    parameters: Dict[str, Any]


class FeatureEngineeringPipeline:
    """
    Feature Engineering Pipeline for transforming raw data into features.
    
    The FeatureEngineeringPipeline handles:
    - Feature extraction from various data types
    - Feature selection and importance ranking
    - Feature transformation and normalization
    - Feature validation and quality assurance
    """
    
    def __init__(self):
        """Initialize the FeatureEngineeringPipeline."""
        self.transformations = []
        self.pipeline = None
        self.feature_names = None
        self.feature_importances = None
        
    def add_transformation(self, transformation: FeatureTransformation):
        """
        Add a transformation to the pipeline.
        
        Args:
            transformation: Configuration for the transformation
        """
        self.transformations.append(transformation)
        
    def build_pipeline(self):
        """
        Build the scikit-learn pipeline from the configured transformations.
        
        Returns:
            pipeline: The constructed scikit-learn pipeline
        """
        steps = []
        
        for i, transform in enumerate(self.transformations):
            transformer = self._create_transformer(transform)
            steps.append((f"{transform.name}_{i}", transformer))
            
        self.pipeline = Pipeline(steps)
        return self.pipeline
    
    def _create_transformer(self, config: FeatureTransformation):
        """
        Create a transformer based on configuration.
        
        Args:
            config: Configuration for the transformer
            
        Returns:
            transformer: The constructed transformer
        """
        if config.transformer_type == "standard_scaler":
            return StandardScaler(**config.parameters)
        elif config.transformer_type == "minmax_scaler":
            return MinMaxScaler(**config.parameters)
        elif config.transformer_type == "one_hot_encoder":
            return OneHotEncoder(**config.parameters)
        elif config.transformer_type == "pca":
            return PCA(**config.parameters)
        elif config.transformer_type == "select_k_best":
            if config.parameters.get("score_func") == "f_classif":
                score_func = f_classif
            elif config.parameters.get("score_func") == "mutual_info_regression":
                score_func = mutual_info_regression
            else:
                score_func = f_classif
                
            params = config.parameters.copy()
            if "score_func" in params:
                del params["score_func"]
                
            return SelectKBest(score_func=score_func, **params)
        else:
            raise ValueError(f"Unknown transformer type: {config.transformer_type}")
    
    def fit_transform(self, data: pd.DataFrame) -> np.ndarray:
        """
        Fit the pipeline to the data and transform it.
        
        Args:
            data: Input data to transform
            
        Returns:
            transformed_data: The transformed features
        """
        if self.pipeline is None:
            self.build_pipeline()
            
        # Store original feature names
        self.feature_names = list(data.columns)
        
        # Fit and transform
        transformed_data = self.pipeline.fit_transform(data)
        
        # Extract feature importances if available
        self._extract_feature_importances()
        
        return transformed_data
    
    def transform(self, data: pd.DataFrame) -> np.ndarray:
        """
        Transform data using the fitted pipeline.
        
        Args:
            data: Input data to transform
            
        Returns:
            transformed_data: The transformed features
        """
        if self.pipeline is None:
            raise ValueError("Pipeline must be fitted before transform can be called")
            
        return self.pipeline.transform(data)
    
    def _extract_feature_importances(self):
        """Extract feature importances from the pipeline if available."""
        self.feature_importances = {}
        
        # Check for SelectKBest in the pipeline
        for name, transformer in self.pipeline.named_steps.items():
            if isinstance(transformer, SelectKBest) and hasattr(transformer, "scores_"):
                self.feature_importances[name] = dict(zip(self.feature_names, transformer.scores_))
    
    def get_feature_importances(self) -> Dict[str, Dict[str, float]]:
        """
        Get feature importances from the pipeline.
        
        Returns:
            importances: Dictionary of feature importances by transformer
        """
        if self.feature_importances is None:
            return {}
            
        return self.feature_importances
    
    def save(self, filepath: str):
        """
        Save the pipeline to a file.
        
        Args:
            filepath: Path to save the pipeline
        """
        if self.pipeline is None:
            raise ValueError("Pipeline must be built before it can be saved")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save pipeline and metadata
        joblib.dump({
            "pipeline": self.pipeline,
            "transformations": self.transformations,
            "feature_names": self.feature_names,
            "feature_importances": self.feature_importances
        }, filepath)
    
    @classmethod
    def load(cls, filepath: str) -> 'FeatureEngineeringPipeline':
        """
        Load a pipeline from a file.
        
        Args:
            filepath: Path to load the pipeline from
            
        Returns:
            pipeline: The loaded pipeline
        """
        data = joblib.load(filepath)
        
        pipeline = cls()
        pipeline.pipeline = data["pipeline"]
        pipeline.transformations = data["transformations"]
        pipeline.feature_names = data["feature_names"]
        pipeline.feature_importances = data["feature_importances"]
        
        return pipeline


class TextFeatureExtractor:
    """
    Extract features from text data.
    
    This class provides methods for extracting features from text data,
    including bag-of-words, TF-IDF, and word embeddings.
    """
    
    def __init__(self, method: str = "tfidf", **kwargs):
        """
        Initialize the TextFeatureExtractor.
        
        Args:
            method: Feature extraction method ("bow", "tfidf", or "embedding")
            **kwargs: Additional parameters for the extraction method
        """
        self.method = method
        self.params = kwargs
        self.extractor = None
        
        if method == "bow":
            from sklearn.feature_extraction.text import CountVectorizer
            self.extractor = CountVectorizer(**kwargs)
        elif method == "tfidf":
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.extractor = TfidfVectorizer(**kwargs)
        elif method == "embedding":
            # Default to using spaCy for embeddings
            import spacy
            model_name = kwargs.get("model", "en_core_web_md")
            self.extractor = spacy.load(model_name)
        else:
            raise ValueError(f"Unknown text feature extraction method: {method}")
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        Fit the extractor to the texts and transform them.
        
        Args:
            texts: List of text documents
            
        Returns:
            features: Extracted features
        """
        if self.method in ["bow", "tfidf"]:
            return self.extractor.fit_transform(texts)
        elif self.method == "embedding":
            return np.array([self.extractor(text).vector for text in texts])
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform texts using the fitted extractor.
        
        Args:
            texts: List of text documents
            
        Returns:
            features: Extracted features
        """
        if self.method in ["bow", "tfidf"]:
            return self.extractor.transform(texts)
        elif self.method == "embedding":
            return np.array([self.extractor(text).vector for text in texts])
    
    def get_feature_names(self) -> List[str]:
        """
        Get the names of the extracted features.
        
        Returns:
            feature_names: List of feature names
        """
        if self.method in ["bow", "tfidf"]:
            return self.extractor.get_feature_names_out()
        elif self.method == "embedding":
            # Embedding features don't have meaningful names
            dim = self.extractor("test").vector.shape[0]
            return [f"embedding_dim_{i}" for i in range(dim)]
    
    def save(self, filepath: str):
        """
        Save the extractor to a file.
        
        Args:
            filepath: Path to save the extractor
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # For spaCy models, we just save the model name
        if self.method == "embedding":
            import json
            with open(filepath, 'w') as f:
                json.dump({
                    "method": self.method,
                    "params": self.params
                }, f)
        else:
            joblib.dump(self.extractor, filepath)
    
    @classmethod
    def load(cls, filepath: str) -> 'TextFeatureExtractor':
        """
        Load an extractor from a file.
        
        Args:
            filepath: Path to load the extractor from
            
        Returns:
            extractor: The loaded extractor
        """
        # Check if this is a spaCy model
        if filepath.endswith(".json"):
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
                return cls(method=data["method"], **data["params"])
        else:
            extractor = cls()
            extractor.extractor = joblib.load(filepath)
            return extractor


class ImageFeatureExtractor:
    """
    Extract features from image data.
    
    This class provides methods for extracting features from images,
    including using pre-trained CNN models.
    """
    
    def __init__(self, method: str = "cnn", model_name: str = "resnet50", **kwargs):
        """
        Initialize the ImageFeatureExtractor.
        
        Args:
            method: Feature extraction method ("cnn" or "custom")
            model_name: Name of the pre-trained model to use
            **kwargs: Additional parameters for the extraction method
        """
        self.method = method
        self.model_name = model_name
        self.params = kwargs
        self.extractor = None
        
        if method == "cnn":
            try:
                from tensorflow.keras.applications import ResNet50, VGG16, MobileNetV2
                from tensorflow.keras.models import Model
                
                # Load the appropriate pre-trained model
                if model_name == "resnet50":
                    base_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
                elif model_name == "vgg16":
                    base_model = VGG16(weights='imagenet', include_top=False, pooling='avg')
                elif model_name == "mobilenet":
                    base_model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
                else:
                    raise ValueError(f"Unknown model name: {model_name}")
                
                self.extractor = base_model
                
            except ImportError:
                raise ImportError("TensorFlow is required for CNN feature extraction")
        elif method == "custom":
            # Custom feature extraction method
            if "extractor" in kwargs:
                self.extractor = kwargs["extractor"]
            else:
                raise ValueError("Custom extractor must be provided")
        else:
            raise ValueError(f"Unknown image feature extraction method: {method}")
    
    def preprocess_image(self, image):
        """
        Preprocess an image for feature extraction.
        
        Args:
            image: Input image
            
        Returns:
            preprocessed_image: Preprocessed image
        """
        if self.method == "cnn":
            from tensorflow.keras.applications.resnet50 import preprocess_input
            from tensorflow.keras.preprocessing import image as keras_image
            import numpy as np
            
            # Resize image to expected size
            if isinstance(image, str):
                # Load image from file
                img = keras_image.load_img(image, target_size=(224, 224))
                img = keras_image.img_to_array(img)
            else:
                # Resize image
                img = keras_image.smart_resize(image, (224, 224))
                
            # Expand dimensions and preprocess
            img = np.expand_dims(img, axis=0)
            img = preprocess_input(img)
            
            return img
        elif self.method == "custom":
            # Use custom preprocessing if provided
            if "preprocess" in self.params:
                return self.params["preprocess"](image)
            else:
                return image
    
    def extract_features(self, images: List[Any]) -> np.ndarray:
        """
        Extract features from images.
        
        Args:
            images: List of images or image paths
            
        Returns:
            features: Extracted features
        """
        if self.extractor is None:
            raise ValueError("Extractor not initialized")
            
        # Preprocess images
        preprocessed = [self.preprocess_image(img) for img in images]
        
        if self.method == "cnn":
            import numpy as np
            
            # For CNN, we need to concatenate the preprocessed images
            batch = np.vstack(preprocessed)
            
            # Extract features
            features = self.extractor.predict(batch)
            
            return features
        elif self.method == "custom":
            # Use custom extraction
            return np.array([self.extractor.predict(img) for img in preprocessed])
    
    def save(self, filepath: str):
        """
        Save the extractor configuration to a file.
        
        Args:
            filepath: Path to save the extractor
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # For CNN models, we just save the configuration
        if self.method == "cnn":
            import json
            with open(filepath, 'w') as f:
                json.dump({
                    "method": self.method,
                    "model_name": self.model_name,
                    "params": {k: v for k, v in self.params.items() if isinstance(v, (str, int, float, bool, list, dict))}
                }, f)
        else:
            # For custom extractors, we need to use joblib if possible
            try:
                joblib.dump(self.extractor, filepath)
            except:
                raise ValueError("Custom extractor cannot be saved")
    
    @classmethod
    def load(cls, filepath: str) -> 'ImageFeatureExtractor':
        """
        Load an extractor from a file.
        
        Args:
            filepath: Path to load the extractor from
            
        Returns:
            extractor: The loaded extractor
        """
        # Check if this is a CNN configuration
        if filepath.endswith(".json"):
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
                return cls(method=data["method"], model_name=data.get("model_name", "resnet50"), **data.get("params", {}))
        else:
            # For custom extractors
            extractor = cls(method="custom")
            extractor.extractor = joblib.load(filepath)
            return extractor


class FeatureValidator:
    """
    Validate features for quality and consistency.
    
    This class provides methods for validating features before they are used
    for model training or inference.
    """
    
    def __init__(self):
        """Initialize the FeatureValidator."""
        self.validators = []
        
    def add_validator(self, validator_func: Callable[[np.ndarray], Tuple[bool, str]]):
        """
        Add a validator function.
        
        Args:
            validator_func: Function that takes features and returns (is_valid, message)
        """
        self.validators.append(validator_func)
        
    def validate(self, features: np.ndarray) -> Tuple[bool, List[str]]:
        """
        Validate features using all registered validators.
        
        Args:
            features: Features to validate
            
        Returns:
            is_valid: Whether the features are valid
            messages: List of validation messages
        """
        is_valid = True
        messages = []
        
        for validator in self.validators:
            valid, message = validator(features)
            if not valid:
                is_valid = False
                messages.append(message)
                
        return is_valid, messages
    
    @staticmethod
    def check_missing_values(features: np.ndarray, threshold: float = 0.1) -> Tuple[bool, str]:
        """
        Check for missing values in features.
        
        Args:
            features: Features to check
            threshold: Maximum allowed fraction of missing values
            
        Returns:
            is_valid: Whether the features are valid
            message: Validation message
        """
        if isinstance(features, np.ndarray):
            missing_fraction = np.isnan(features).mean()
        else:
            # For sparse matrices
            missing_fraction = 0  # Sparse matrices don't typically have NaN values
            
        is_valid = missing_fraction <= threshold
        message = f"Missing values: {missing_fraction:.2%}" if not is_valid else ""
        
        return is_valid, message
    
    @staticmethod
    def check_feature_range(features: np.ndarray, min_val: float = -1e6, max_val: float = 1e6) -> Tuple[bool, str]:
        """
        Check if features are within a valid range.
        
        Args:
            features: Features to check
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            is_valid: Whether the features are valid
            message: Validation message
        """
        if isinstance(features, np.ndarray):
            min_feature = np.min(features)
            max_feature = np.max(features)
        else:
            # For sparse matrices
            min_feature = features.min()
            max_feature = features.max()
            
        is_valid = min_feature >= min_val and max_feature <= max_val
        message = f"Feature range: [{min_feature}, {max_feature}]" if not is_valid else ""
        
        return is_valid, message
    
    @staticmethod
    def check_feature_variance(features: np.ndarray, min_variance: float = 1e-6) -> Tuple[bool, str]:
        """
        Check if features have sufficient variance.
        
        Args:
            features: Features to check
            min_variance: Minimum allowed variance
            
        Returns:
            is_valid: Whether the features are valid
            message: Validation message
        """
        if isinstance(features, np.ndarray):
            variances = np.var(features, axis=0)
        else:
            # For sparse matrices
            variances = np.var(features.toarray(), axis=0)
            
        min_var = np.min(variances)
        is_valid = min_var >= min_variance
        message = f"Minimum variance: {min_var}" if not is_valid else ""
        
        return is_valid, message
