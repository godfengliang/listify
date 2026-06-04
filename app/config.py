import os
import sys
from dotenv import load_dotenv

load_dotenv()

# AI Engine
AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-v4-pro")

# Lemon Squeezy
LEMON_SQUEEZY_API_KEY = os.getenv("LEMON_SQUEEZY_API_KEY")
LEMON_SQUEEZY_STORE_ID = os.getenv("LEMON_SQUEEZY_STORE_ID")

# Validate critical config on startup
if not AI_API_KEY:
    print("WARNING: AI_API_KEY not set. Listing generation will fail.", file=sys.stderr)
if not LEMON_SQUEEZY_API_KEY:
    print("WARNING: LEMON_SQUEEZY_API_KEY not set. Payments will not work.", file=sys.stderr)
