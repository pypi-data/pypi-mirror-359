import pathlib
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Type
from .openapi_utils import find_and_validate_swagger_files
from .utils import enumerate_php_files
import asyncio
from .indicators import (
    BaseIndicator,
    ComposerTypeLibraryIndicator,
    ComposerTypeProjectIndicator,
    HasPSR4AutoloadIndicator,
    SrcDirectoryIndicator,
    TestsDirectoryIndicator,
    LibraryReadmeIndicator,
    ComposerRequireInstructionsIndicator,
    HasWebEntryPointIndicator,
    HasHtaccessIndicator,
    HasFrontendAssetsIndicator,
    HasEnvFileIndicator,
    HasFrameworkDirsIndicator,
    HasViewsTemplatesIndicator,
    HasWebFrameworkIndicator,
    HasDockerConfigIndicator,
)

@dataclass
class AnalysisResult:
    """
    Results of the project analysis.
    """
    path: str
    library_score: float
    webapp_score: float
    indicators_found: List[BaseIndicator]

    @property
    def total_score(self) -> float:
        return self.library_score + self.webapp_score

    @property
    def normalized_library_score(self) -> float:
        return self.library_score / self.total_score if self.total_score > 0 else 0.5

    @property
    def normalized_webapp_score(self) -> float:
        return self.webapp_score / self.total_score if self.total_score > 0 else 0.5

    @property
    def project_type(self) -> str:
        lib_score = self.normalized_library_score
        if lib_score > 0.7:
            return "Library"
        elif lib_score < 0.3:
            return "Web Application"
        else:
            return "Hybrid/Unclear"

    def get_confidence_level(self) -> Tuple[str, str]:
        lib_score = self.normalized_library_score
        if abs(lib_score - 0.5) > 0.4:
            return "High", "green"
        elif abs(lib_score - 0.5) > 0.2:
            return "Medium", "yellow"
        else:
            return "Low", "red"

class PHPProjectAnalyzer:
    """
    Analyzes PHP projects to determine if they are libraries or web applications.
    """
    def __init__(self, repo_path: str, verbose: bool = False):
        self.repo_path = pathlib.Path(repo_path).resolve()
        self.verbose = verbose
        self.indicators: List[BaseIndicator] = self._define_indicators()
        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.repo_path}")
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

    def _define_indicators(self) -> List[BaseIndicator]:
        """
        Instantiate all indicator classes.
        """
        return [
            ComposerTypeLibraryIndicator(),
            HasPSR4AutoloadIndicator(),
            SrcDirectoryIndicator(),
            TestsDirectoryIndicator(),
            LibraryReadmeIndicator(),
            ComposerRequireInstructionsIndicator(),
            HasWebEntryPointIndicator(),
            HasHtaccessIndicator(),
            HasFrontendAssetsIndicator(),
            HasEnvFileIndicator(),
            HasFrameworkDirsIndicator(),
            HasViewsTemplatesIndicator(),
            ComposerTypeProjectIndicator(),
            HasWebFrameworkIndicator(),
            HasDockerConfigIndicator(),
        ]

    async def analyze(self) -> AnalysisResult:
        """
        Asynchronously analyze the repository and determine if it's a library or web application.

        Returns:
            AnalysisResult: The analysis results
        """
        library_score: float = 0.0
        webapp_score: float = 0.0
        indicators_found: List[BaseIndicator] = []
        composer_data = await self._load_composer_json()
        readme_content = await self._load_readme()
        # Run all indicator checks concurrently
        indicator_tasks = [
            indicator.check(str(self.repo_path), composer_data, readme_content)
            for indicator in self.indicators
        ]
        results = await asyncio.gather(*indicator_tasks)
        for indicator, found in zip(self.indicators, results):
            if found:
                indicators_found.append(indicator)
                if indicator.is_library is True:
                    library_score += indicator.weight
                elif indicator.is_library is False:
                    webapp_score += indicator.weight
        return AnalysisResult(
            path=str(self.repo_path),
            library_score=library_score,
            webapp_score=webapp_score,
            indicators_found=indicators_found
        )

    async def _load_composer_json(self) -> Optional[Dict]:
        composer_path = self.repo_path / "composer.json"
        if composer_path.exists():
            try:
                return await asyncio.to_thread(self._read_json, composer_path)
            except Exception:
                return None
        return None

    def _read_json(self, path) -> dict:
        import json
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def _load_readme(self) -> Optional[str]:
        readme_filenames = ["README.md", "README", "readme.md", "Readme.md", "README.txt"]
        for filename in readme_filenames:
            readme_path = self.repo_path / filename
            if readme_path.exists():
                try:
                    return await asyncio.to_thread(self._read_text, readme_path)
                except Exception:
                    continue
        return None

    def _read_text(self, path) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read() 