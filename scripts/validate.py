import json
from pathlib import Path

def validate_project_structure():
    required = {
        'directories': [
            'bot',
            'app_config',
            'data',
            'scripts/deploy',
            'docs'
        ],
        'files': [
            'bot/bot.py',
            'app_config/settings.py',
            'scripts/setup.py',
            'data/filters.json',
            '.gitignore'
        ]
    }

    errors = []
    
    for dir in required['directories']:
        if not Path(dir).exists():
            errors.append(f"Missing directory: {dir}")
    
    for file in required['files']:
        if not Path(file).exists():
            errors.append(f"Missing file: {file}")
    
    if errors:
        print("❌ Validation failed:")
        for error in errors:
            print(f" - {error}")
        exit(1)
    else:
        print("✅ Project structure valid")

if __name__ == "__main__":
    validate_project_structure()