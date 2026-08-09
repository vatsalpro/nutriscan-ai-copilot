import os
import sys

# Ensure backend directory is in sys.path for Vercel Serverless Functions
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database.seed import seed_database
try:
    seed_database()
except Exception as e:
    print(f"Vercel DB initialization: {e}")

from main import app

