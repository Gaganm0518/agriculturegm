"""
Prediction Routes for Yield.
API endpoint for Crop Yield Prediction.
"""

import json
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.yield_service import YieldService
from backend.models.prediction import Prediction
from backend.models.notification import Notification
from backend.models.user import User
from backend.services.email_service import send_prediction_report
from backend.extensions import db
from backend.utils.helpers import api_response, api_error
from backend.services.logger import log_ml_prediction

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/yield', methods=['POST'])
@jwt_required()
def predict_yield():
    """
    POST /api/predict/yield
    Expects JSON: {
        "crop": "Rice", "season": "Kharif", "region": "Karnataka",
        "area_ha": 2.5, "rainfall": 180, "fertilizer_kg": 120, "pesticide_kg": 1.5
    }
    """
    data = request.get_json()
    if not data:
        return api_error("Invalid JSON data", 400)

    # Validate required fields
    required_fields = ['crop', 'season', 'region', 'area_ha', 'rainfall', 'fertilizer_kg', 'pesticide_kg']
    missing = [f for f in required_fields if f not in data or data[f] == ""]
    if missing:
        return api_error(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        # Predict yield per hectare
        yield_per_ha = YieldService.predict_yield(
            crop=data['crop'],
            season=data['season'],
            region=data['region'],
            area_ha=data['area_ha'],
            rainfall=data['rainfall'],
            fertilizer_kg=data['fertilizer_kg'],
            pesticide_kg=data['pesticide_kg']
        )
        
        area = float(data['area_ha'])
        total_yield_kg = round(yield_per_ha * area, 2)

    except ValueError:
        return api_error("Invalid numeric values provided", 400)
    except RuntimeError:
        return api_error("Yield prediction model is currently unavailable", 500)
    except Exception as e:
        current_app.logger.error(f"Yield Prediction error: {e}")
        return api_error("Failed to generate yield prediction", 500)

    # Save to Database
    user_id = get_jwt_identity()
    result_data = {
        'yield_per_ha': yield_per_ha,
        'total_yield_kg': total_yield_kg,
        'unit': 'kg',
        'crop': data['crop']
    }
    
    # Audit log
    log_ml_prediction('yield', user_id, data, result_data)

    prediction_record = Prediction(
        user_id=user_id,
        prediction_type='yield_prediction',
        crop_name=data['crop'],
        predicted_yield_kg=total_yield_kg,
        raw_output=json.dumps(result_data)
    )

    try:
        db.session.add(prediction_record)
        
        # Create Notification
        notif = Notification(
            user_id=user_id,
            type='prediction',
            message=f"Yield Prediction complete for {data['crop']}: {total_yield_kg} kg"
        )
        db.session.add(notif)
        
        db.session.commit()
        
        # Send Email
        user = User.query.get(user_id)
        if user:
            send_prediction_report(user, 'yield_prediction', {'result': f"{total_yield_kg} kg total yield for {data['crop']}"})
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to save yield prediction to DB: {e}")

    # Return response
    return api_response(result_data, message="Yield prediction completed successfully")
