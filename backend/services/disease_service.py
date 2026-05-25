"""
Disease Detection Service.
Loads the CNN model and handles plant disease classification.
"""

import os
import json
import numpy as np
import logging
from PIL import Image

logger = logging.getLogger(__name__)


class DiseaseService:
    """Service class for plant disease detection using the trained CNN model."""

    _model = None
    _class_names = None
    _diseases_info = None

    @classmethod
    def _load_artifacts(cls):
        from backend.services.model_registry import model_registry
        cls._model = model_registry.get_model('disease_cnn_model')
        
        if cls._class_names is None or cls._diseases_info is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            try:
                with open(os.path.join(base_dir, 'models', 'class_names.json'), 'r') as f:
                    cls._class_names = json.load(f)
                with open(os.path.join(base_dir, 'datasets', 'diseases_info.json'), 'r') as f:
                    cls._diseases_info = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load JSON info: {e}")
                return False
                
        return cls._model is not None and cls._class_names is not None

    @classmethod
    def preprocess_image(cls, image_path):
        """Load and preprocess an image for the CNN model."""
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0  # Normalize to 0-1
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        return img_array

    @classmethod
    def predict(cls, image_path):
        """Run disease detection on a single image file path."""
        if not cls._load_artifacts():
            raise RuntimeError("Disease detection model artifacts are unavailable.")

        # Preprocess
        img_array = cls.preprocess_image(image_path)

        # Predict
        predictions = cls._model.predict(img_array, verbose=0)
        predicted_idx = int(np.argmax(predictions[0]))
        confidence = round(float(predictions[0][predicted_idx]) * 100, 2)

        # Map to disease name
        disease_key = cls._class_names.get(str(predicted_idx), "Unknown")
        info = cls._diseases_info.get(disease_key, {})

        display_name = info.get('display_name', disease_key.replace('_', ' '))
        remedy = info.get('treatment', 'No treatment information available.')
        symptoms = info.get('symptoms', '')
        severity = info.get('severity', 'Unknown')
        affected_crops = info.get('affected_crops', [])

        return {
            'disease_key': disease_key,
            'disease_name': display_name,
            'confidence': confidence,
            'remedy': remedy,
            'symptoms': symptoms,
            'severity': severity,
            'affected_crops': affected_crops
        }
