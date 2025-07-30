from .base import BaseIndicator
from typing import Optional

class HasWebFrameworkIndicator(BaseIndicator):
    def __init__(self):
        super().__init__(
            name="has_web_framework",
            description="Depends on a major web framework",
            weight=0.7,
            is_library=False
        )

    async def check(self, repo_path: str, composer_data: Optional[dict], readme_content: Optional[str]) -> bool:
        """
        Check if composer.json depends on a major web framework.

        Args:
            repo_path (str): Path to the repository.
            composer_data (Optional[dict]): Parsed composer.json data.
            readme_content (Optional[str]): Content of the README file.

        Returns:
            bool: True if the indicator is found, False otherwise.
        """
        if composer_data:
            web_frameworks = ["laravel", "symfony", "slim", "yii", "cakephp", "zend", "laminas", "codeigniter"]
            require = composer_data.get("require", {})
            return any(framework in pkg.lower() for pkg in require for framework in web_frameworks)
        return False 