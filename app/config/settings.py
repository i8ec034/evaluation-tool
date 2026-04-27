import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Database Configuration
DB_URL = os.getenv("DB_URL", "sqlite:///evaluation.db")

# Excel File Configuration
EXCEL_FILE = os.getenv("EXCEL_FILE", "data/users.xlsx")
ADMIN_SHEET = os.getenv("ADMIN_SHEET", "admin")
USER_SHEET = os.getenv("USER_SHEET", "users")
GUEST_SHEET = os.getenv("GUEST_SHEET", "guest")
DOMAIN_SHEET = os.getenv("DOMAIN_SHEET", "domains")

# LLM settings
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
OVERLAP = int(os.getenv("OVERLAP", "200"))
QA_PER_CHUNK = int(os.getenv("QA_PER_CHUNK", "10"))
CHUNK_TOKEN_THRESHOLD = int(os.getenv("CHUNK_TOKEN_THRESHOLD", "4000"))
MAX_ATTEMPTS_PER_USER_PER_DOMAIN = int(os.getenv("MAX_ATTEMPTS_PER_USER_PER_DOMAIN", "3"))

# Quiz settings
QUESTIONS_PER_QUIZ = int(os.getenv("QUESTIONS_PER_QUIZ", "20"))
THRESHOLD = float(os.getenv("THRESHOLD", "0.7"))
INTERACTIVE_MODE = os.getenv("INTERACTIVE_MODE", "True").lower() == "true"
ALLOW_REVIEW_BEFORE_SUBMIT = os.getenv("ALLOW_REVIEW_BEFORE_SUBMIT", "False").lower() == "true"

# Vector search settings
ENABLE_VECTOR_SEARCH = os.getenv("ENABLE_VECTOR_SEARCH", "False").lower() == "true"
VECTOR_SEARCH_RESULTS = int(os.getenv("VECTOR_SEARCH_RESULTS", "20"))