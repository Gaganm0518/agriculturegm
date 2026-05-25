import os
import time
import json
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from werkzeug.exceptions import HTTPException

def setup_logger(name, log_dir=None, level=logging.INFO):
    """
    Create and return a configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_format = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, 'app.log'),
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
            )
            file_handler.setLevel(level)
            file_format = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] [%(funcName)s:%(lineno)d] %(message)s')
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
            
    return logger

def setup_advanced_logging(app):
    """Sets up advanced logging including request/response logging, ML auditing, and error tracebacks."""
    
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    @app.before_request
    def start_timer():
        g.start_time = time.time()
        
    @app.after_request
    def log_request(response):
        if request.path.startswith('/static/') or request.path.endswith('.html') or request.path == '/':
            return response
            
        duration_ms = int((time.time() - getattr(g, 'start_time', time.time())) * 1000)
        
        user_id = 'anonymous'
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                user_id = identity
        except Exception:
            pass

        app.logger.info(
            f"API Request | {request.method} {request.path} | "
            f"User: {user_id} | Status: {response.status_code} | "
            f"Duration: {duration_ms}ms"
        )
        return response

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        if isinstance(e, HTTPException):
            return e
            
        app.logger.error(f"Unhandled Exception on {request.method} {request.path}: {str(e)}", exc_info=True)
        return {"success": False, "error": "Internal server error", "code": 500}, 500

def log_ml_prediction(model_name, user_id, input_data, output_result):
    """Log an ML prediction securely with an input hash for auditing."""
    try:
        input_str = json.dumps(input_data, sort_keys=True)
        input_hash = hashlib.sha256(input_str.encode('utf-8')).hexdigest()[:16]
        
        logger = logging.getLogger('flask.app')
        logger.info(
            f"ML Prediction | Model: {model_name} | User: {user_id} | "
            f"InputHash: {input_hash} | Result: {output_result}"
        )
    except Exception as e:
        logger = logging.getLogger('flask.app')
        logger.error(f"Failed to log ML prediction: {str(e)}")
