"""
Disease Detection Routes.
API endpoint for uploading a leaf image and detecting plant diseases via CNN.
"""

import os
import json
import time
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from backend.services.disease_service import DiseaseService
from backend.models.prediction import Prediction
from backend.models.notification import Notification
from backend.models.user import User
from backend.services.email_service import send_prediction_report
from backend.extensions import db
from backend.utils.helpers import api_response, api_error, validate_image_bytes
from backend.services.logger import log_ml_prediction

detect_bp = Blueprint('detect', __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@detect_bp.route('/disease', methods=['POST'])
@jwt_required()
def detect_disease():
    """
    POST /api/detect/disease
    Accepts a leaf image (multipart/form-data) and returns the detected disease.
    """
    # 1. Validate file presence
    if 'image' not in request.files:
        return api_error("No 'image' file provided in the request.", 400)

    file = request.files['image']

    if file.filename == '':
        return api_error("No file selected.", 400)

    # 2. Validate extension
    if not _allowed_file(file.filename):
        return api_error("Invalid file type. Allowed: jpg, jpeg, png.", 400)

    # 3. Validate MIME type
    if file.content_type not in ('image/jpeg', 'image/png'):
        return api_error("Invalid MIME type. Upload a JPEG or PNG image.", 400)
        
    # 4. Validate magic bytes to ensure it's truly an image
    if not validate_image_bytes(file):
        return api_error("Invalid file content. The file is not a valid image.", 400)

    # 5. Validate file size (read into memory to check)
    file_data = file.read()
    if len(file_data) > MAX_FILE_SIZE:
        return api_error(f"File too large. Maximum size is 5MB.", 400)
    file.seek(0)  # Reset stream position after reading

    # 5. Save uploaded file
    user_id = get_jwt_identity()
    timestamp = int(time.time())
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{timestamp}.{ext}"

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    upload_dir = os.path.join(base_dir, 'static', 'uploads', 'diseases', str(user_id))
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)
    
    # Process image: resize to max 800px width and compress
    from PIL import Image
    import io
    
    try:
        img = Image.open(io.BytesIO(file_data))
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Resize if width > 800
        if img.width > 800:
            ratio = 800.0 / float(img.width)
            new_height = int(float(img.height) * float(ratio))
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)
            
        # Save as JPEG with quality=85
        if ext != 'jpg' and ext != 'jpeg':
            filename = f"{timestamp}.jpg"
            file_path = os.path.join(upload_dir, filename)
            
        img.save(file_path, 'JPEG', quality=85, optimize=True)
    except Exception as e:
        current_app.logger.error(f"Image processing failed: {e}")
        return api_error("Failed to process uploaded image.", 500)

    image_url = f"/static/uploads/diseases/{user_id}/{filename}"

    # 6. Run Prediction
    try:
        result = DiseaseService.predict(file_path)
    except RuntimeError:
        return api_error("Disease detection model is currently unavailable.", 500)
    except Exception as e:
        return api_error(f"Prediction failed: {str(e)}", 500)

    # Audit log
    log_ml_prediction('disease', user_id, {"image_path": file_path}, result)

    # 7. Save to Database
    prediction_record = Prediction(
        user_id=user_id,
        prediction_type='disease_detection',
        disease_name=result['disease_name'],
        confidence_score=result['confidence'],
        remedy=result['remedy'],
        image_path=image_url,
        raw_output=json.dumps(result)
    )

    try:
        db.session.add(prediction_record)
        
        # Create Notification
        notif = Notification(
            user_id=user_id,
            type='prediction',
            message=f"Disease Detection complete: {result['disease_name']} ({result['confidence']:.1f}%)"
        )
        db.session.add(notif)
        db.session.commit()
        
        # Send Email
        user = User.query.get(user_id)
        if user:
            send_prediction_report(user, 'disease_detection', {'result': result['disease_name'], 'confidence': f"{result['confidence']:.1f}%"})
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to save disease prediction to DB: {e}")

    # 8. Return response
    return api_response({
        'disease': result['disease_name'],
        'confidence': result['confidence'],
        'remedy': result['remedy'],
        'symptoms': result['symptoms'],
        'severity': result['severity'],
        'affected_crops': result['affected_crops'],
        'image_url': image_url,
        'prediction_id': prediction_record.id
    }, message="Disease detection completed successfully")
