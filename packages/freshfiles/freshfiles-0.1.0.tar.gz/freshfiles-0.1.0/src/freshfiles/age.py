import os
import time
from pathlib import Path
from typing import List, Optional
import math
import logging


def get_max_file_age_in_seconds_pathlib(filepaths: List[Path]) -> Optional[int]:
    """
    Calculates the maximum age in seconds among a list of files using pathlib.

    Args:
        filepaths: A list of pathlib.Path objects.

    Returns:
        The maximum age in seconds as an integer (floored).
        Returns None if the list is empty or if no valid file paths are processed
        due to errors (e.g., file not found, permission denied for all files).
    """
    if not filepaths:
        return None

    current_time = time.time()
    max_age_float = 0.0
    found_valid_file = False

    for file_path in filepaths:
        try:
            if not file_path.is_file():
                logging.error(f"Not a regular file or does not exist: '{file_path}'")
                continue

            modification_time = file_path.stat().st_mtime
            age = current_time - modification_time

            if age > max_age_float:
                max_age_float = age

            found_valid_file = True

        except FileNotFoundError:
            logging.error(f"File not found: '{file_path}'")
        except PermissionError:
            logging.error(f"Permission denied to access file: '{file_path}'")
        except Exception as e:
            logging.error(f"An unexpected error occurred with file '{file_path}': {e}")

    if not found_valid_file:
        return None

    return math.floor(max_age_float)
