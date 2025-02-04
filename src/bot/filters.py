# bot/filters.py
import json
import logging
import threading
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any

FILTERS_PATH = Path(__file__).parent.parent / 'data/filters.json'
LOCK = threading.Lock()

class FilterSystem:
    """Thread-safe filter management system"""
    def __init__(self):
        self._filters = self._load_filters()
        self._defaults = self._get_default_filters()
        
    def _load_filters(self) -> Dict[str, Any]:
        """Load filters with atomic read and validation"""
        with LOCK:
            try:
                if not FILTERS_PATH.exists():
                    self._create_initial_filters()
                    
                raw_data = FILTERS_PATH.read_text(encoding='utf-8')
                filters = json.loads(raw_data)
                return self._validate_filters(filters)
                
            except json.JSONDecodeError:
                logging.error("Corrupted filters - resetting to defaults")
                return self._reset_to_defaults()
            except Exception as e:
                logging.critical(f"Filter load failure: {str(e)}")
                return self._get_default_filters()

    def _validate_filters(self, filters: Dict) -> Dict:
        """Ensure all required filter keys exist"""
        required_keys = self._get_default_filters().keys()
        return {
            key: filters.get(key, default)
            for key, default in self._get_default_filters().items()
        }

    def _reset_to_defaults(self) -> Dict:
        """Reset filters and return defaults"""
        defaults = self._get_default_filters()
        self._save_filters(defaults)
        return defaults

    def _create_initial_filters(self):
        """Initialize filters file with defaults"""
        FILTERS_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._save_filters(self._get_default_filters())

    def _save_filters(self, filters: Dict) -> None:
        """Atomic filter persistence"""
        try:
            with NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=FILTERS_PATH.parent,
                delete=False
            ) as tmp:
                json.dump(filters, tmp, indent=2)
                
            Path(tmp.name).replace(FILTERS_PATH)
        except Exception as e:
            logging.error(f"Filter save failed: {str(e)}")
            raise RuntimeError(f"Critical filter save error: {str(e)}") from e

    def get_filters(self) -> Dict[str, Any]:
        """Get current filter values"""
        with LOCK:
            return self._filters.copy()

    def update_filter(self, key: str, value: Any) -> None:
        """Thread-safe filter update"""
        with LOCK:
            try:
                self._filters[key] = self._validate_value(key, value)
                self._save_filters(self._filters)
            except ValueError as e:
                logging.error(f"Invalid filter value: {str(e)}")
                raise

    def _validate_value(self, key: str, value: Any) -> Any:
        """Type and range validation"""
        defaults = self._get_default_filters()
        
        if key not in defaults:
            raise ValueError(f"Invalid filter key: {key}")
            
        if not isinstance(value, type(defaults[key])):
            raise TypeError(f"Invalid type for {key} - expected {type(defaults[key])}")
            
        # Special validation for ranges
        if key == "min_market_cap" and value >= self._filters["max_market_cap"]:
            raise ValueError("Min market cap must be less than max")
            
        if key == "max_market_cap" and value <= self._filters["min_market_cap"]:
            raise ValueError("Max market cap must be greater than min")
            
        return value

    def _get_default_filters(self) -> Dict[str, int]:
        """Original default values preserved"""
        return {
            "min_liquidity": 80000,
            "min_market_cap": 150000,
            "max_market_cap": 11000000,
            "min_5m_volume": 150000
        }

    def add_filter(self, guild_id: str, token_address: str) -> None:
        """Original filter addition logic preserved"""
        with LOCK:
            guild_filters = self._filters.setdefault(guild_id, [])
            if token_address not in guild_filters:
                guild_filters.append(token_address)
                self._save_filters(self._filters)