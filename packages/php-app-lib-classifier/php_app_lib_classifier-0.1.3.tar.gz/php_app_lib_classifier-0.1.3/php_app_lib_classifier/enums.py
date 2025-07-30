from enum import Enum

class ProjectType(Enum):
    """Enum for project classification types."""
    LIBRARY = "library"
    APPLICATION = "application"
    HYBRID = "hybrid"

class ConfidenceLevel(Enum):
    """Enum for confidence levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ConfidenceColor(Enum):
    """Enum for confidence level colors."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red" 