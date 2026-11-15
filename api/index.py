import os
import sys

# Vercel loads this file as the serverless handler for every route.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app import app  # noqa: E402,F401  (Flask WSGI app)
