"""
Model Registry Service.
Loads and caches all ML models at application startup.
"""

import os
import time
import logging
import threading
import joblib

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Singleton registry with thread-safe lazy loading for ML models."""
    
    _instance = None
    _models = {}
    _is_loaded = False
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_all_models(self, models_dir=None):
        """Thread-safe loading of all models."""
        if self._is_loaded:
            return
            
        with self._lock:
            if self._is_loaded:
                return
                
            start_time = time.time()
            if not models_dir:
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                models_dir = os.path.join(base_dir, 'models')

            model_files = {
                'crop_model': 'crop_model.pkl',
                'disease_cnn_model': 'disease_cnn_model.h5',
                'yield_model': 'yield_model.pkl',
                'fertilizer_model': 'fertilizer_model.pkl',
                'scaler_crop': 'scaler_crop.pkl',
                'scaler_yield': 'scaler_yield.pkl',
                'label_encoder_crop': 'label_encoder_crop.pkl',
                'encoders_yield': 'encoders_yield.pkl',
                'encoders_fertilizer': 'encoders_fertilizer.pkl',
                'scaler_fertilizer': 'scaler_fertilizer.pkl'
            }
            
            for name, filename in model_files.items():
                filepath = os.path.join(models_dir, filename)
                if os.path.exists(filepath):
                    try:
                        if filename.endswith('.h5'):
                            import tensorflow as tf
                            self._models[name] = tf.keras.models.load_model(filepath)
                        else:
                            self._models[name] = joblib.load(filepath)
                    except Exception as e:
                        logger.error(f"Failed to load model {name}: {e}")
                        self._models[name] = None
                else:
                    self._models[name] = None
            
            self._is_loaded = True
            load_time = time.time() - start_time
            logger.info(f"Model registry initialized in {load_time:.2f}s. Loaded: {sum(1 for v in self._models.values() if v is not None)} models.")
    
    def get_model(self, name):
        """Retrieve a loaded model."""
        if not self._is_loaded:
            self.load_all_models()
        return self._models.get(name)

model_registry = ModelRegistry()
