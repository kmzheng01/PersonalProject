"""Configuration management for AudioStream."""

import os
import yaml
from typing import Dict, Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_file: str = 'config/default_config.yaml'):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
        logger.info("ConfigManager initialized")

    def load_config(self) -> bool:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            logger.warning(f"Config file not found: {self.config_file}, using defaults")
            self._setup_defaults()
            return False
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"Config loaded from {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._setup_defaults()
            return False

    def _setup_defaults(self) -> None:
        """Setup default configuration."""
        self.config = {
            'app': {
                'name': 'AudioStream',
                'version': '1.0.0',
                'debug': False,
            },
            'audio': {
                'sample_rate': 44100,
                'channels': 2,
                'format': 'PCM_16',
                'auto_output_detect': True,
            },
            'web': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
            },
            'hardware': {
                'enable_rpi_gpio': True,
                'enable_display': True,
                'enable_esp': True,
            },
            'library': {
                'music_dir': './music',
                'auto_scan': True,
            },
            'torrenting': {
                'enabled': False,
                'max_concurrent': 3,
                'download_dir': './downloads',
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (dot notation supported, e.g., 'audio.sample_rate')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Config set: {key} = {value}")

    def save_config(self, filepath: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            filepath: File path to save to (uses default if not provided)
            
        Returns:
            True if successful
        """
        filepath = filepath or self.config_file
        
        try:
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            
            with open(filepath, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Config saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self.config.copy()

    def reset_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._setup_defaults()
        logger.info("Config reset to defaults")

    def validate(self) -> bool:
        """Validate configuration."""
        required_keys = [
            'app', 'audio', 'web', 'library'
        ]
        
        for key in required_keys:
            if key not in self.config:
                logger.warning(f"Missing required config key: {key}")
                return False
        
        logger.info("Config validation passed")
        return True
