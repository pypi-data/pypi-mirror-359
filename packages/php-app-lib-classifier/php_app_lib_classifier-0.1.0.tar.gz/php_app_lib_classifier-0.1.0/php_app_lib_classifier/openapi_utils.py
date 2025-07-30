import os
import json
import yaml
import re
from typing import List, Optional, AsyncGenerator
from .utils import enumerate_files, enumerate_php_files
import asyncio

async def find_and_validate_swagger_files(repo_path: str) -> List[str]:
    """
    Asynchronously find and validate Swagger/OpenAPI files in the repository.

    Args:
        repo_path (str): Path to the repository.

    Returns:
        List[str]: List of relative paths to valid Swagger/OpenAPI files.
    """
    swagger_files = []
    async for file_path in enumerate_files(repo_path, extensions=(".yaml", ".yml", ".json")):
        file_name = os.path.basename(file_path)
        if re.search(r".*(swagger|api).*\.(yaml|yml|json)$", file_name, re.IGNORECASE):
            if await validate_swagger_file(file_path):
                relative_path = os.path.relpath(file_path, repo_path)
                swagger_files.append(relative_path)
    return swagger_files

async def validate_swagger_file(file_path: str) -> bool:
    """
    Asynchronously validate if a file conforms to Swagger/OpenAPI specification.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if valid Swagger/OpenAPI file, else False.
    """
    try:
        async with await asyncio.to_thread(open, file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "swagger" not in content.lower() and "openapi" not in content.lower():
            return False
        if file_path.endswith((".yaml", ".yml")):
            spec = yaml.safe_load(content)
        elif file_path.endswith(".json"):
            spec = json.loads(content)
        else:
            return False
        return ("swagger" in spec or "openapi" in spec) and "paths" in spec
    except Exception as e:
        # Log error if needed
        return False

async def is_swagger_php_file(path: str) -> bool:
    """
    Asynchronously check if a PHP file contains Swagger/OpenAPI annotations.

    Args:
        path (str): Path to the PHP file.

    Returns:
        bool: True if Swagger/OpenAPI annotations found, else False.
    """
    if not os.path.isfile(path):
        return False
    try:
        async with await asyncio.to_thread(open, path, "rb") as php_file:
            content = php_file.read()
        return b"#[OA\\" in content or b"@OA\\" in content or b"OpenApi" in content
    except Exception:
        return False

async def check_repository_swagger_usage(repository_path: str) -> bool:
    """
    Asynchronously check if any PHP file in the repository uses Swagger/OpenAPI annotations.

    Args:
        repository_path (str): Path to the repository.

    Returns:
        bool: True if Swagger/OpenAPI usage is detected, else False.
    """
    async for php_file_path in enumerate_php_files(repository_path):
        if await is_swagger_php_file(php_file_path):
            return True
    return False

async def is_apiblueprint_file(path: str) -> bool:
    """
    Asynchronously check if a PHP file contains API Blueprint annotations.

    Args:
        path (str): Path to the PHP file.

    Returns:
        bool: True if API Blueprint annotations found, else False.
    """
    if not os.path.isfile(path):
        return False
    try:
        async with await asyncio.to_thread(open, path, "rb") as php_file:
            content = php_file.read()
        return b"@Parameters(" in content
    except Exception:
        return False

async def check_repository_apiblueprint_usage(repository_path: str) -> bool:
    """
    Asynchronously check if any PHP file in the repository uses API Blueprint annotations.

    Args:
        repository_path (str): Path to the repository.

    Returns:
        bool: True if API Blueprint usage is detected, else False.
    """
    async for php_file_path in enumerate_php_files(repository_path):
        if await is_apiblueprint_file(php_file_path):
            return True
    return False 