"""
Recommendation Routes.
API endpoints for Crop, Yield, Disease, and Fertilizer ML models.
"""

import json
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.crop_service import CropService
from backend.services.fertilizer_service import FertilizerService
from backend.models.prediction import Prediction
from backend.models.notification import Notification
from backend.models.user import User
from backend.services.email_service import send_prediction_report
from backend.extensions import db
from backend.utils.helpers import api_response, api_error
from backend.services.logger import log_ml_prediction

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/crop', methods=['POST'])
@jwt_required()
def recommend_crop():
    """
    POST /api/recommend/crop
    Accepts soil and weather parameters and returns a crop recommendation.
    """
    data = request.get_json()
    if not data:
        return api_error("No input data provided", 400)

    # Required fields
    required_fields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']
    for field in required_fields:
        if field not in data:
            return api_error(f"Missing required field: {field}", 400)

    # Validate numeric and ranges
    try:
        n = float(data['nitrogen'])
        p = float(data['phosphorus'])
        k = float(data['potassium'])
        temp = float(data['temperature'])
        hum = float(data['humidity'])
        ph = float(data['ph'])
        rain = float(data['rainfall'])

        if not (0 <= temp <= 60): raise ValueError("Temperature must be 0-60.")
        if not (0 <= hum <= 100): raise ValueError("Humidity must be 0-100.")
        if not (0 <= ph <= 14): raise ValueError("pH must be 0-14.")
        if n < 0 or p < 0 or k < 0 or rain < 0: raise ValueError("N, P, K, and Rainfall must be positive.")

    except ValueError as e:
        return api_error(str(e), 400)
    except TypeError:
        return api_error("All fields must be numeric.", 400)

    # Run Prediction
    try:
        crop_name, confidence, info = CropService.recommend(n, p, k, temp, hum, ph, rain)
    except RuntimeError:
        return api_error("ML model is currently unavailable.", 500)
    except Exception as e:
        return api_error(f"Prediction failed: {str(e)}", 500)

    # Save to Database
    user_id = get_jwt_identity()
    
    # Store input and result in JSON format in the Prediction table
    input_data = {
        "N": n, "P": p, "K": k, 
        "temperature": temp, "humidity": hum, "ph": ph, "rainfall": rain
    }
    result_data = {
        "recommended_crop": crop_name.capitalize(),
        "confidence_score": confidence,
        "info": info
    }
    
    # Audit log
    log_ml_prediction('crop', user_id, input_data, result_data)


    prediction_record = Prediction(
        user_id=user_id,
        prediction_type='crop_recommendation',
        recommended_crop=crop_name.capitalize(),
        confidence_score=confidence,
        raw_output=json.dumps({"input": input_data, "info": info})
    )

    try:
        db.session.add(prediction_record)
        
        # Create Notification
        notif = Notification(
            user_id=user_id,
            type='prediction',
            message=f"Crop Recommendation complete: {crop_name.capitalize()} ({confidence:.1f}%)"
        )
        db.session.add(notif)
        db.session.commit()
        
        # Send Email
        user = User.query.get(user_id)
        if user:
            send_prediction_report(user, 'crop_recommendation', {'result': crop_name.capitalize(), 'confidence': f"{confidence:.1f}%"})
            
    except Exception as e:
        db.session.rollback()
        # Non-fatal error, we can still return the prediction
        print(f"Failed to save prediction to DB: {e}")

    # Return response
    return api_response({
        "crop": crop_name.capitalize(),
        "confidence": confidence,
        "info": info,
        "prediction_id": prediction_record.id
    }, message="Crop recommendation successful")


@recommend_bp.route('/fertilizer', methods=['POST'])
@jwt_required()
def recommend_fertilizer():
    """
    POST /api/recommend/fertilizer
    Predict the best fertilizer based on soil nutrients, crop, and conditions.
    """
    data = request.get_json()
    if not data:
        return api_error("No input data provided", 400)

    required_fields = ['nitrogen', 'phosphorus', 'potassium', 'soil_type',
                       'crop', 'moisture', 'temperature', 'humidity']
    missing = [f for f in required_fields if f not in data or data[f] == ""]
    if missing:
        return api_error(f"Missing required fields: {', '.join(missing)}", 400)

    try:
        n = float(data['nitrogen'])
        p = float(data['phosphorus'])
        k = float(data['potassium'])
        temp = float(data['temperature'])
        hum = float(data['humidity'])
        moist = float(data['moisture'])
        if n < 0 or p < 0 or k < 0: raise ValueError("N, P, K must be positive.")
        if not (0 <= temp <= 60): raise ValueError("Temperature must be 0-60.")
        if not (0 <= hum <= 100): raise ValueError("Humidity must be 0-100.")
        if not (0 <= moist <= 100): raise ValueError("Moisture must be 0-100.")
    except ValueError as e:
        return api_error(str(e), 400)
    except TypeError:
        return api_error("Numeric fields must be numbers.", 400)

    try:
        fertilizer_name, confidence, info = FertilizerService.recommend(
            nitrogen=data['nitrogen'],
            phosphorus=data['phosphorus'],
            potassium=data['potassium'],
            soil_type=data['soil_type'],
            crop_type=data['crop'],
            moisture=data['moisture'],
            temperature=data['temperature'],
            humidity=data['humidity']
        )
    except RuntimeError:
        return api_error("Fertilizer model is currently unavailable.", 500)
    except Exception as e:
        return api_error(f"Prediction failed: {str(e)}", 500)

    # Save to DB
    user_id = get_jwt_identity()
    result_payload = {
        'fertilizer': fertilizer_name,
        'confidence': confidence,
        'info': info,
        'input': {
            'N': float(data['nitrogen']),
            'P': float(data['phosphorus']),
            'K': float(data['potassium']),
            'soil_type': data['soil_type'],
            'crop': data['crop']
        }
    }
    
    # Audit log
    log_ml_prediction('fertilizer', user_id, result_payload['input'], {'fertilizer': fertilizer_name, 'confidence': confidence})

    prediction_record = Prediction(
        user_id=user_id,
        prediction_type='fertilizer_recommendation',
        recommended_crop=data['crop'],
        raw_output=json.dumps(result_payload)
    )

    try:
        db.session.add(prediction_record)
        
        # Create Notification
        notif = Notification(
            user_id=user_id,
            type='prediction',
            message=f"Fertilizer Recommendation complete: {fertilizer_name} ({confidence:.1f}%)"
        )
        db.session.add(notif)
        db.session.commit()
        
        # Send Email
        user = User.query.get(user_id)
        if user:
            send_prediction_report(user, 'fertilizer_recommendation', {'result': fertilizer_name, 'confidence': f"{confidence:.1f}%"})
            
    except Exception as e:
        db.session.rollback()

    return api_response({
        'fertilizer': fertilizer_name,
        'confidence': confidence,
        'quantity_kg_per_acre': info.get('quantity_kg_per_acre', 'N/A'),
        'application_method': info.get('application_method', ''),
        'description': info.get('description', ''),
        'deficiency_addressed': info.get('deficiency_addressed', ''),
        'warning': info.get('warning', ''),
        'best_for': info.get('best_for', []),
        'cost_estimate': info.get('cost_estimate', ''),
        'full_name': info.get('name', fertilizer_name),
        'input_npk': {
            'nitrogen': float(data['nitrogen']),
            'phosphorus': float(data['phosphorus']),
            'potassium': float(data['potassium'])
        }
    }, message="Fertilizer recommendation successful")
