"""
Flask Application Factory.
Creates and configures the Flask application, registers blueprints,
initializes extensions, and loads ML models at startup.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, send_from_directory, Request, request

from backend.config import config_map
from backend.extensions import db, jwt, mail, cache, limiter, bcrypt, cors, talisman, compress
from backend.services.logger import setup_advanced_logging

class SanitizedRequest(Request):
    def get_json(self, *args, **kwargs):
        data = super().get_json(*args, **kwargs)
        if data:
            from backend.utils.helpers import sanitize_input
            return sanitize_input(data)
        return data


def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
    )
    app.request_class = SanitizedRequest
    
    # Load configuration
    app.config.from_object(config_map.get(config_name, config_map['development']))
    
    # Initialize extensions
    _init_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Setup logging
    setup_advanced_logging(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Serve frontend pages
    _register_frontend_routes(app)
    # Load ML Models at startup
    if not app.config.get('TESTING'):
        from backend.services.model_registry import model_registry
        model_registry.load_all_models()
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_status = "connected"
        try:
            db.session.execute('SELECT 1')
        except Exception:
            db_status = "disconnected"
            
        return jsonify({
            "status": "ok",
            "db": db_status,
            "models_loaded": True
        }), 200

    @app.after_request
    def add_etag(response):
        if response.status_code == 200 and request.method in ['GET', 'HEAD']:
            response.add_etag()
            return response.make_conditional(request)
        return response

    return app

def _init_extensions(app):
    """Initialize all Flask extensions with the app."""
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    bcrypt.init_app(app)
    
    # Security Hardening
    allowed_origins = os.getenv('FRONTEND_URL', 'http://localhost:5000,http://127.0.0.1:5000').split(',')
    cors.init_app(app, resources={r"/api/*": {"origins": allowed_origins}})
    
    csp = {
        'default-src': ["'self'"],
        'img-src': ["'self'", "data:", "blob:"],
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"],
        'font-src': ["'self'", "https://cdnjs.cloudflare.com"]
    }
    talisman.init_app(app, content_security_policy=csp, force_https=False)
    compress.init_app(app)
    # Configure JWT token blocklist loader
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        from backend.models.token_blocklist import TokenBlocklist
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None

    # Create database tables
    with app.app_context():
        import backend.models  # Import models so they are registered before create_all
        db.create_all()


def _register_blueprints(app):
    """Register all route blueprints."""
    from backend.routes.auth import auth_bp
    from backend.routes.history import history_bp
    from backend.routes.weather import weather_bp
    from backend.routes.recommend import recommend_bp
    from backend.routes.detect import detect_bp
    from backend.routes.predict import predict_bp
    from backend.routes.admin import admin_bp
    from backend.routes.notifications import notifications_bp
    from backend.routes.report import report_bp
    from backend.routes.market import market_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    app.register_blueprint(detect_bp, url_prefix='/api/detect')
    app.register_blueprint(predict_bp, url_prefix='/api/predict')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    app.register_blueprint(market_bp, url_prefix='/api/market')


# Logging is now handled by backend.services.logger.setup_advanced_logging


def _register_error_handlers(app):
    """Register global error handlers following the standard API response format."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": "Bad request",
            "code": 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": "Unauthorized access",
            "code": 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            "error": "Forbidden",
            "code": 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "Resource not found",
            "code": 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "code": 500
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            "success": False,
            "error": "Model not available",
            "code": 503
        }), 503


def _register_frontend_routes(app):
    """Serve frontend HTML pages."""
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    @app.route('/')
    @limiter.exempt
    def index():
        return send_from_directory(frontend_dir, 'login.html')
    
    @app.route('/<path:filename>.html')
    @limiter.exempt
    def serve_page(filename):
        return send_from_directory(frontend_dir, f'{filename}.html')


# Application entry point
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
