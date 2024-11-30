import os

# API Configuration
API_KEY = os.getenv("API_KEY", "your_api_key_here")
BASE64_PRIVATE_KEY = os.getenv("PRIVATE_KEY", "your_private_key_here")

# Logging Configuration
LOGGING_CONFIG = {
    "filename": "trading_scheduler.log",
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
}
