"""
Fertilizer Data database model.
Stores fertilizer recommendation results linked to soil inputs.
"""

from datetime import datetime
from backend.extensions import db


class FertilizerData(db.Model):
    """Stores fertilizer recommendations generated from soil analysis."""
    __tablename__ = 'fertilizer_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    soil_data_id = db.Column(db.Integer, db.ForeignKey('soil_data.id'), nullable=True, index=True)

    # Fertilizer recommendation
    fertilizer_name = db.Column(db.String(150), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=True)
    reason = db.Column(db.Text, nullable=True)

    # Crop context
    target_crop = db.Column(db.String(100), nullable=True)

    # Nutrient analysis
    nitrogen_status = db.Column(db.String(20), nullable=True)   # 'low', 'normal', 'high'
    phosphorus_status = db.Column(db.String(20), nullable=True)
    potassium_status = db.Column(db.String(20), nullable=True)

    # Model info
    confidence_score = db.Column(db.Float, nullable=True)
    model_used = db.Column(db.String(100), nullable=True)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship back to user
    user = db.relationship('User', backref=db.backref('fertilizer_data', lazy='dynamic'))

    def to_dict(self):
        """Serialize fertilizer data to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'soil_data_id': self.soil_data_id,
            'fertilizer_name': self.fertilizer_name,
            'quantity_kg': self.quantity_kg,
            'reason': self.reason,
            'target_crop': self.target_crop,
            'nitrogen_status': self.nitrogen_status,
            'phosphorus_status': self.phosphorus_status,
            'potassium_status': self.potassium_status,
            'confidence_score': self.confidence_score,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<FertilizerData id={self.id} name={self.fertilizer_name}>'
