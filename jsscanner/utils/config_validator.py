"""
Configuration Validator
Validates scanner configuration for common issues
"""
from typing import Dict, List, Tuple


class ConfigValidator:
    """Validates scanner configuration"""
    
    @staticmethod
    def validate_noise_filter(config: dict) -> Tuple[bool, List[str]]:
        """
        Validate noise filter configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        nf = config.get('noise_filter', {})
        
        # Validate min_file_size_kb
        min_kb = nf.get('min_file_size_kb', 50)
        if not isinstance(min_kb, (int, float)):
            errors.append(f"noise_filter.min_file_size_kb must be a number, got {type(min_kb).__name__}")
        elif not 1 <= min_kb <= 10000:
            errors.append(f"noise_filter.min_file_size_kb must be 1-10000, got {min_kb}")
        
        # Validate max_newlines
        max_lines = nf.get('max_newlines', 20)
        if not isinstance(max_lines, int):
            errors.append(f"noise_filter.max_newlines must be an integer, got {type(max_lines).__name__}")
        elif not 1 <= max_lines <= 1000:
            errors.append(f"noise_filter.max_newlines must be 1-1000, got {max_lines}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_bloom_filter(config: dict) -> Tuple[bool, List[str]]:
        """
        Validate Bloom filter configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        bf = config.get('bloom_filter', {})
        
        # Validate capacity
        capacity = bf.get('capacity', 100000)
        if not isinstance(capacity, int):
            errors.append(f"bloom_filter.capacity must be an integer, got {type(capacity).__name__}")
        elif capacity < 1000:
            errors.append(f"bloom_filter.capacity must be at least 1000, got {capacity}")
        
        # Validate error_rate
        error_rate = bf.get('error_rate', 0.001)
        if not isinstance(error_rate, (int, float)):
            errors.append(f"bloom_filter.error_rate must be a number, got {type(error_rate).__name__}")
        elif not 0.0001 <= error_rate <= 0.1:
            errors.append(f"bloom_filter.error_rate must be 0.0001-0.1, got {error_rate}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_secrets(config: dict) -> Tuple[bool, List[str]]:
        """
        Validate secrets configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        secrets = config.get('secrets', {})
        
        # Validate buffer_size
        buffer_size = secrets.get('buffer_size', 10)
        if not isinstance(buffer_size, int):
            errors.append(f"secrets.buffer_size must be an integer, got {type(buffer_size).__name__}")
        elif not 1 <= buffer_size <= 1000:
            errors.append(f"secrets.buffer_size must be 1-1000, got {buffer_size}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_all(cls, config: dict) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate all configuration sections
        
        Args:
            config: Configuration dictionary
            
        Returns:
            (is_valid, dict_of_errors_by_section)
        """
        all_errors = {}
        
        # Validate each section
        sections = [
            ('noise_filter', cls.validate_noise_filter),
            ('bloom_filter', cls.validate_bloom_filter),
            ('secrets', cls.validate_secrets)
        ]
        
        for section_name, validator in sections:
            is_valid, errors = validator(config)
            if not is_valid:
                all_errors[section_name] = errors
        
        return len(all_errors) == 0, all_errors
    
    @staticmethod
    def format_errors(errors: Dict[str, List[str]]) -> str:
        """
        Format validation errors for display
        
        Args:
            errors: Dictionary of errors by section
            
        Returns:
            Formatted error string
        """
        if not errors:
            return "✅ Configuration is valid"
        
        lines = ["❌ Configuration validation failed:"]
        for section, section_errors in errors.items():
            lines.append(f"\n[{section}]")
            for error in section_errors:
                lines.append(f"  - {error}")
        
        return "\n".join(lines)


def validate_config_file(config_path: str):
    """
    Validate configuration file
    
    Args:
        config_path: Path to config.yaml file
    """
    import yaml
    from pathlib import Path
    
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    is_valid, errors = ConfigValidator.validate_all(config)
    print(ConfigValidator.format_errors(errors))
    
    return is_valid


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python config_validator.py <path-to-config.yaml>")
        sys.exit(1)
    
    is_valid = validate_config_file(sys.argv[1])
    sys.exit(0 if is_valid else 1)
