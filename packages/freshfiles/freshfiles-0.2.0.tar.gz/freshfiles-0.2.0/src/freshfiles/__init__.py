import sys
import logging
import typer
from typing_extensions import Annotated
from typing import List
from pathlib import Path
from freshfiles.age import get_max_file_age_in_seconds
from freshfiles.age import get_min_file_age_in_seconds


app = typer.Typer()


@app.command()
def check(
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

    This command calculates the maximum age among the provided files and compares
    it against `max_age_seconds`.

    Returns:
        Exits with status 0 if all files are fresher than `max_age_seconds`,
        otherwise exits with status 1.
    """
    try:
        files_max_age = get_max_file_age_in_seconds(files)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

    if not files_max_age or files_max_age > max_age_seconds:
        sys.exit(1)
    else:
        sys.exit(0)


@app.command()
def compare(
    source_files: Annotated[
        List[Path],
        typer.Option(
            "-s",
            "--source",
        ),
    ],
    target_files: Annotated[
        List[Path],
        typer.Option(
            "-t",
            "--target",
        ),
    ],
) -> bool:
    """
    Checks that all the target files are fresher (younger) than all the source files.

    Returns:
        Exits with status 0 the target files are fresher than the source files,
        otherwise exits with status 1.
    """
    try:
        source_age = get_min_file_age_in_seconds(source_files)
        target_age = get_max_file_age_in_seconds(target_files)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


    if target_age > source_age:
        sys.exit(1)
    else:
        sys.exit(0)


@app.callback()
def cli_app(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Enable verbose mode.",
    ),
):
    """
    Sentinel app to check the age of filesets
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.FATAL)


def main():
    app()
