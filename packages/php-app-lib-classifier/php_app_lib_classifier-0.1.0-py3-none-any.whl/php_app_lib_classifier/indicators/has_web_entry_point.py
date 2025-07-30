from .base import BaseIndicator
from typing import Optional
import pathlib

class HasWebEntryPointIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="has_web_entry_point",
            description="Has web entry points (index.php, etc.)",
            weight=0.8,
            is_library=False
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the repository has web entry points (index.php, etc.).

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        entry_points = [
            "index.php", "public/index.php", "web/index.php", "www/index.php", "htdocs/index.php"
        ]
        return any((pathlib.Path(repo_path) / entry_point).exists() for entry_point in entry_points) 