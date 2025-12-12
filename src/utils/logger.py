"""
Logging configuration and utilities
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from src.config.settings import settings


def setup_logger(log_file: Optional[str] = None) -> None:
    """
    Setup application logging with file and console handlers
    
    Args:
        log_file: Path to log file (defaults to settings.LOG_FILE)
    """
    log_file = log_file or settings.LOG_FILE
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Set uvicorn logger level
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

