from .base import BaseIndicator
from typing import Optional
import pathlib

class HasFrontendAssetsIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="has_frontend_assets",
            description="Has directories for frontend assets",
            weight=0.7,
            is_library=False
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the repository has directories for frontend assets.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        asset_dirs = ["public/js", "public/css", "assets", "web/assets", "resources/js", "resources/css"]
        return any((pathlib.Path(repo_path) / dir_path).exists() for dir_path in asset_dirs) 