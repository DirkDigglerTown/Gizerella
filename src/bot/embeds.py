# src/bot/embeds.py
import discord
import logging
from typing import List, Dict
from src.bot.helpers import (
    safe_get,
    safe_number,
    safe_float,
    trend_emoji,
    photon_url,
    dexscreener_url,
    truncate
)

def create_embed(meme_coins: List[Dict]) -> discord.Embed:
    """Generates rich embed for meme coin display with validation"""
    embed = discord.Embed(
        title="🚀 Top Trending Solana Meme Coins",
        color=0x5865F2,
        description="**Real-time market data (Updated every 3 minutes)**\n\u200b"
    )
    
    thumbnail_set = False
    for idx, token in enumerate(meme_coins[:5], 1):
        try:
            field_content = format_coin_data(token)
            embed.add_field(
                name=f"{idx}. {safe_get(token, 'name', 'Unknown')} ({safe_get(token, 'symbol', '?')})",
                value=field_content,
                inline=False
            )
            
            if not thumbnail_set and safe_get(token, 'image'):
                embed.set_thumbnail(url=token['image'])
                thumbnail_set = True
                
        except Exception as e:
            logging.error(f"Embed creation error for token {idx}: {str(e)}")

    embed.set_footer(
        text="🔍 Data Sources: Helius | Birdeye | Jupiter", 
        icon_url="https://i.imgur.com/7Q4RJs6.png"
    )
    return embed

def format_coin_data(token: Dict) -> str:
    """Safely formats token data with fallback values"""
    return (
        f"▸ **MC:** ${safe_number(token, 'market_cap')}\n"
        f"▸ **Liquidity:** ${safe_number(token, 'liquidity')}\n"
        f"▸ **5m Vol:** ${safe_number(token, 'volume_5min')} {trend_emoji(token)}\n"
        f"▸ **Price:** ${safe_float(token, 'price')}\n"
        f"▸ **Links:** [Photon]({photon_url(token)}) | [DexScreener]({dexscreener_url(token)})\n"
        f"▸ **Description:** {truncate(safe_get(token, 'description', 'No description'), 150)}"
    )
    except KeyError as e:
        logging.error(f"Missing key in token data: {str(e)}")

def photon_url(token: Dict) -> str:
    return f"https://photon-sol.tinyastro.io/en/lp/{token.get('contract', '')}"

def dexscreener_url(token: Dict) -> str:
    return f"https://dexscreener.com/solana/{token.get('contract', '')}"

def set_thumbnail(embed: discord.Embed, token: Dict) -> None:
    """Sets thumbnail if available."""
    if url := token.get("image"):
        embed.set_thumbnail(url=url)