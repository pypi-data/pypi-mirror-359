from .base import BaseIndicator
from typing import Optional

class ComposerTypeLibraryIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="composer_type_library",
            description="composer.json has 'type' field set to 'library'",
            weight=0.8,
            is_library=True
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if composer.json has 'type' field set to 'library'.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        if composer_data:
            return composer_data.get("type") == "library"
        return False 