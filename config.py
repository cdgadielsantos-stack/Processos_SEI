import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/aneel_monitor.db")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Directories
DOWNLOAD_DIR = BASE_DIR / "downloads"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"

# Ensure directories exist
for dir_path in [DOWNLOAD_DIR, DATA_DIR, LOGS_DIR, EXPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# OCR (optional)
TESSERACT_CMD = os.getenv("TESSERACT_CMD", None)