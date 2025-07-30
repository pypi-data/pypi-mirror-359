# Copyright 2024 JosueARz
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional

CACHE_DIR = Path(".prompt_cache")
CACHE_DIR.mkdir(exist_ok=True)


def hash_schema(schema: Dict[str, str]) -> str:
    """
    Generates a deterministic MD5 hash based on the given schema dictionary.

    Args:
        schema (Dict[str, str]): Dictionary mapping column names to descriptions.

    Returns:
        str: MD5 hash string representing the schema.
    """
    schema_str = json.dumps(schema, sort_keys=True)
    return hashlib.md5(schema_str.encode()).hexdigest()


def load_cached_prompt(hash_value: str) -> Optional[str]:
    """
    Loads a previously cached prompt from disk if available.

    Args:
        hash_value (str): Hash representing the schema used for lookup.

    Returns:
        Optional[str]: Cached prompt content, or None if not found.
    """
    cache_file = CACHE_DIR / f"{hash_value}.txt"
    return cache_file.read_text() if cache_file.exists() else None


def save_cached_prompt(hash_value: str, prompt: str) -> None:
    """
    Stores a generated prompt in the cache directory using its hash.

    Args:
        hash_value (str): Hash representing the schema.
        prompt (str): System prompt content to be saved.
    """
    cache_file = CACHE_DIR / f"{hash_value}.txt"
    cache_file.write_text(prompt)
