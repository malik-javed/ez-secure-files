import os
from dotenv import load_dotenv
import pathlib

# Load environment variables from .env file if it exists
load_dotenv()

# Base directory
BASE_DIR = pathlib.Path(__file__).parent.parent.parent

# MongoDB settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "file_sharing_db3")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "users")
    
# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")  # Change this in production!
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")) 

# Email settings
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_FROM = os.getenv("MAIL_FROM", "personalprojects123400@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "dhijkhxeqgmupnao")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_TLS = True
MAIL_SSL = False

# Development settings
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
BYPASS_EMAIL_VERIFICATION = os.getenv("BYPASS_EMAIL_VERIFICATION", "false").lower() == "true"

# File storage settings
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = ["pptx", "docx", "xlsx"]

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True) 