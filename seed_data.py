"""
Convenience script to seed the database with sample users from the repository root.
Usage:
    python seed_data.py
"""
import sys
from pathlib import Path

# Add project directories to Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "fastapi_project"))

from fastapi_project.app.seed import run_seed

if __name__ == "__main__":
    run_seed()

