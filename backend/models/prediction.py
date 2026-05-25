"""
Prediction database model.
Stores ML prediction results — crop recommendations, disease detections, yield predictions.
"""

from datetime import datetime
from backend.extensions import db


class Prediction(db.Model):
    """Stores all types of ML predictions made for a user."""
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    soil_data_id = db.Column(db.Integer, db.ForeignKey('soil_data.id'), nullable=True, index=True)

    # Prediction type: 'crop_recommendation', 'disease_detection', 'yield_prediction'
    prediction_type = db.Column(db.String(50), nullable=False, index=True)

    # Crop Recommendation fields
    recommended_crop = db.Column(db.String(100), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)

    # Disease Detection fields
    image_path = db.Column(db.String(500), nullable=True)
    disease_name = db.Column(db.String(200), nullable=True)
    remedy = db.Column(db.Text, nullable=True)

    # Yield Prediction fields
    crop_name = db.Column(db.String(100), nullable=True)
    predicted_yield_kg = db.Column(db.Float, nullable=True)

    # General
    model_used = db.Column(db.String(100), nullable=True)
    raw_output = db.Column(db.Text, nullable=True)  # JSON string of full model output

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Serialize prediction to dictionary."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'soil_data_id': self.soil_data_id,
            'prediction_type': self.prediction_type,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        if self.prediction_type == 'crop_recommendation':
            result.update({
                'recommended_crop': self.recommended_crop,
                'confidence_score': self.confidence_score,
            })
        elif self.prediction_type == 'disease_detection':
            result.update({
                'image_path': self.image_path,
                'disease_name': self.disease_name,
                'remedy': self.remedy,
                'confidence_score': self.confidence_score,
            })
        elif self.prediction_type == 'yield_prediction':
            result.update({
                'crop_name': self.crop_name,
                'predicted_yield_kg': self.predicted_yield_kg,
            })

        return result

    def __repr__(self):
        return f'<Prediction id={self.id} type={self.prediction_type}>'
