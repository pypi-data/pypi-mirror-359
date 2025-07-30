from .base import BaseIndicator
from typing import Optional

class HasPSR4AutoloadIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="has_psr4_autoload",
            description="composer.json defines PSR-4 autoload",
            weight=0.6,
            is_library=True
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if composer.json defines PSR-4 autoload.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        if composer_data:
            autoload = composer_data.get("autoload", {})
            return "psr-4" in autoload
        return False 