"""Application configuration and constants."""
from pathlib import Path

# Relative path ensures it works locally and on Streamlit Cloud
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "skillbridge.db")

DEPARTMENTS = [
    "Computer Science",
    "Commerce",
    "Design",
    "Psychology",
    "Management",
    "Engineering",
    "Arts",
    "Other",
]
