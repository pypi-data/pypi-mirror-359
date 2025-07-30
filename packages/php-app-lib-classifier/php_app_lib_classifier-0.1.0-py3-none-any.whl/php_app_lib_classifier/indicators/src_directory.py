from .base import BaseIndicator
from typing import Optional
import pathlib

class SrcDirectoryIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="src_directory",
            description="Has a src/ directory for source code",
            weight=0.5,
            is_library=True
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if the repository has a src/ directory for source code.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        return (pathlib.Path(repo_path) / "src").exists() 