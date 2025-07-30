from typing import Optional
from dataclasses import dataclass

@dataclass
class BaseIndicator:
    """
    Base class for all project indicators.
    """
    name: str
    description: str
    weight: float  # Weight for scoring (0.0 - 1.0)
    is_library: Optional[bool] = None

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the indicator is present in the given repository.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        raise NotImplementedError 