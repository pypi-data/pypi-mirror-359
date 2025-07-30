from .base import BaseIndicator
from typing import Optional

class LibraryReadmeIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="library_readme",
            description="README mentions it's a library/package",
            weight=0.5,
            is_library=True
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if README mentions it's a library/package.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        if readme_content:
            library_terms = ["library", "package", "component", "module", "dependency"]
            return any(term in readme_content.lower() for term in library_terms)
        return False 