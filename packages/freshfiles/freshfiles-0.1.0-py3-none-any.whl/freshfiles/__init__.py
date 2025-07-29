import sys
import typer
from typing_extensions import Annotated
from typing import List
from pathlib import Path
from freshfiles.age import get_max_file_age_in_seconds_pathlib


app = typer.Typer()


@app.command()
def all_fresher_than(
    max_age_seconds: Annotated[
        int,
        typer.Option(
            help="The maximum age in seconds that files are considered valid for."
        ),
    ],
    files: List[Path],
) -> bool:
    """
    Checks if all specified files are fresher (younger) than a given expiry age.

    Sample use-case: `freshfiles --max_age_seconds 3600 file1 file2 || ./update_files.sh`

    This command calculates the maximum age among the provided files and compares
    it against `max_age_seconds`.

    Returns:
        Exits with status 0 if all files are fresher than `max_age_seconds`,
        otherwise exits with status 1.
    """
    files_max_age = get_max_file_age_in_seconds_pathlib(files)
    if not files_max_age:
        sys.exit(1)
    elif files_max_age > max_age_seconds:
        sys.exit(1)
    else:
        sys.exit(0)


def main():
    """
    Entry point for the FreshFiles CLI application.
    """
    app()
