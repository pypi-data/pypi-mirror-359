"""
Configuration file loader.

This module handles loading and parsing of Python configuration files
with 'data = {...}' format and basic file validation.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, Any, Set, List


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass


class ConfigLoader:
    """Loads and parses configuration files with format validation."""
    
    # Valid configuration file extensions
    ALLOWED_EXTENSIONS = {'.py', '.env'}
    FORBIDDEN_EXTENSIONS = {'.ini', '.yaml', '.yml', '.json', '.toml'}
    
    def __init__(self, config_root: Path = None):
        """Initialize configuration loader."""
        self.config_root = config_root or Path("config")
        self.config_root.mkdir(exist_ok=True, parents=True)
        logger.debug(f"ConfigLoader initialized with root: {self.config_root}")
    
    def validate_file_format(self, file_path: Path) -> None:
        """Validate that file format is allowed."""
        extension = file_path.suffix.lower()
        
        if extension in self.FORBIDDEN_EXTENSIONS:
            raise ConfigurationError(
                f"Configuration file format '{extension}' is not allowed. "
                f"Only .py and .env files are supported. "
                f"File: {file_path}"
            )
        
        if extension not in self.ALLOWED_EXTENSIONS:
            raise ConfigurationError(
                f"Unknown configuration file format '{extension}'. "
                f"Only .py and .env files are supported. "
                f"File: {file_path}"
            )
    
    def load_python_config(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from Python file with 'data = {...}' format."""
        self.validate_file_format(file_path)
        
        if not file_path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to extract 'data' variable
            tree = ast.parse(content, filename=str(file_path))
            
            data_value = None
            for node in ast.walk(tree):
                if (isinstance(node, ast.Assign) and 
                    len(node.targets) == 1 and
                    isinstance(node.targets[0], ast.Name) and
                    node.targets[0].id == 'data'):
                    
                    # Evaluate the data assignment
                    data_value = ast.literal_eval(node.value)
                    break
            
            if data_value is None:
                raise ConfigurationError(
                    f"Configuration file must contain a 'data = {{...}}' variable. "
                    f"File: {file_path}"
                )
            
            if not isinstance(data_value, dict):
                raise ConfigurationError(
                    f"Configuration 'data' must be a dictionary. "
                    f"File: {file_path}"
                )
            
            logger.debug(f"Loaded Python config: {file_path}")
            return data_value
            
        except SyntaxError as e:
            raise ConfigurationError(
                f"Syntax error in configuration file {file_path}: {e}"
            )
        except ValueError as e:
            raise ConfigurationError(
                f"Invalid data in configuration file {file_path}: {e}"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration file {file_path}: {e}"
            )
    
    def load_config_file(self, file_path: str) -> Dict[str, Any]:
        """Load configuration file with format validation (backward compatibility)."""
        path_obj = Path(file_path)
        self.validate_file_format(path_obj)
        return self.load_python_config(path_obj)
    
    def check_forbidden_formats(self) -> List[str]:
        """Check for forbidden file formats in config directory."""
        errors = []
        
        for forbidden_ext in self.FORBIDDEN_EXTENSIONS:
            forbidden_files = list(self.config_root.rglob(f"*{forbidden_ext}"))
            for file_path in forbidden_files:
                errors.append(
                    f"Forbidden configuration format '{forbidden_ext}': {file_path}"
                )
        
        return errors
    
    def list_config_files(self, subdirectory: str = None) -> List[Path]:
        """List all Python configuration files in a directory."""
        search_dir = self.config_root / subdirectory if subdirectory else self.config_root
        
        if not search_dir.exists():
            return []
        
        config_files = []
        for file_path in search_dir.glob("*.py"):
            if file_path.name != "__init__.py":
                config_files.append(file_path)
        
        return sorted(config_files)
    
    def get_config_path(self, subdirectory: str, filename: str) -> Path:
        """Get full path to a configuration file."""
        if not filename.endswith('.py'):
            filename += '.py'
        
        return self.config_root / subdirectory / filename
    
    def config_exists(self, subdirectory: str, filename: str) -> bool:
        """Check if a configuration file exists."""
        return self.get_config_path(subdirectory, filename).exists()
    
    def get_config_stats(self) -> Dict[str, Any]:
        """Get statistics about configuration files."""
        stats = {
            "total_files": 0,
            "by_directory": {},
            "forbidden_files": len(self.check_forbidden_formats()),
            "directories": []
        }
        
        # Standard config directories
        directories = [
            "monitoring_groups",
            "user_groups", 
            "reporting_groups",
            # "schedules",  # Removed in v2.2
            "result_display_templates"
        ]
        
        for directory in directories:
            dir_path = self.config_root / directory
            if dir_path.exists():
                files = self.list_config_files(directory)
                stats["by_directory"][directory] = len(files)
                stats["total_files"] += len(files)
                stats["directories"].append(directory)
        
        return stats 