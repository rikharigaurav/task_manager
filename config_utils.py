# config_utils.py - Configuration utilities for the application

import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("config.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("config_utils")

# Default configuration
DEFAULT_CONFIG = {
    "database": {
        "path": "database/tasks.db",
        "backup_enabled": True,
        "backup_interval": 86400,  # 24 hours in seconds
        "last_backup": None
    },
    "api": {
        "host": "localhost",
        "port": 5000,
        "debug": False,
        "cors_enabled": True,
        "rate_limit": 100  # requests per minute
    },
    "logging": {
        "level": "INFO",
        "file_enabled": True,
        "console_enabled": True,
        "max_file_size": 10485760,  # 10MB
        "backup_count": 3
    }
}

CONFIG_FILE_PATH = "config.json"

class ConfigManager:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from file or create with defaults"""
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r') as f:
                    self._config = json.load(f)
                logger.info("Configuration loaded from file")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                self._config = DEFAULT_CONFIG.copy()
                self._save_config()
        else:
            logger.info("No configuration file found, creating with defaults")
            self._config = DEFAULT_CONFIG.copy()
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(self._config, f, indent=4)
            logger.info("Configuration saved to file")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get_config(self):
        """Get the entire configuration"""
        return self._config
    
    def get(self, section, key=None):
        """
        Get a configuration value
        
        Args:
            section (str): Configuration section
            key (str, optional): Configuration key
            
        Returns:
            The configuration value or section dictionary
        """
        if section not in self._config:
            return None
        
        if key is None:
            return self._config[section]
        
        return self._config[section].get(key)
    
    def set(self, section, key, value):
        """
        Set a configuration value
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            value: Value to set
            
        Returns:
            bool: Success status
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
        self._save_config()
        return True
    
    def update_section(self, section, values):
        """
        Update an entire configuration section
        
        Args:
            section (str): Configuration section
            values (dict): Dictionary of values
            
        Returns:
            bool: Success status
        """
        if not isinstance(values, dict):
            return False
        
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section].update(values)
        self._save_config()
        return True
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = DEFAULT_CONFIG.copy()
        self._save_config()
        logger.info("Configuration reset to defaults")
        return True

class AppSettings:
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def get_database_path(self):
        """Get the database path setting"""
        return self.config_manager.get("database", "path")
    
    def get_api_settings(self):
        """Get API settings"""
        return self.config_manager.get("api")
    
    def get_logging_level(self):
        """Get logging level"""
        level_str = self.config_manager.get("logging", "level")
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(level_str, logging.INFO)
    
    def should_backup_database(self):
        """
        Check if database backup should be performed
        
        Returns:
            bool: True if backup should be performed
        """
        # Get backup settings
        backup_enabled = self.config_manager.get("database", "backup_enabled")
        if not backup_enabled:
            return False
        
        backup_interval = self.config_manager.get("database", "backup_interval")
        last_backup = self.config_manager.get("database", "last_backup")
        
        # If never backed up, do it
        if last_backup is None:
            return True
        
        # Check if interval has elapsed
        try:
            last_backup_time = datetime.fromisoformat(last_backup)
            elapsed = (datetime.now() - last_backup_time).total_seconds()
            return elapsed >= backup_interval
        except Exception as e:
            logger.error(f"Error checking backup time: {e}")
            return True
    
    def update_last_backup_time(self):
        """Update the last backup timestamp"""
        now = datetime.now().isoformat()
        self.config_manager.set("database", "last_backup", now)
        return True
    
if __name__ == "main":
    app_settings = AppSettings()