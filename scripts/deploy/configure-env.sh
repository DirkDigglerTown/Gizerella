#!/bin/bash
# Guides user through .env setup
read -p "Enter Discord Bot Token: " DISCORD_BOT_TOKEN
read -p "Enter Helius API Key: " HELIUS_API_KEY
read -p "Enter Birdeye API Key: " BIRDEYE_API_KEY

cat > ../../app_config/.env <<EOL
DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN
DISCORD_CHANNEL_ID=YOUR_CHANNEL_ID
HELIUS_API_KEY=$HELIUS_API_KEY
BIRDEYE_API_KEY=$BIRDEYE_API_KEY
SCRAPER_API_KEY=YOUR_SCRAPERAPI_KEY
EOL