"""
Admin Routes.
Handles fetching users, statistics, and managing the platform.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.prediction import Prediction
from backend.extensions import db
from backend.utils.helpers import api_response, api_error
from functools import wraps
from datetime import datetime, timedelta
import os
import uuid
import threading
import subprocess
from werkzeug.utils import secure_filename
from backend.utils.helpers import allowed_file

# Global dictionary to track retraining jobs
# In a real production app, use Celery and Redis.
training_jobs = {}

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    """Custom decorator to verify the logged-in user is an admin."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return api_error("Admin access required.", 403)
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """GET /api/admin/users?page=1&per_page=20"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Sort users by newest first
    query = User.query.order_by(User.created_at.desc())
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()

    users_data = []
    for user in users:
        u_dict = user.to_dict()
        u_dict['predictions_count'] = user.predictions.count()
        users_data.append(u_dict)

    return api_response(data={
        "users": users_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    })


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """PUT /api/admin/users/<id> — update role or status"""
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)
        
    data = request.get_json()
    
    if 'role' in data and data['role'] in ['farmer', 'admin']:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
        
    try:
        db.session.commit()
        return api_response(data=user.to_dict(), message="User updated successfully.")
    except Exception as e:
        db.session.rollback()
        return api_error(str(e), 500)


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """DELETE /api/admin/users/<id> — completely delete a user and their predictions"""
    current_user_id = get_jwt_identity()
    if int(current_user_id) == user_id:
        return api_error("You cannot delete yourself.", 400)
        
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)
        
    try:
        # Delete related predictions first (if cascading not set)
        Prediction.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return api_response(message="User deleted successfully.")
    except Exception as e:
        db.session.rollback()
        return api_error(str(e), 500)


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """GET /api/admin/stats — Dashboard summary statistics"""
    total_users = User.query.count()
    total_predictions = Prediction.query.count()
    
    # Active today
    today = datetime.utcnow().date()
    start_of_today = datetime(today.year, today.month, today.day)
    predictions_today = Prediction.query.filter(Prediction.created_at >= start_of_today).count()
    
    # Active users this week
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    # Distinct users who made a prediction in last 7 days
    active_users = db.session.query(Prediction.user_id).filter(
        Prediction.created_at >= one_week_ago
    ).distinct().count()

    # Prediction distribution
    crop_count = Prediction.query.filter_by(prediction_type='crop_recommendation').count()
    disease_count = Prediction.query.filter_by(prediction_type='disease_detection').count()
    yield_count = Prediction.query.filter_by(prediction_type='yield_prediction').count()
    fert_count = Prediction.query.filter_by(prediction_type='fertilizer_recommendation').count()

    # Predictions per day (last 7 days)
    chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        count = Prediction.query.filter(Prediction.created_at >= day_start, Prediction.created_at < day_end).count()
        chart_data.append({"date": day.strftime('%Y-%m-%d'), "count": count})

    return api_response(data={
        "total_users": total_users,
        "total_predictions": total_predictions,
        "predictions_today": predictions_today,
        "active_users_weekly": active_users,
        "distribution": {
            "crop": crop_count,
            "disease": disease_count,
            "yield": yield_count,
            "fertilizer": fert_count
        },
        "trend_chart": chart_data
    })


@admin_bp.route('/datasets', methods=['GET'])
@admin_required
def get_datasets():
    """GET /api/admin/datasets — list all dataset files"""
    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'datasets')
    os.makedirs(dataset_dir, exist_ok=True)
    
    datasets = []
    for filename in os.listdir(dataset_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(dataset_dir, filename)
            stats = os.stat(file_path)
            
            # Count rows (approximate for large files or exact for small)
            row_count = 0
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    row_count = sum(1 for _ in f) - 1 # subtract header
            except:
                pass
                
            datasets.append({
                'name': filename,
                'size_bytes': stats.st_size,
                'last_updated': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'rows': max(0, row_count)
            })
            
    return api_response(data=datasets)


@admin_bp.route('/datasets/upload', methods=['POST'])
@admin_required
def upload_dataset():
    """POST /api/admin/datasets/upload — upload a CSV dataset"""
    if 'file' not in request.files:
        return api_error('No file part', 400)
    file = request.files['file']
    if file.filename == '':
        return api_error('No selected file', 400)
        
    if file and allowed_file(file.filename, {'csv'}):
        filename = secure_filename(file.filename)
        dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'datasets')
        file_path = os.path.join(dataset_dir, filename)
        file.save(file_path)
        return api_response(message=f'Dataset {filename} uploaded successfully.')
        
    return api_error('Invalid file type. Only CSV allowed.', 400)


def run_training_task(job_id, model_type):
    """Background task to run the training script."""
    training_jobs[job_id]['status'] = 'running'
    script_map = {
        'crop': 'train_crop_model.py',
        'disease': 'train_disease_model.py',
        'yield': 'train_yield_model.py',
        'fertilizer': 'train_fertilizer_model.py'
    }
    
    if model_type not in script_map:
        training_jobs[job_id]['status'] = 'failed'
        training_jobs[job_id]['error'] = 'Invalid model type'
        return
        
    script_name = script_map[model_type]
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
    script_path = os.path.join(models_dir, script_name)
    log_path = os.path.join(models_dir, f'{model_type}_training.log')
    
    try:
        with open(log_path, 'w') as log_file:
            process = subprocess.Popen(
                ['python', script_path],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=models_dir
            )
            process.wait()
            
        if process.returncode == 0:
            training_jobs[job_id]['status'] = 'completed'
            # Parse the log to find accuracy
            accuracy = 'N/A'
            with open(log_path, 'r') as log_file:
                for line in log_file:
                    if 'Accuracy' in line and '%' in line:
                        accuracy = line.strip().split(': ')[-1]
            training_jobs[job_id]['accuracy'] = accuracy
        else:
            training_jobs[job_id]['status'] = 'failed'
            training_jobs[job_id]['error'] = f'Script exited with code {process.returncode}'
            
    except Exception as e:
        training_jobs[job_id]['status'] = 'failed'
        training_jobs[job_id]['error'] = str(e)


@admin_bp.route('/retrain/<model_type>', methods=['POST'])
@admin_required
def trigger_retraining(model_type):
    """POST /api/admin/retrain/<model_type>"""
    valid_types = ['crop', 'disease', 'yield', 'fertilizer']
    if model_type not in valid_types:
        return api_error('Invalid model type', 400)
        
    job_id = str(uuid.uuid4())
    training_jobs[job_id] = {
        'id': job_id,
        'model_type': model_type,
        'status': 'pending',
        'start_time': datetime.utcnow().isoformat(),
        'accuracy': None,
        'error': None
    }
    
    # Start thread
    thread = threading.Thread(target=run_training_task, args=(job_id, model_type))
    thread.daemon = True
    thread.start()
    
    return api_response(data={'job_id': job_id}, message=f'Retraining started for {model_type}')


@admin_bp.route('/retrain/status/<job_id>', methods=['GET'])
@admin_required
def get_retrain_status(job_id):
    """GET /api/admin/retrain/status/<job_id>"""
    if job_id not in training_jobs:
        return api_error('Job not found', 404)
        
    job = training_jobs[job_id]
    
    # Tail the log file
    log_tail = []
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
    log_path = os.path.join(models_dir, f"{job['model_type']}_training.log")
    
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
                log_tail = lines[-30:] # Get last 30 lines
        except:
            pass
            
    response_data = job.copy()
    response_data['log_tail'] = log_tail
    
    return api_response(data=response_data)
