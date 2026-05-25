"""
Flask extension instances.
These are created here (without an app) and initialized in app.py via init_app().
This avoids circular imports between modules.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Database ORM
db = SQLAlchemy()

# JWT Authentication
jwt = JWTManager()

# Email
mail = Mail()

# Caching
cache = Cache()

# Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://",
    enabled=True,
)

# Password Hashing
bcrypt = Bcrypt()

# CORS
cors = CORS()

# Security Headers
from flask_talisman import Talisman
talisman = Talisman()

# Response Compression
from flask_compress import Compress
compress = Compress()
