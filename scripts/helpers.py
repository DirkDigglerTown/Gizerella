# src/bot/helpers.py
from typing import Any, Dict

def safe_get(data: Dict, key: str, default: str = "N/A") -> str:
    return str(data.get(key, default))[:50]

def safe_number(data: Dict, key: str) -> str:
    return f"{int(data.get(key, 0)):,}" if data.get(key) else "0"

def safe_float(data: Dict, key: str) -> str:
    return f"{float(data.get(key, 0)):.4f}".rstrip('0').rstrip('.') if data.get(key) else "0.0000"

def trend_emoji(token: Dict) -> str:
    vol = token.get('volume_5min', 0)
    return "🚀" if vol > 500000 else "📈" if vol > 100000 else "📉"

def photon_url(token: Dict) -> str:
    base = "https://photon-sol.tinyastro.io/en/lp/"
    return base + token.get('contract', '') if token.get('contract') else base

def dexscreener_url(token: Dict) -> str:
    base = "https://dexscreener.com/solana/"
    return base + token.get('contract', '') if token.get('contract') else base

def truncate(text: str, max_length: int) -> str:
    return (text[:max_length] + '...') if len(text) > max_length else text