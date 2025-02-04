import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from src.app_config import settings
from src.bot.utils import fetch_helius_assets, fetch_birdeye_metrics

async def test():
    print("=== HELIUS API TEST ===")
    try:
        assets = await fetch_helius_assets()
        print(f"Received {len(assets)} assets")
        if assets:
            print("Sample asset:", assets[0]["id"][:10] + "...")
    except Exception as e:
        print(f"Helius error: {str(e)}")

    print("\n=== BIRDEYE API TEST ===")
    try:
        metrics = await fetch_birdeye_metrics("So11111111111111111111111111111111111111112")
        print(f"Liquidity: {metrics['liquidity']}")
        print(f"Volume 24h: {metrics['volume_24h']}")
    except Exception as e:
        print(f"Birdeye error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test())