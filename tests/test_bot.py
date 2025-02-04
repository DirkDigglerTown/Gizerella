import unittest
from src.bot.filters import load_filters, save_filters, get_default_filters
from src.bot.utils import get_top_solana_meme_coins
from src.config.settings import DISCORD_TOKEN, HELIUS_API_KEY, CHANNEL_ID

class TestBotFunctions(unittest.TestCase):

    def test_load_filters(self):
        """Ensure filters load correctly and include expected keys."""
        filters = load_filters()
        default_keys = ["min_liquidity", "min_market_cap", "max_market_cap", "max_pair_age_hours", "min_5m_volume", "max_5m_volume"]
        for key in default_keys:
            self.assertIn(key, filters)

    def test_save_filters(self):
        """Ensure saving and loading filters work as expected."""
        test_filters = {
            "min_liquidity": 100000,
            "min_market_cap": 200000,
            "max_market_cap": 5000000,
            "max_pair_age_hours": 48,
            "min_5m_volume": 250000,
            "max_5m_volume": 15000000
        }
        save_filters(test_filters)
        loaded_filters = load_filters()
        self.assertEqual(test_filters, loaded_filters)

    def test_helius_api_key_exists(self):
        """Ensure Helius API Key is set."""
        self.assertIsNotNone(HELIUS_API_KEY)

    def test_discord_token_exists(self):
        """Ensure Discord Bot Token is set."""
        self.assertIsNotNone(DISCORD_TOKEN)

    def test_channel_id_exists(self):
        """Ensure Discord Channel ID is set."""
        self.assertIsInstance(CHANNEL_ID, int)

    def test_get_top_solana_meme_coins(self):
        """Test API call to fetch Solana meme coins."""
        tokens = get_top_solana_meme_coins()
        self.assertIsInstance(tokens, list)

if __name__ == "__main__":
    unittest.main()
