from enum import Enum

class ProjectType(Enum):
    """Enum for project classification types."""
    LIBRARY = "Library"
    WEB_APPLICATION = "Web Application"
    HYBRID_UNCLEAR = "Hybrid/Unclear"

class ConfidenceLevel(Enum):
    """Enum for confidence levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ConfidenceColor(Enum):
    """Enum for confidence level colors."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red" 