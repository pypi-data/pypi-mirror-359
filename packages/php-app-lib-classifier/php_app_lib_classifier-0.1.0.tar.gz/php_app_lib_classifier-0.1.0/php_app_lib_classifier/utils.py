import os
from typing import AsyncGenerator, List
import pathlib

async def enumerate_files(directory: str, extensions: tuple[str, ...] = ('.php',)) -> AsyncGenerator[str, None]:
    """
    Asynchronously enumerate files in a directory with given extensions.

    Args:
        directory (str): The root directory to search.
        extensions (tuple[str, ...]): File extensions to include.

    Yields:
        str: The path to each matching file.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                yield os.path.join(root, file)

async def enumerate_php_files(directory: str) -> AsyncGenerator[str, None]:
    """
    Asynchronously enumerate all PHP files in a directory.

    Args:
        directory (str): The root directory to search.

    Yields:
        str: The path to each PHP file.
    """
    async for file_path in enumerate_files(directory, extensions=(".php",)):
        yield file_path

def enumerate_php_files(repo_path: str) -> List[str]:
    """
    Recursively enumerate all PHP files in the given repository path.

    Args:
        repo_path (str): Path to the repository.

    Returns:
        List[str]: List of PHP file paths (as strings).
    """
    repo = pathlib.Path(repo_path)
    return [str(p) for p in repo.rglob('*.php')] 