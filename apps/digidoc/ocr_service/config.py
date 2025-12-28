"""
DigiDoc Configuration Loader

Loads configuration from digidoc_config.yaml with support for:
- Variable substitution ({storage_base} → expanded path)
- Environment variable overrides (DIGIDOC_<SECTION>_<KEY>)
- Typed access via dot notation
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigSection:
    """Wrapper for config sections to enable dot notation access."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
    
    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return super().__getattribute__(name)
        
        value = self._data.get(name)
        
        # If value is a dict, wrap it in ConfigSection for nested access
        if isinstance(value, dict):
            return ConfigSection(value)
        
        return value
    
    def __getitem__(self, key: str) -> Any:
        return self._data[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class Config:
    """Main configuration class with dot notation access."""
    
    def __init__(self, config_data: Dict[str, Any]):
        self._data = config_data
        
        # Create section attributes for dot notation
        for section_name, section_data in config_data.items():
            setattr(self, section_name, ConfigSection(section_data))
    
    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return super().__getattribute__(name)
        return getattr(self, name)


def _expand_path(path: str) -> str:
    """Expand ~ and environment variables in path."""
    return os.path.expanduser(os.path.expandvars(path))


def _substitute_variables(value: Any, substitutions: Dict[str, str]) -> Any:
    """Recursively substitute variables in config values."""
    if isinstance(value, str):
        # Replace all {variable} patterns
        result = value
        for var_name, var_value in substitutions.items():
            result = result.replace(f"{{{var_name}}}", var_value)
        return result
    elif isinstance(value, dict):
        return {k: _substitute_variables(v, substitutions) for k, v in value.items()}
    elif isinstance(value, list):
        return [_substitute_variables(item, substitutions) for item in value]
    else:
        return value


def _find_config_file() -> Path:
    """Find the config file location.
    
    Priority:
    1. DIGIDOC_CONFIG_PATH environment variable
    2. DigiDoc root directory (parent of ocr_service/)
    """
    # Check environment variable first
    env_path = os.getenv('DIGIDOC_CONFIG_PATH')
    if env_path:
        return Path(env_path).expanduser().resolve()
    
    # Default: DigiDoc root (one level up from ocr_service/)
    # This file is in ocr_service/config.py, so parent.parent is DigiDoc root
    current_file = Path(__file__).resolve()
    digidoc_root = current_file.parent.parent
    config_file = digidoc_root / 'digidoc_config.yaml'
    
    return config_file


def _load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Set DIGIDOC_CONFIG_PATH environment variable to specify custom location."
        )
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    if config_data is None:
        raise ValueError(f"Config file is empty: {config_path}")
    
    return config_data


def _convert_type(value: str, original_value: Any) -> Any:
    """Convert string environment variable to appropriate type.
    
    Attempts to match the type of the original config value.
    """
    # If original value exists, try to match its type
    if original_value is not None:
        if isinstance(original_value, bool):
            # Handle boolean strings
            value_lower = value.lower()
            if value_lower in ('true', '1', 'yes', 'on'):
                return True
            elif value_lower in ('false', '0', 'no', 'off'):
                return False
        elif isinstance(original_value, int):
            # Try to convert to int
            try:
                return int(value)
            except ValueError:
                pass
        elif isinstance(original_value, float):
            # Try to convert to float
            try:
                return float(value)
            except ValueError:
                pass
    
    # Fallback: try to infer type from string value
    value_lower = value.lower()
    
    # Boolean
    if value_lower in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
        return value_lower in ('true', '1', 'yes', 'on')
    
    # Integer
    try:
        if '.' not in value:
            return int(value)
    except ValueError:
        pass
    
    # Float
    try:
        return float(value)
    except ValueError:
        pass
    
    # String (default)
    return value


def _collect_env_overrides() -> Dict[str, Any]:
    """Collect environment variable overrides.
    
    Pattern: DIGIDOC_<SECTION>_<KEY>
    Example: DIGIDOC_PREPROCESSING_TARGET_DPI → preprocessing.target_dpi
    
    Returns:
        Dict with nested structure matching config sections
    """
    overrides = {}
    prefix = 'DIGIDOC_'
    
    for env_key, env_value in os.environ.items():
        if not env_key.startswith(prefix):
            continue
        
        # Skip DIGIDOC_CONFIG_PATH (handled separately)
        if env_key == 'DIGIDOC_CONFIG_PATH':
            continue
        
        # Remove prefix and split into parts
        key_parts = env_key[len(prefix):].lower().split('_')
        
        if len(key_parts) < 2:
            # Need at least section and key
            continue
        
        # First part is section, rest is key (may have underscores)
        section = key_parts[0]
        key = '_'.join(key_parts[1:])
        
        # Create nested structure
        if section not in overrides:
            overrides[section] = {}
        
        overrides[section][key] = env_value
    
    return overrides


def _apply_env_overrides(config_data: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config data.
    
    Args:
        config_data: Original config data from YAML
        overrides: Environment variable overrides (nested dict structure)
    
    Returns:
        Config data with overrides applied
    """
    result = config_data.copy()
    
    for section, section_overrides in overrides.items():
        if section not in result:
            # Section doesn't exist in config, create it
            result[section] = {}
        
        for key, env_value in section_overrides.items():
            # Get original value for type conversion
            original_value = result[section].get(key) if isinstance(result[section], dict) else None
            
            # Convert type and apply override
            converted_value = _convert_type(env_value, original_value)
            
            if isinstance(result[section], dict):
                result[section][key] = converted_value
    
    return result


def _apply_variable_substitution(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply variable substitution to config data.
    
    Expands {storage_base} and other variables in paths section.
    """
    # First, expand storage_base path
    if 'paths' in config_data and 'storage_base' in config_data['paths']:
        storage_base = config_data['paths']['storage_base']
        expanded_storage_base = _expand_path(storage_base)
        
        # Create substitutions dictionary
        substitutions = {
            'storage_base': expanded_storage_base
        }
        
        # Apply substitutions recursively to entire config
        config_data = _substitute_variables(config_data, substitutions)
        
        # Update storage_base with expanded path
        config_data['paths']['storage_base'] = expanded_storage_base
    
    return config_data


# Global config instance (lazy-loaded)
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the configuration instance (singleton pattern).
    
    Returns:
        Config: Configuration object with dot notation access
        
    Example:
        >>> config = get_config()
        >>> print(config.preprocessing.target_dpi)
        300
        >>> print(config.paths.queue_directory)
        /Users/scottroberts/Dropbox/Application Data/DigiDoc/queue
    """
    global _config_instance
    
    if _config_instance is None:
        # Find and load config file
        config_path = _find_config_file()
        config_data = _load_yaml_config(config_path)
        
        # Apply environment variable overrides (before variable substitution)
        env_overrides = _collect_env_overrides()
        config_data = _apply_env_overrides(config_data, env_overrides)
        
        # Apply variable substitution
        config_data = _apply_variable_substitution(config_data)
        
        # Create Config instance
        _config_instance = Config(config_data)
    
    return _config_instance


def reload_config() -> Config:
    """Reload configuration from file (useful for testing or config changes)."""
    global _config_instance
    _config_instance = None
    return get_config()
