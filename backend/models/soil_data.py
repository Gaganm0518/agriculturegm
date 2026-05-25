"""
Soil Data database model.
Stores soil parameters and weather conditions submitted by farmers.
"""

from datetime import datetime
from backend.extensions import db


class SoilData(db.Model):
    """Stores soil test results and environmental conditions for each user input."""
    __tablename__ = 'soil_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Soil nutrients (NPK values)
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)

    # Soil properties
    soil_type = db.Column(db.String(50), nullable=True)
    ph_level = db.Column(db.Float, nullable=True)

    # Environmental conditions
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    rainfall = db.Column(db.Float, nullable=True)

    # Location
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    predictions = db.relationship('Prediction', backref='soil_data', lazy='dynamic')
    fertilizer_recommendations = db.relationship('FertilizerData', backref='soil_data', lazy='dynamic')

    def to_dict(self):
        """Serialize soil data to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'soil_type': self.soil_type,
            'ph_level': self.ph_level,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'rainfall': self.rainfall,
            'city': self.city,
            'state': self.state,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<SoilData id={self.id} user={self.user_id}>'
