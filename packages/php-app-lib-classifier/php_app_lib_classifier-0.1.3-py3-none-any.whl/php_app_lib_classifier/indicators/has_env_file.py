from .base import BaseIndicator
from typing import Optional
import pathlib

class HasEnvFileIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="has_env_file",
            description="Has .env or .env.example file",
            weight=0.6,
            is_library=False
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the repository has .env or .env.example file.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        repo = pathlib.Path(repo_path)
        return (repo / ".env").exists() or (repo / ".env.example").exists() 