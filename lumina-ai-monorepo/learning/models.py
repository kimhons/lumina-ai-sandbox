import logging
import numpy as np
import os
import pickle
import json
from typing import Dict, List, Any, Optional, Tuple, Union
import asyncio
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import joblib

from .interfaces import (
    LearningEvent, FeedbackEvent, InteractionEvent, ErrorEvent, PerformanceEvent,
    LearningModel
)

logger = logging.getLogger(__name__)


class BaseModel(LearningModel):
    """Base class for learning models."""
    
    def __init__(self, model_name: str):
        """
        Initialize a new base model.
        
        Args:
            model_name: Name of the model
        """
        self.model_name = model_name
        self.model = None
        self.metadata = {
            "name": model_name,
            "version": "1.0.0",
            "created_at": None,
            "updated_at": None,
            "training_events": 0,
            "performance_metrics": {}
        }
    
    async def save(self, path: str) -> bool:
        """
        Save the model to a file.
        
        Args:
            path: Path to save the model
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save model and metadata
            model_data = {
                "model": self.model,
                "metadata": self.metadata
            }
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    async def load(self, path: str) -> bool:
        """
        Load the model from a file.
        
        Args:
            path: Path to load the model from
            
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            if not os.path.exists(path):
                logger.warning(f"Model file {path} does not exist")
                return False
            
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data["model"]
            self.metadata = model_data["metadata"]
            
            logger.info(f"Model loaded from {path}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


class FeedbackClassifier(BaseModel):
    """Model for classifying feedback."""
    
    def __init__(self):
        """Initialize a new feedback classifier."""
        super().__init__("feedback_classifier")
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.scaler = StandardScaler()
    
    async def train(self, events: List[LearningEvent]) -> bool:
        """
        Train the model on a list of events.
        
        Args:
            events: List of learning events
            
        Returns:
            True if training was successful, False otherwise
        """
        try:
            # Filter for feedback events
            feedback_events = [event for event in events if event.event_type == "feedback"]
            
            if not feedback_events:
                logger.warning("No feedback events to train on")
                return False
            
            # Extract features and labels
            texts = []
            ratings = []
            
            for event in feedback_events:
                if "feedback_text" in event.data and "rating" in event.data:
                    texts.append(event.data["feedback_text"] or "")
                    ratings.append(event.data["rating"])
            
            if not texts:
                logger.warning("No valid feedback data to train on")
                return False
            
            # Transform text features
            X_text = self.vectorizer.fit_transform(texts)
            
            # Train the model
            self.model.fit(X_text, ratings)
            
            # Update metadata
            self.metadata["updated_at"] = asyncio.get_event_loop().time()
            self.metadata["training_events"] = len(feedback_events)
            
            logger.info(f"Trained feedback classifier on {len(feedback_events)} events")
            return True
        
        except Exception as e:
            logger.error(f"Error training feedback classifier: {e}")
            return False
    
    async def predict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction based on the context.
        
        Args:
            context: Context for the prediction
            
        Returns:
            Prediction result
        """
        try:
            if not self.model:
                logger.warning("Model not trained yet")
                return {"error": "Model not trained"}
            
            if "text" not in context:
                logger.warning("No text in context")
                return {"error": "No text in context"}
            
            # Transform text
            text = [context["text"]]
            X_text = self.vectorizer.transform(text)
            
            # Make prediction
            rating = self.model.predict(X_text)[0]
            probabilities = self.model.predict_proba(X_text)[0]
            
            # Get confidence
            confidence = max(probabilities)
            
            return {
                "rating": int(rating),
                "confidence": float(confidence),
                "probabilities": {i: float(p) for i, p in enumerate(probabilities)}
            }
        
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {"error": str(e)}
    
    async def save(self, path: str) -> bool:
        """
        Save the model to a file.
        
        Args:
            path: Path to save the model
            
        Returns:
            True if saving was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save model components
            model_dir = os.path.dirname(path)
            base_name = os.path.basename(path).split('.')[0]
            
            # Save classifier
            classifier_path = os.path.join(model_dir, f"{base_name}_classifier.pkl")
            joblib.dump(self.model, classifier_path)
            
            # Save vectorizer
            vectorizer_path = os.path.join(model_dir, f"{base_name}_vectorizer.pkl")
            joblib.dump(self.vectorizer, vectorizer_path)
            
            # Save scaler
            scaler_path = os.path.join(model_dir, f"{base_name}_scaler.pkl")
            joblib.dump(self.scaler, scaler_path)
            
            # Save metadata
            metadata_path = os.path.join(model_dir, f"{base_name}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            logger.info(f"Model components saved to {model_dir}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    async def load(self, path: str) -> bool:
        """
        Load the model from a file.
        
        Args:
            path: Path to load the model from
            
        Returns:
            True if loading was successful, False otherwise
        """
        try:
            model_dir = os.path.dirname(path)
            base_name = os.path.basename(path).split('.')[0]
            
            # Load classifier
            classifier_path = os.path.join(model_dir, f"{base_name}_classifier.pkl")
            if not os.path.exists(classifier_path):
                logger.warning(f"Classifier file {classifier_path} does not exist")
                return False
            
            self.model = joblib.load(classifier_path)
            
            # Load vectorizer
            vectorizer_path = os.path.join(model_dir, f"{base_name}_vectorizer.pkl")
            if not os.path.exists(vectorizer_path):
                logger.warning(f"Vectorizer file {vectorizer_path} does not exist")
                return False
            
            self.vectorizer = joblib.load(vectorizer_path)
            
            # Load scaler
            scaler_path = os.path.join(model_dir, f"{base_name}_scaler.pkl")
            if not os.path.exists(scaler_path):
                logger.warning(f"Scaler file {scaler_path} does not exist")
                return False
            
            self.scaler = joblib.load(scaler_path)
            
            # Load metadata
            metadata_path = os.path.join(model_dir, f"{base_name}_metadata.json")
            if not os.path.exists(metadata_path):
                logger.warning(f"Metadata file {metadata_path} does not exist")
                return False
            
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            logger.info(f"Model components loaded from {model_dir}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


class ResponseQualityPredictor(BaseModel):
    """Model for predicting response quality."""
    
    def __init__(self):
        """Initialize a new response quality predictor."""
        super().__init__("response_quality_predictor")
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.vectorizer = TfidfVectorizer(max_features=1000)
    
    async def train(self, events: List[LearningEvent]) -> bool:
        """
        Train the model on a list of events.
        
        Args:
            events: List of learning events
            
        Returns:
            True if training was successful, False otherwise
        """
        try:
            # We need both interaction events (for responses) and feedback events (for ratings)
            interaction_events = {event.event_id: event for event in events if event.event_type == "interaction"}
            feedback_events = [event for event in events if event.event_type == "feedback"]
            
            if not interaction_events or not feedback_events:
                logger.warning("Not enough events to train on")
                return False
            
            # Extract features and labels
            texts = []
            ratings = []
            
            for feedback in feedback_events:
                # Get the interaction that this feedback is for
                interaction_id = feedback.metadata.get("interaction_id")
                if not interaction_id or interaction_id not in interaction_events:
                    continue
                
                interaction = interaction_events[interaction_id]
                
                if "content" in interaction.data and "rating" in feedback.data:
                    texts.append(interaction.data["content"] or "")
                    ratings.append(feedback.data["rating"])
            
            if not texts:
                logger.warning("No valid training data")
                return False
            
            # Transform text features
            X_text = self.vectorizer.fit_transform(texts)
            
            # Train the model
            self.model.fit(X_text, ratings)
            
            # Update metadata
            self.metadata["updated_at"] = asyncio.get_event_loop().time()
            self.metadata["training_events"] = len(texts)
            
            logger.info(f"Trained response quality predictor on {len(texts)} events")
            return True
        
        except Exception as e:
            logger.error(f"Error training response quality predictor: {e}")
            return False
    
    async def predict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction based on the context.
        
        Args:
            context: Context for the prediction
            
        Returns:
            Prediction result
        """
        try:
            if not self.model:
                logger.warning("Model not trained yet")
                return {"error": "Model not trained"}
            
            if "response" not in context:
                logger.warning("No response in context")
                return {"error": "No response in context"}
            
            # Transform text
            text = [context["response"]]
            X_text = self.vectorizer.transform(text)
            
            # Make prediction
            quality = self.model.predict(X_text)[0]
            
            return {
                "quality": float(quality),
                "confidence": 0.8  # Simplified confidence estimation
            }
        
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {"error": str(e)}


class UserPreferenceModel(BaseModel):
    """Model for learning user preferences."""
    
    def __init__(self):
        """Initialize a new user preference model."""
        super().__init__("user_preference_model")
        self.user_models = {}  # Dictionary of user-specific models
    
    async def train(self, events: List[LearningEvent]) -> bool:
        """
        Train the model on a list of events.
        
        Args:
            events: List of learning events
            
        Returns:
            True if training was successful, False otherwise
        """
        try:
            # Group events by user
            user_events = {}
            for event in events:
                if not event.user_id:
                    continue
                
                if event.user_id not in user_events:
                    user_events[event.user_id] = []
                
                user_events[event.user_id].append(event)
            
            if not user_events:
                logger.warning("No user events to train on")
                return False
            
            # Train a model for each user
            for user_id, user_event_list in user_events.items():
                # Create a user model if it doesn't exist
                if user_id not in self.user_models:
                    self.user_models[user_id] = {
                        "preferences": {},
                        "interaction_history": [],
                        "feedback_history": []
                    }
                
                user_model = self.user_models[user_id]
                
                # Process events
                for event in user_event_list:
                    if event.event_type == "interaction":
                        user_model["interaction_history"].append(event.to_dict())
                    elif event.event_type == "feedback":
                        user_model["feedback_history"].append(event.to_dict())
                        
                        # Update preferences based on feedback
                        if "feedback_type" in event.data and "rating" in event.data:
                            feedback_type = event.data["feedback_type"]
                            rating = event.data["rating"]
                            
                            if feedback_type not in user_model["preferences"]:
                                user_model["preferences"][feedback_type] = []
                            
                            user_model["preferences"][feedback_type].append(rating)
            
            # Calculate average preferences
            for user_id, user_model in self.user_models.items():
                for feedback_type, ratings in user_model["preferences"].items():
                    if ratings:
                        user_model["preferences"][feedback_type] = sum(ratings) / len(ratings)
            
            # Update metadata
            self.metadata["updated_at"] = asyncio.get_event_loop().time()
            self.metadata["training_events"] = sum(len(events) for events in user_events.values())
            self.metadata["user_count"] = len(user_events)
            
            logger.info(f"Trained user preference model for {len(user_events)} users")
            return True
        
        except Exception as e:
            logger.error(f"Error training user preference model: {e}")
            return False
    
    async def predict(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction based on the context.
        
        Args:
            context: Context for the prediction
            
        Returns:
            Prediction result
        """
        try:
            if "user_id" not in context:
                logger.warning("No user_id in context")
                return {"error": "No user_id in context"}
            
            user_id = context["user_id"]
            
            if user_id not in self.user_models:
                logger.warning(f"No model for user {user_id}")
                return {"preferences": {}, "confidence": 0.0}
            
            user_model = self.user_models[user_id]
            
            # Calculate confidence based on amount of data
            interaction_count = len(user_model["interaction_history"])
            feedback_count = len(user_model["feedback_history"])
            
            confidence = min(1.0, (interaction_count + feedback_count * 2) / 100)
            
            return {
                "preferences": user_model["preferences"],
                "confidence": confidence,
                "interaction_count": interaction_count,
                "feedback_count": feedback_count
            }
        
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {"error": str(e)}


class ModelFactory:
    """Factory for creating learning models."""
    
    @staticmethod
    def create_model(model_type: str) -> LearningModel:
        """
        Create a learning model.
        
        Args:
            model_type: Type of model to create
            
        Returns:
            The created model
            
        Raises:
            ValueError: If the model type is not supported
        """
        if model_type == "feedback_classifier":
            return FeedbackClassifier()
        elif model_type == "response_quality":
            return ResponseQualityPredictor()
        elif model_type == "user_preference":
            return UserPreferenceModel()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
