"""
Entry point for running the Flask application.
Run with: python run.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
