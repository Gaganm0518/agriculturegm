"""
Notification database model.
"""

from datetime import datetime
from backend.extensions import db


class Notification(db.Model):
    """Notification model for in-app alerts."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False) # 'info', 'success', 'warning', 'error', 'prediction'
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship to user
    # 'user' is already backref'd from User model if defined, but we'll leave it simple here

    def to_dict(self):
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Notification {self.id} User {self.user_id}>'
