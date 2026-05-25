"""
History Routes.
Handles fetching, filtering, paginating, and deleting user prediction history.
"""

import json
import csv
import io
from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.prediction import Prediction
from backend.extensions import db
from backend.utils.helpers import api_response, api_error

history_bp = Blueprint('history', __name__)

# Valid prediction type filters
VALID_TYPES = {
    'crop': 'crop_recommendation',
    'disease': 'disease_detection',
    'yield': 'yield_prediction',
    'fertilizer': 'fertilizer_recommendation',
}


@history_bp.route('/', methods=['GET'])
@jwt_required()
def get_history():
    """
    GET /api/history?type=crop&page=1&per_page=20
    Returns paginated prediction history for the logged-in user.
    """
    current_user_id = get_jwt_identity()

    # Query params
    type_filter = request.args.get('type', 'all').lower()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Cap at 100

    # Base query
    query = Prediction.query.filter_by(user_id=current_user_id)

    # Apply type filter
    if type_filter != 'all' and type_filter in VALID_TYPES:
        query = query.filter_by(prediction_type=VALID_TYPES[type_filter])

    # Order by newest first
    query = query.order_by(Prediction.created_at.desc())

    # Paginate
    total = query.count()
    predictions = query.offset((page - 1) * per_page).limit(per_page).all()

    # Build enriched response items
    items = []
    for p in predictions:
        item = p.to_dict()

        # Parse raw_output for richer detail
        raw = {}
        if p.raw_output:
            try:
                raw = json.loads(p.raw_output)
            except (json.JSONDecodeError, TypeError):
                pass
        item['raw_output'] = raw

        # Add a human-readable summary for each type
        if p.prediction_type == 'crop_recommendation':
            item['summary'] = f"Recommended: {p.recommended_crop or 'N/A'}"
            item['icon'] = 'fa-leaf'
            item['badge_color'] = '#16a34a'
        elif p.prediction_type == 'disease_detection':
            item['summary'] = f"Detected: {p.disease_name or 'N/A'}"
            item['icon'] = 'fa-bug'
            item['badge_color'] = '#dc2626'
        elif p.prediction_type == 'yield_prediction':
            item['summary'] = f"Yield: {p.predicted_yield_kg or 0:.0f} kg"
            item['icon'] = 'fa-chart-line'
            item['badge_color'] = '#ea580c'
        elif p.prediction_type == 'fertilizer_recommendation':
            fert_name = raw.get('fertilizer', raw.get('info', {}).get('name', 'N/A'))
            item['summary'] = f"Fertilizer: {fert_name}"
            item['icon'] = 'fa-vial'
            item['badge_color'] = '#2563eb'
        else:
            item['summary'] = p.prediction_type
            item['icon'] = 'fa-question-circle'
            item['badge_color'] = '#6b7280'

        items.append(item)

    return api_response(
        data={
            "history": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page if per_page else 1,
            }
        },
        message="History retrieved successfully"
    )


@history_bp.route('/<int:prediction_id>', methods=['DELETE'])
@jwt_required()
def delete_history_item(prediction_id):
    """DELETE /api/history/<id> — Delete a specific prediction record."""
    current_user_id = get_jwt_identity()

    prediction = Prediction.query.filter_by(
        id=prediction_id, user_id=current_user_id
    ).first()

    if not prediction:
        return api_error("Record not found or access denied.", 404)

    try:
        db.session.delete(prediction)
        db.session.commit()
        return api_response(data={"deleted_id": prediction_id},
                            message="Record deleted successfully")
    except Exception as e:
        db.session.rollback()
        return api_error(f"Failed to delete record: {str(e)}", 500)


@history_bp.route('/export', methods=['GET'])
@jwt_required()
def export_csv():
    """GET /api/history/export — Download all history as a CSV file."""
    current_user_id = get_jwt_identity()

    predictions = Prediction.query.filter_by(user_id=current_user_id) \
                                  .order_by(Prediction.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Type', 'Date', 'Summary', 'Confidence', 'Details'])

    for p in predictions:
        raw = {}
        if p.raw_output:
            try:
                raw = json.loads(p.raw_output)
            except (json.JSONDecodeError, TypeError):
                pass

        summary = ''
        if p.prediction_type == 'crop_recommendation':
            summary = f"Crop: {p.recommended_crop}"
        elif p.prediction_type == 'disease_detection':
            summary = f"Disease: {p.disease_name}"
        elif p.prediction_type == 'yield_prediction':
            summary = f"Yield: {p.predicted_yield_kg} kg"
        elif p.prediction_type == 'fertilizer_recommendation':
            summary = f"Fertilizer: {raw.get('fertilizer', 'N/A')}"

        writer.writerow([
            p.id,
            p.prediction_type,
            p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else '',
            summary,
            p.confidence_score or '',
            json.dumps(raw)[:500]  # Truncate to avoid huge cells
        ])

    csv_content = output.getvalue()
    output.close()

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=smart_agri_history.csv'}
    )
