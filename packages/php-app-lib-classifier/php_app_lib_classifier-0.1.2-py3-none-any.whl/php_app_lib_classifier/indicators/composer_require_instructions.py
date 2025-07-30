from .base import BaseIndicator
from typing import Optional

class ComposerRequireInstructionsIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="composer_require_instructions",
            description="README has composer require instructions",
            weight=0.7,
            is_library=True
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if README has composer require instructions.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        if readme_content:
            return "composer require" in readme_content.lower()
        return False 