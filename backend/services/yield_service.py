"""
Yield Prediction Service.
Loads the regression model and handles yield inference.
"""

import os
import joblib
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class YieldService:
    """Service class for crop yield prediction."""

    _model = None
    _scaler = None
    _encoders = None

    @classmethod
    def _load_artifacts(cls):
        from backend.services.model_registry import model_registry
        cls._model = model_registry.get_model('yield_model')
        cls._scaler = model_registry.get_model('scaler_yield')
        cls._encoders = model_registry.get_model('encoders_yield')
        return cls._model is not None and cls._scaler is not None and cls._encoders is not None

    @classmethod
    def predict_yield(cls, crop, season, region, area_ha, rainfall, fertilizer_kg, pesticide_kg):
        """Predict yield in kg/ha based on inputs."""
        if not cls._load_artifacts():
            raise RuntimeError("Yield prediction model artifacts are unavailable.")

        # Prepare input data
        input_data = {
            'crop': crop,
            'season': season,
            'region': region,
            'area_ha': float(area_ha),
            'annual_rainfall': float(rainfall),
            'fertilizer_kg': float(fertilizer_kg),
            'pesticide_kg': float(pesticide_kg)
        }

        input_df = pd.DataFrame([input_data])

        # 1. Label Encode
        for col in ['crop', 'season', 'region']:
            le = cls._encoders.get(col)
            if le:
                try:
                    input_df[col] = le.transform(input_df[col])
                except ValueError:
                    # If unseen label provided, default to the first known class to avoid crashing
                    logger.warning(f"Unseen label '{input_data[col]}' for {col}. Defaulting.")
                    input_df[col] = le.transform([le.classes_[0]])
            else:
                input_df[col] = 0

        # 2. Scale
        num_cols = ['area_ha', 'annual_rainfall', 'fertilizer_kg', 'pesticide_kg']
        input_df[num_cols] = cls._scaler.transform(input_df[num_cols])

        # 3. Predict
        predicted_yield_per_ha = cls._model.predict(input_df)[0]
        
        # Ensure it's not negative
        predicted_yield_per_ha = max(0.0, float(predicted_yield_per_ha))
        
        return round(predicted_yield_per_ha, 2)
