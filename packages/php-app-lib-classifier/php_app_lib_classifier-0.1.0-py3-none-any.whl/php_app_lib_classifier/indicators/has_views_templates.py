from .base import BaseIndicator
from typing import Optional
import pathlib

class HasViewsTemplatesIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="has_views_templates",
            description="Has view/template directories",
            weight=0.7,
            is_library=False
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the repository has view/template directories.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        view_dirs = ["views", "templates", "resources/views", "src/View", "src/Template"]
        return any((pathlib.Path(repo_path) / dir_path).exists() for dir_path in view_dirs) 