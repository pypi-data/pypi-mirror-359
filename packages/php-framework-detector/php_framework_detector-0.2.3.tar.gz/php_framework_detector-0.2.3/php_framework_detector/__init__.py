"""
PHP Framework Detector

A modern Python tool for detecting PHP frameworks in project directories.
Provides async-aware detection with comprehensive framework support.
"""

from .core import (
    FrameworkDetector,
    FrameworkDetectorFactory,
    DetectionConfig,
    DetectionResult,
    FrameworkInfo,
    FrameworkMetadata
)
from .core.exceptions import (
    FrameworkDetectorError,
    InvalidPathError,
    DetectionError,
    ConfigurationError,
    FileReadError,
    TimeoutError,
    UnsupportedFrameworkError
)

# Legacy API for backward compatibility
def detect_framework(path: str) -> str:
    """
    Detect the framework used in a PHP project.
    
    Args:
        path: Path to the repository
        
    Returns:
        Framework name or "na" if no framework is detected
    """
    from .core.factory import FrameworkDetectorFactory
    
    try:
        # Get all detector instances
        detectors = FrameworkDetectorFactory.get_all_detectors(path)
        
        # Try each detector
        for detector in detectors:
            if detector.detect():
                return detector.name
        
        return "na"
    except Exception:
        return "na"


def get_framework_names() -> dict:
    """
    Get mapping of framework codes to display names.
    
    Returns:
        Dictionary mapping framework codes to display names
    """
    from .core.factory import FrameworkDetectorFactory
    return FrameworkDetectorFactory.get_framework_names()


def get_available_frameworks() -> list:
    """
    Get list of available framework names.
    
    Returns:
        List of available framework codes
    """
    from .core.factory import FrameworkDetectorFactory
    return FrameworkDetectorFactory.get_available_frameworks()


__version__ = "0.2.0"
__all__ = [
    # Core classes
    "FrameworkDetector",
    "FrameworkDetectorFactory",
    
    # Models
    "DetectionConfig",
    "DetectionResult",
    "FrameworkInfo", 
    "FrameworkMetadata",
    
    # Exceptions
    "FrameworkDetectorError",
    "InvalidPathError",
    "DetectionError",
    "ConfigurationError",
    "FileReadError",
    "TimeoutError",
    "UnsupportedFrameworkError",
    
    # Legacy API
    "detect_framework",
    "get_framework_names",
    "get_available_frameworks",
] 