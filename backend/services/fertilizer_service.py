"""
Fertilizer Recommendation Service.
Loads the trained classifier and fertilizer metadata to produce recommendations.
"""

import os
import json
import joblib
import pandas as pd
import logging

logger = logging.getLogger(__name__)

from backend.extensions import cache

@cache.memoize(timeout=3600)
def get_fertilizer_info():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    try:
        with open(os.path.join(base_dir, 'datasets', 'fertilizer_info.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load fertilizer info: {e}")
        return {}

class FertilizerService:
    """Service class for fertilizer recommendation inference."""

    _model = None
    _scaler = None
    _encoders = None

    @classmethod
    def _load_artifacts(cls):
        from backend.services.model_registry import model_registry
        cls._model = model_registry.get_model('fertilizer_model')
        cls._scaler = model_registry.get_model('scaler_fertilizer')
        cls._encoders = model_registry.get_model('encoders_fertilizer')
        
        return cls._model is not None and cls._scaler is not None and cls._encoders is not None

    @classmethod
    def recommend(cls, nitrogen, phosphorus, potassium, soil_type, crop_type,
                  moisture, temperature, humidity):
        """Predict the best fertilizer and return enriched info."""
        if not cls._load_artifacts():
            raise RuntimeError("Fertilizer model artifacts are unavailable.")

        # Build input dataframe
        input_data = {
            'temperature': float(temperature),
            'humidity': float(humidity),
            'moisture': float(moisture),
            'soil_type': soil_type,
            'crop_type': crop_type,
            'nitrogen': float(nitrogen),
            'phosphorus': float(phosphorus),
            'potassium': float(potassium),
        }
        input_df = pd.DataFrame([input_data])

        # Encode categoricals
        for col in ['soil_type', 'crop_type']:
            le = cls._encoders.get(col)
            if le:
                try:
                    input_df[col] = le.transform(input_df[col])
                except ValueError:
                    logger.warning(f"Unseen label '{input_data[col]}' for {col}. Defaulting.")
                    input_df[col] = le.transform([le.classes_[0]])

        # Scale numerics
        num_cols = ['temperature', 'humidity', 'moisture', 'nitrogen', 'phosphorus', 'potassium']
        input_df[num_cols] = cls._scaler.transform(input_df[num_cols])

        # Predict
        pred_idx = cls._model.predict(input_df)[0]
        fertilizer_name = cls._encoders['fertilizer_name'].inverse_transform([pred_idx])[0]

        # Get confidence from class probabilities
        proba = cls._model.predict_proba(input_df)[0]
        confidence = round(float(max(proba)) * 100, 1)

        # Enrich with metadata from fertilizer_info.json
        info = get_fertilizer_info().get(fertilizer_name, {})

        return fertilizer_name, confidence, info
