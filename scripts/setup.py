# scripts/setup.py
from setuptools import setup, find_packages
setup(
    ...
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ...
)
from pathlib import Path

# ✅ Load requirements from file
requirements = (Path(__file__).parent.parent / "requirements.txt").read_text().splitlines()

setup(
    name="solana-meme-bot",
    version="1.2.0",  # Semantic versioning
    packages=find_packages(include=["bot", "app_config", "utils"]),
    install_requires=requirements,
    python_requires=">=3.10",  # Match your runtime environment
    entry_points={
        "console_scripts": [
            "meme-bot=bot.bot:main"  # Ensure bot.py has main()
        ]
    },
    include_package_data=True,  # ✅ Critical for .env/filters.json
    package_data={
        "app_config": ["*.env"],
        "bot": ["data/*.json"]
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Communications :: Chat",
        "Framework :: AsyncIO"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Real-time Solana meme coin tracking bot with dynamic filters",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/solana-meme-bot"
)