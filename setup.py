# setup.py
from setuptools import setup, find_packages

setup(
    name="solana-meme-bot",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'discord.py==2.3.2',
        'solders>=0.23.0',
        'solana>=0.29.0',
        'aiohttp==3.10.11',
        'python-dotenv==1.0.0',
        'beautifulsoup4==4.12.2'
    ],
)