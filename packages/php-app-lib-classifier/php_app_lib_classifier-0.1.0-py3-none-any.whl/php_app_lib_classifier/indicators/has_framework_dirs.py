from .base import BaseIndicator
from typing import Optional
import pathlib

class HasFrameworkDirsIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="has_framework_dirs",
            description="Has framework-specific directories",
            weight=0.8,
            is_library=False
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the repository has framework-specific directories.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        framework_dirs = ["app", "config", "routes", "resources/views", "templates", "migrations"]
        return any((pathlib.Path(repo_path) / dir_path).exists() for dir_path in framework_dirs) 