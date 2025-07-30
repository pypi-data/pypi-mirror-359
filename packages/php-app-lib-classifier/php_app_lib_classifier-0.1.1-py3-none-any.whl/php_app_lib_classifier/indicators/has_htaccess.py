from .base import BaseIndicator
from typing import Optional
import pathlib

class HasHtaccessIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="has_htaccess",
            description="Has .htaccess file",
            weight=0.5,
            is_library=False
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the repository has a .htaccess file.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        return any(path.name == ".htaccess" for path in pathlib.Path(repo_path).glob("**/.htaccess")) 