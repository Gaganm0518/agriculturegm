"""
Notifications API Routes.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.notification import Notification
from backend.models.user import User
from backend.extensions import db
from backend.utils.helpers import api_response, api_error

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """GET /api/notifications — get unread count + list for current user"""
    user_id = get_jwt_identity()
    
    # Get all notifications for user, ordered by newest first (limit to last 50 for performance)
    notifs = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    return api_response(data={
        "unread_count": unread_count,
        "notifications": [n.to_dict() for n in notifs]
    })


@notifications_bp.route('/', methods=['POST'])
@jwt_required()
def create_notification():
    """POST /api/notifications — create notification (mostly internal, but exposed for completeness)"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'message' not in data:
        return api_error("Message is required", 400)
        
    type_ = data.get('type', 'info')
    
    notif = Notification(
        user_id=user_id,
        type=type_,
        message=data['message']
    )
    
    db.session.add(notif)
    db.session.commit()
    
    return api_response(data=notif.to_dict(), message="Notification created", status_code=201)


@notifications_bp.route('/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notif_id):
    """PUT /api/notifications/{id}/read — mark as read"""
    user_id = get_jwt_identity()
    notif = Notification.query.filter_by(id=notif_id, user_id=user_id).first()
    
    if not notif:
        return api_error("Notification not found", 404)
        
    notif.is_read = True
    db.session.commit()
    
    return api_response(message="Notification marked as read")


@notifications_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    """PUT /api/notifications/read-all — mark all as read"""
    user_id = get_jwt_identity()
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return api_response(message="All notifications marked as read")
