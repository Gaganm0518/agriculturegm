"""
Crop Prediction Service.
Loads the ML model and handles crop recommendation logic.
"""

import os
import json
import numpy as np
import joblib
import logging

logger = logging.getLogger(__name__)

from backend.extensions import cache

@cache.memoize(timeout=3600)
def get_crop_info():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    try:
        with open(os.path.join(base_dir, 'datasets', 'crops_info.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load crops_info: {e}")
        return {}

class CropService:
    _model = None
    _scaler = None
    _label_encoder = None

    @classmethod
    def _load_artifacts(cls):
        from backend.services.model_registry import model_registry
        
        cls._model = model_registry.get_model('crop_model')
        cls._scaler = model_registry.get_model('scaler_crop')
        cls._label_encoder = model_registry.get_model('label_encoder_crop')
        
        return cls._model is not None and cls._scaler is not None and cls._label_encoder is not None

    @classmethod
    def recommend(cls, N, P, K, temp, humidity, ph, rainfall):
        """Runs the prediction model on input parameters."""
        if not cls._load_artifacts():
            raise RuntimeError("ML model artifacts are unavailable.")

        # Prepare and scale features
        features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
        features_scaled = cls._scaler.transform(features)

        # Predict
        predicted_idx = cls._model.predict(features_scaled)[0]
        crop_name = cls._label_encoder.inverse_transform([predicted_idx])[0]

        # Calculate confidence
        confidence = 0.0
        if hasattr(cls._model, 'predict_proba'):
            probs = cls._model.predict_proba(features_scaled)[0]
            confidence = round(probs[predicted_idx] * 100, 2)

        # Get additional info
        crops_info = get_crop_info()
        info = crops_info.get(crop_name, {
            "season": "Unknown",
            "water_needs": "Unknown",
            "growing_tips": "No specific tips available."
        })

        return crop_name, confidence, info
