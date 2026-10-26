"""Environment-based project configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

AIR_QUALITY_API_KEY = os.getenv("AIR_QUALITY_API_KEY", "").strip() or None
