# bot/utils.py
import aiohttp
import logging
from src.app_config import settings
from src.bot.helpers import (
    photon_url,
    dexscreener_url,
    truncate,
    safe_get,
    safe_number,
    safe_float,
    trend_emoji
)
from solders.pubkey import Pubkey

class RateLimiter:
    """Async rate limiter for API calls"""
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.semaphore = asyncio.Semaphore(calls_per_minute)
        self.lock = asyncio.Lock()
        self.last_reset = time.monotonic()
        self.call_count = 0

    async def __aenter__(self):
        async with self.lock:
            elapsed = time.monotonic() - self.last_reset
            if elapsed > 60:
                self.last_reset = time.monotonic()
                self.call_count = 0
                
            if self.call_count >= self.calls_per_minute:
                sleep_time = 60 - elapsed
                logging.warning(f"Rate limit hit. Sleeping {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
                self.last_reset = time.monotonic()
                self.call_count = 0
                
            self.call_count += 1
        return await self.semaphore.acquire()

    async def __aexit__(self, *args):
        self.semaphore.release()

HELIUS_RL = RateLimiter(120)  # Helius 120 RPM limit
BIRDEYE_RL = RateLimiter(60)   # BirdEye 60 RPM limit

async def fetch_async(
    url: str, 
    method: str = "GET",
    headers: Optional[Dict] = None,
    json: Optional[Dict] = None
) -> Optional[Dict]:
    """Generic async HTTP client with retry logic"""
    async with aiohttp.ClientSession() as session:
        for attempt in range(3):
            try:
                async with session.request(
                    method, url, headers=headers, json=json, timeout=20
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.warning(f"Request failed (attempt {attempt+1}/3): {str(e)}")
                await asyncio.sleep(2 ** attempt)
        return None

def validate_solana_address(address: str) -> bool:
    """Validate Solana address format"""
    try:
        Pubkey.from_string(address)
        return True
    except ValueError:
        return False

async def fetch_jupiter_price(mint: str) -> float:
    """Get current price from Jupiter API"""
    if not validate_solana_address(mint):
        return 0.0
    
    async with HELIUS_RL:
        url = f"https://price.jup.ag/v4/price?ids={mint}"
        data = await fetch_async(url)
        return float(data["data"][mint]["price"]) if data else 0.0

async def fetch_birdeye_metrics(mint: str) -> Dict[str, float]:
    """Get token metrics from Birdeye"""
    if not validate_solana_address(mint):
        return {"liquidity": 0, "volume_24h": 0, "market_cap": 0}
    
    async with BIRDEYE_RL:
        url = f"https://public-api.birdeye.so/public/token?address={mint}"
        headers = {"X-API-KEY": settings.BIRDEYE_API_KEY}
        data = await fetch_async(url, headers=headers)
        
        return {
            "liquidity": float(data.get("liquidity", 0)),
            "volume_24h": float(data.get("volume24h", 0)),
            "market_cap": float(data.get("marketCap", 0))
        }

async def fetch_helius_assets() -> List[Dict]:
    """Fetch trending tokens from Helius DAS"""
    async with HELIUS_RL:
        url = f"https://mainnet.helius-rpc.com/?api-key={settings.HELIUS_API_KEY}"
        payload = {
            "jsonrpc": "2.0",
            "id": "meme-scanner",
            "method": "searchAssets",
            "params": {
                "owner": None,
                "compressed": False,
                "page": 1,
                "limit": 50
            }
        }
        data = await fetch_async(url, method="POST", json=payload)
        return data.get("result", {}).get("items", [])

async def fetch_pumpfun_description(mint: str) -> str:
    """Scrape pump.fun token description"""
    if not validate_solana_address(mint):
        return "Invalid address"
    
    try:
        url = f"https://pump.fun/{mint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                meta = soup.find("meta", {"name": "description"})
                return meta["content"].strip() if meta else "No description available"
    except Exception as e:
        logging.error(f"Pump.fun scrape failed: {str(e)}")
        return "Description unavailable"

def format_coin_data(
    token: Dict, 
    metrics: Dict
) -> Dict[str, Any]:
    """Structure normalized coin data"""
    return {
        "name": token.get("content", {}).get("metadata", {}).get("name", "Unknown"),
        "symbol": token.get("content", {}).get("metadata", {}).get("symbol", "?"),
        "price": metrics.get("price", 0),
        "liquidity": metrics.get("liquidity", 0),
        "market_cap": metrics.get("market_cap", 0),
        "volume_5min": metrics.get("volume_24h", 0) / 288,
        "contract": token.get("id", ""),
        "image": next(iter(token.get("content", {}).get("files", [])), {}).get("uri", ""),
        "description": metrics.get("description", "")
    }