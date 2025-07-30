from .base import BaseIndicator
from typing import Optional
import pathlib

class TestsDirectoryIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="tests_directory",
            description="Has a tests/ directory",
            weight=0.4,
            is_library=True
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the repository has a tests/ or test/ directory.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        repo = pathlib.Path(repo_path)
        return (repo / "tests").exists() or (repo / "test").exists() 