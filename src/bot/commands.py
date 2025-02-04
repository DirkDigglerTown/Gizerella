# src/bot/commands.py
from discord import app_commands
import discord
from src.app_config import settings
from src.bot.filters import FilterSystem
from src.bot.helpers import (
    safe_get,
    safe_number,
    safe_float,
    trend_emoji
)
import logging

class MemeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.filter_system = FilterSystem()

    @app_commands.command(name="addfilter", description="Add token to watchlist")
    @app_commands.guilds(discord.Object(id=settings.TEST_GUILD_ID))
    @app_commands.default_permissions(manage_guild=True)
    async def add_filter(self, interaction: discord.Interaction, token_address: str):
        """Original functionality preserved with enhanced validation"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            if not validate_transaction(token_address):
                await interaction.followup.send(embed=error_embed("Invalid token address"))
                return

            self.filter_system.add_filter(
                guild_id=str(interaction.guild_id),
                token_address=token_address
            )
            await interaction.followup.send(
                f"Added {token_address} to watchlist",
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Filter error: {e}", exc_info=True)
            await interaction.followup.send(
                embed=error_embed("Filter operation failed"),
                ephemeral=True
            )

    @app_commands.command(name="memesearch", description="Find latest meme coin trades")
    async def meme_search(self, interaction: discord.Interaction, token_address: str):
        """Preserved original search functionality with async"""
        try:
            await interaction.response.defer()
            
            data = await fetch_helius_assets(token_address)
            if not data:
                await interaction.followup.send(embed=error_embed("No trading activity found"))
                return

            embed = create_meme_embed(data)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logging.error(f"Search error: {e}", exc_info=True)
            await interaction.followup.send(embed=error_embed("Search failed"))

    @app_commands.command(name="set_liquidity", description="Set minimum liquidity threshold")
    @app_commands.guilds(discord.Object(id=settings.TEST_GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def set_liquidity(self, interaction: discord.Interaction, min_value: int):
        """Admin command with validation"""
        try:
            if min_value < 0:
                await interaction.response.send_message("❌ Value must be positive!", ephemeral=True)
                return
                
            self.filter_system.update_filter("min_liquidity", min_value)
            await interaction.response.send_message(
                f"✅ Minimum liquidity set to **${min_value:,}**",
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Set liquidity error: {e}")
            await interaction.response.send_message(
                "❌ Failed to update liquidity filter", 
                ephemeral=True
            )

    @app_commands.command(name="set_market_cap", description="Set market cap range")
    @app_commands.guilds(discord.Object(id=settings.TEST_GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def set_market_cap(self, interaction: discord.Interaction, 
                           min_value: int, max_value: int):
        """Preserved range validation"""
        try:
            if min_value >= max_value:
                await interaction.response.send_message("❌ Min must be less than max!", ephemeral=True)
                return
                
            self.filter_system.update_filter("min_market_cap", min_value)
            self.filter_system.update_filter("max_market_cap", max_value)
            await interaction.response.send_message(
                f"✅ Market cap range set to **${min_value:,}-${max_value:,}**",
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Set market cap error: {e}")
            await interaction.response.send_message(
                "❌ Failed to update market cap filters", 
                ephemeral=True
            )

    @app_commands.command(name="set_volume", description="Set minimum 5-minute volume")
    @app_commands.guilds(discord.Object(id=settings.TEST_GUILD_ID))
    @app_commands.default_permissions(administrator=True)
    async def set_volume(self, interaction: discord.Interaction, min_value: int):
        """Volume filter preservation"""
        try:
            if min_value < 0:
                await interaction.response.send_message("❌ Value must be positive!", ephemeral=True)
                return
                
            self.filter_system.update_filter("min_5m_volume", min_value)
            await interaction.response.send_message(
                f"✅ Minimum 5m volume set to **${min_value:,}**",
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Set volume error: {e}")
            await interaction.response.send_message(
                "❌ Failed to update volume filter", 
                ephemeral=True
            )

    @app_commands.command(name="filters", description="Show current filtering criteria")
    async def show_filters(self, interaction: discord.Interaction):
        """Preserved embed display with current filters"""
        try:
            filters = self.filter_system.get_filters()
            embed = discord.Embed(
                title="🔍 Active Filters",
                color=0x00ff00,
                description="**Token Qualification Requirements:**"
            )
            embed.add_field(
                name="Minimum Liquidity",
                value=f"${filters['min_liquidity']:,}",
                inline=True
            )
            embed.add_field(
                name="Market Cap Range",
                value=f"${filters['min_market_cap']:,} - ${filters['max_market_cap']:,}",
                inline=True
            )
            embed.add_field(
                name="5-Min Volume Threshold",
                value=f"${filters['min_5m_volume']:,}",
                inline=True
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            logging.error(f"Show filters error: {e}")
            await interaction.response.send_message(
                "❌ Failed to retrieve filters", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(MemeCommands(bot))