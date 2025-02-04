# app_config/settings.py
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent
dotenv_path = BASE_DIR / ".env"

if not dotenv_path.exists():
    raise RuntimeError(f".env file not found at {dotenv_path}")

load_dotenv(dotenv_path)

# Core Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "").strip()
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "").strip()

# ID Validation
try:
    DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))
except ValueError:
    DISCORD_CHANNEL_ID = 0

try:
    TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID", 0))
except ValueError:
    TEST_GUILD_ID = 0

# Unified Validation
required_config = {
    "DISCORD_TOKEN": DISCORD_TOKEN,
    "HELIUS_API_KEY": HELIUS_API_KEY,
    "BIRDEYE_API_KEY": BIRDEYE_API_KEY,
    "DISCORD_CHANNEL_ID": DISCORD_CHANNEL_ID,
    "TEST_GUILD_ID": TEST_GUILD_ID
}

for name, value in required_config.items():
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    if "ID" in name and not isinstance(value, int):
        raise TypeError(f"Invalid type for {name} - must be integer")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logging.info("Configuration validated successfully")