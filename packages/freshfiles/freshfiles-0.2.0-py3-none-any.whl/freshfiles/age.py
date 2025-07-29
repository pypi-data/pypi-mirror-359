import time
from pathlib import Path
from typing import List, Optional
import math


def _get_file_mtime(file_path: Path) -> float:
    if not file_path.is_file():
        raise FileNotFoundError(f"Not a regular file or does not exist: '{file_path}'")
    return file_path.stat().st_mtime


def _get_file_ages_in_seconds(filepaths: List[Path]) -> List[float]:
    current_time = time.time()
    return [current_time - _get_file_mtime(filepath) for filepath in filepaths]


def get_max_file_age_in_seconds(filepaths: List[Path]) -> Optional[int]:
    """
    Calculates the maximum age in seconds among a list of files.
    """
    all_ages = _get_file_ages_in_seconds(filepaths)
    return math.floor(max(all_ages)) if all_ages else None


def get_min_file_age_in_seconds(filepaths: List[Path]) -> Optional[int]:
    """
    Calculates the minimum age in seconds among a list of files.
    """
    all_ages = _get_file_ages_in_seconds(filepaths)
    return math.floor(min(all_ages)) if all_ages else None
