from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DB_PATH = PROJECT_DIR / "olms.sqlite"
APP_NAME = "OLMS - Operational Logistics Management System"
DEFAULT_WAREHOUSE = "MZALPHA1"
