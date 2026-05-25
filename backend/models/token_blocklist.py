"""
Token blocklist model for JWT revocation.
Stores JTI (JWT ID) of revoked tokens to prevent them from being used after logout.
"""

from datetime import datetime
from backend.extensions import db


class TokenBlocklist(db.Model):
    """Model for storing revoked JWT tokens."""
    __tablename__ = 'token_blocklist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<TokenBlocklist jti={self.jti}>'
