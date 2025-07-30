"""
Data models for PHP Framework Detector.

This module defines Pydantic models for type safety, data validation,
and structured data handling throughout the application.
"""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field, validator


class FrameworkInfo(BaseModel):
    """
    Information about a PHP framework.
    
    Attributes:
        code: Unique identifier for the framework
        name: Human-readable name of the framework
        description: Brief description of the framework
        version: Detected version (if available)
        confidence: Detection confidence score (0-100)
    """
    code: str = Field(..., description="Unique framework identifier")
    name: str = Field(..., description="Human-readable framework name")
    description: Optional[str] = Field(None, description="Framework description")
    version: Optional[str] = Field(None, description="Detected framework version")
    confidence: int = Field(100, ge=0, le=100, description="Detection confidence score")
    
    @validator('confidence')
    def validate_confidence(cls, v: int) -> int:
        """Ensure confidence is within valid range."""
        if not 0 <= v <= 100:
            raise ValueError('Confidence must be between 0 and 100')
        return v


class DetectionResult(BaseModel):
    """
    Result of framework detection analysis.
    
    Attributes:
        detected_framework: Code of the detected framework (or "na" if none)
        detected_name: Human-readable name of detected framework
        scores: Dictionary mapping framework codes to detection scores
        project_path: Path to the analyzed project
        detection_time: Timestamp of when detection was performed
        total_frameworks: Total number of frameworks checked
    """
    detected_framework: str = Field(..., description="Code of detected framework")
    detected_name: str = Field(..., description="Name of detected framework")
    scores: Dict[str, int] = Field(..., description="Detection scores for all frameworks")
    project_path: str = Field(..., description="Path to analyzed project")
    detection_time: datetime = Field(default_factory=datetime.now, description="Detection timestamp")
    total_frameworks: Optional[int] = Field(None, description="Total frameworks checked")
    
    @validator('detected_framework')
    def validate_detected_framework(cls, v: str) -> str:
        """Ensure detected framework is valid."""
        if not v or v.strip() == "":
            return "na"
        return v.lower().strip()
    
    @property
    def is_framework_detected(self) -> bool:
        """Check if a framework was detected."""
        return self.detected_framework != "na"
    
    @property
    def confidence_score(self) -> int:
        """Get confidence score for detected framework."""
        return self.scores.get(self.detected_framework, 0)
    
    @property
    def top_frameworks(self, limit: int = 5) -> Dict[str, int]:
        """Get top N frameworks by score."""
        sorted_scores = sorted(
            self.scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return dict(sorted_scores[:limit])


class DetectionConfig(BaseModel):
    """
    Configuration for framework detection.
    
    Attributes:
        check_composer: Whether to check composer files
        check_files: Whether to check file patterns
        check_dependencies: Whether to check dependencies
        max_file_size: Maximum file size to read (in bytes)
        timeout: Detection timeout in seconds
        verbose: Enable verbose logging
    """
    check_composer: bool = Field(True, description="Check composer files")
    check_files: bool = Field(True, description="Check file patterns")
    check_dependencies: bool = Field(True, description="Check dependencies")
    max_file_size: int = Field(1024 * 1024, ge=1024, description="Max file size to read")
    timeout: int = Field(30, ge=1, le=300, description="Detection timeout in seconds")
    verbose: bool = Field(False, description="Enable verbose logging")
    
    @validator('max_file_size')
    def validate_max_file_size(cls, v: int) -> int:
        """Ensure max file size is reasonable."""
        if v < 1024:
            raise ValueError('Max file size must be at least 1KB')
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError('Max file size cannot exceed 100MB')
        return v


class FrameworkMetadata(BaseModel):
    """
    Metadata about framework detection capabilities.
    
    Attributes:
        framework_code: Unique framework identifier
        detection_methods: List of detection methods used
        file_patterns: File patterns to check
        composer_packages: Composer package names to check
        content_patterns: Content patterns to search for
    """
    framework_code: str = Field(..., description="Framework identifier")
    detection_methods: list[str] = Field(default_factory=list, description="Detection methods")
    file_patterns: list[str] = Field(default_factory=list, description="File patterns to check")
    composer_packages: list[str] = Field(default_factory=list, description="Composer packages")
    content_patterns: list[str] = Field(default_factory=list, description="Content patterns") 