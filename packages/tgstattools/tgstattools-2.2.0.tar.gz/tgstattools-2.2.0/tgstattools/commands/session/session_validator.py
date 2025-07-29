"""
Session validation utilities.

This module handles session file validation and information extraction.
Single Responsibility: Validating session files and extracting session metadata.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SessionValidator:
    """Handles session file validation and metadata extraction."""
    
    @staticmethod
    def validate_session_file(session_path: Path) -> Dict[str, Any]:
        """
        Validate session file and return validation results.
        
        Args:
            session_path: Path to session file
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": False,
            "exists": False,
            "readable": False,
            "size": 0,
            "error": None
        }
        
        try:
            if not session_path.exists():
                result["error"] = "Session file does not exist"
                return result
            
            result["exists"] = True
            
            if not session_path.is_file():
                result["error"] = "Session path is not a file"
                return result
            
            # Check if file is readable
            try:
                with open(session_path, 'rb') as f:
                    # Try to read first few bytes
                    data = f.read(16)
                    if len(data) == 0:
                        result["error"] = "Session file is empty"
                        return result
                
                result["readable"] = True
                result["size"] = session_path.stat().st_size
                
            except PermissionError:
                result["error"] = "Permission denied reading session file"
                return result
            except Exception as e:
                result["error"] = f"Error reading session file: {e}"
                return result
            
            # Basic validation - session files should be at least a few bytes
            if result["size"] < 10:
                result["error"] = "Session file appears to be corrupted (too small)"
                return result
            
            result["valid"] = True
            return result
            
        except Exception as e:
            logger.exception("Session validation error")
            result["error"] = f"Validation error: {e}"
            return result
    
    @staticmethod
    def get_session_info(session_name: str = "tgstattools_session", 
                        session_dir: str = "data/sessions") -> Dict[str, Any]:
        """
        Get session information and metadata.
        
        Args:
            session_name: Name of session
            session_dir: Directory containing sessions
            
        Returns:
            Dictionary with session information
        """
        session_path = Path(session_dir) / f"{session_name}.session"
        
        info = {
            "session_name": session_name,
            "session_dir": session_dir,
            "session_path": str(session_path),
            "validation": SessionValidator.validate_session_file(session_path)
        }
        
        if info["validation"]["valid"]:
            try:
                stat = session_path.stat()
                info.update({
                    "created_at": stat.st_ctime,
                    "modified_at": stat.st_mtime,
                    "size_bytes": stat.st_size
                })
            except Exception as e:
                logger.warning(f"Could not get session file stats: {e}")
        
        return info
    
    @staticmethod
    def is_session_valid(session_name: str = "tgstattools_session", 
                        session_dir: str = "data/sessions") -> bool:
        """
        Quick check if session is valid.
        
        Args:
            session_name: Name of session
            session_dir: Directory containing sessions
            
        Returns:
            True if session is valid, False otherwise
        """
        session_path = Path(session_dir) / f"{session_name}.session"
        validation = SessionValidator.validate_session_file(session_path)
        return validation["valid"] 