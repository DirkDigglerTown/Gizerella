# bot/bot.py
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import os
import sys
import asyncio
from pathlib import Path
from src.app_config import settings

LOG_DIR = Path(__file__).parent.parent / "data"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,  # 💡 Changed to DEBUG
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",  # 💡 Added name
    handlers=[
        logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class MemeBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for degen trades"
            ),
            chunk_guilds_at_startup=False
        )
        self.launch_time = discord.utils.utcnow()

    async def setup_hook(self):
        await self.load_extension("bot.commands")
        await self.load_extension("bot.filters")
        await self.load_extension("bot.utils")
        await self.load_extension("bot.embeds")
        
        test_guild = discord.Object(id=settings.TEST_GUILD_ID)
        self.tree.copy_global_to(guild=test_guild)
        await self.tree.sync(guild=test_guild)
        await self.tree.sync()
        
        self.update_task.start()

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        logging.error(f"Unhandled error in {event_method}", exc_info=True)

    async def process_coins(self) -> list:
        """Orchestrate data collection from all sources"""
        try:
            valid_coins = []
            tokens = await self.get_cog("Utils").fetch_helius_assets()
            
            for token in tokens:
                contract = token.get("id", "")
                if not contract or not self.get_cog("Utils").validate_solana_address(contract):
                    continue

                metrics = await self.get_cog("Utils").fetch_birdeye_metrics(contract)
                if self.get_cog("Filters").meets_criteria(metrics):
                    coin_data = self.get_cog("Utils").format_coin_data(token, metrics)
                    valid_coins.append(coin_data)
            
            return sorted(valid_coins, key=lambda x: x["volume_5min"], reverse=True)[:5]
        
        except Exception as e:
            logging.error(f"Processing failed: {str(e)}")
            return []

    @tasks.loop(minutes=3)
    async def update_task(self):
        """Periodic market data update"""
        try:
            channel = self.get_channel(settings.DISCORD_CHANNEL_ID)
            if not channel:
                return

            coins = await self.process_coins()
            if coins:
                await self.update_embed(channel, coins)
            else:
                await self.handle_no_coins(channel)
        except Exception as e:
            logging.error(f"Update task failed: {str(e)}")

    async def update_embed(self, channel, coins):
        """Handle message update/create"""
        messages = [msg async for msg in channel.history(limit=1)]
        embed = self.get_cog("Embeds").create_embed(coins)
        
        if messages and messages[0].author == self.user:
            await messages[0].edit(embed=embed)
        else:
            await channel.send(embed=embed)

    async def handle_no_coins(self, channel):
        """No coins found handler"""
        logging.info("⚠️ No matching coins found")
        await channel.send("⚠️ No coins matched filters. Retrying in 3 minutes.")

bot = MemeBot()

# 💡 Add this ON_READY handler right here (line 107)
@bot.event
async def on_ready():
    """Critical startup handler"""
    logging.debug("=== STARTUP INITIATED ===")
    logging.debug(f"Loaded Cogs: {list(bot.cogs.keys())}")
    logging.debug(f"Scheduled Tasks: {len(bot._scheduled_tasks)}")
    logging.debug(f"Test Guild: {settings.TEST_GUILD_ID}")
    logging.debug(f"Channel ID: {settings.DISCORD_CHANNEL_ID}")
    
    logging.info(f"Bot online: {bot.user} | Guilds: {len(bot.guilds)}")
    
    if not bot.update_task.is_running():
        logging.debug("Launching update task...")
        bot.update_task.start()

@bot.tree.command(name="restart", description="Restart the bot (Admin only)")
@app_commands.guilds(discord.Object(id=settings.TEST_GUILD_ID))
@app_commands.default_permissions(administrator=True)
async def restart(interaction: discord.Interaction):
    """Secure container-friendly restart"""
    await interaction.response.send_message("🔄 Restarting...")
    logging.info(f"Restart initiated by {interaction.user}")
    os.execv(sys.executable, ["python", "-m", "bot.bot"])

if __name__ == "__main__":
    try:
        bot.run(settings.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logging.info("Bot shutdown requested")
        bot.loop.run_until_complete(bot.close())
    except Exception as e:
        logging.critical(f"Critical failure: {str(e)}")
        bot.loop.run_until_complete(bot.close())
        sys.exit(1)
    finally:
        if not bot.is_closed():
            bot.loop.run_until_complete(bot.close())
        asyncio.set_event_loop(asyncio.new_event_loop())