from .base import BaseIndicator
from typing import Optional

class ComposerTypeProjectIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="composer_type_project",
            description="composer.json has 'type' field set to 'project'",
            weight=0.8,
            is_library=False
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if composer.json has 'type' field set to 'project'.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        if composer_data:
            return composer_data.get("type") == "project"
        return False 