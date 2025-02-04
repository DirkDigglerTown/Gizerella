#!/bin/bash
# Installs dependencies and bot
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r ../requirements.txt
python3 ../scripts/setup.py install