import json
import sys
from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.table import Table

from . import settings
from .app_logger import log
from .engine import VirusEngine
from .textwrapper import console_log, get_console


def check_file_exist(path):
    cwd = Path.cwd()
    if not (cwd / path).exists():
        raise typer.BadParameter(f"File does not exist : {path}")
    return path


def check_files_exist(paths):
    cwd = Path.cwd()

    for path in paths:
        real_paths = cwd.glob(path)
        ## Checks if the generator is empty
        try:
            _ = next(real_paths)
        except StopIteration:
            raise typer.BadParameter(f"File does not exist : {path}")
    return paths


app = typer.Typer(
    name="virus",
    add_completion=False,
    help="Virus (Validation is Required for Understanding Schema)",
)


@app.command("validate")
def validate(
    src: List[str] = typer.Argument(
        ..., help="Path to the source file", callback=check_files_exist
    ),
    config_path: str = typer.Option(
        settings.DEFAULT_DATASET_RULES,
        help="Path to the config file with Dataset and rules mapping",
        callback=check_file_exist,
    ),
    is_terminal: bool = typer.Option(True, help="Output to terminal"),
    log_file_path: str = typer.Option(
        settings.DEFAULT_LOG_FILE, help="Path to the log file"
    ),
    rules_path: str = typer.Option(
        settings.DEFAULT_VALIDATION_RULES,
        help="Path to the rules file e.g. src/rules.py",
        callback=check_file_exist,
    ),
):
    cwd = Path(".")
    console_out = get_console(is_terminal, log_file_path)
    virus = VirusEngine(config_path, rules_path)
    # add extension .csv if not present in src
    src = [str(path) if path.endswith(".csv") else f"{path}*.csv" for path in src]
    schema_mapping = virus._get_schema_mapping()
    # get all files from the src
    files = set()
    is_error = False
    for dir_path in src:
        files.update(str(file_path) for file_path in cwd.glob(dir_path))
    if files:
        for each_path in files:
            dataset_schema = schema_mapping.get(each_path, False)
            if dataset_schema:
                for each_file, each_df in virus.retrieve_dataset(each_path):
                    response, error = virus.validate_with_schema(
                        dataset_schema, each_df
                    )
                    if error:
                        is_error = True
                    console_log(console_out, response, each_file)
            else:
                log.error(f"Schema not found for {each_path}")
                is_error = True
    else:
        log.error("No files found in the given path")
        is_error = True
    return sys.exit(1) if is_error else sys.exit(0)


@app.command("validate-all")
def validate_all(
    config_path: str = typer.Option(
        settings.DEFAULT_DATASET_RULES,
        help="Path to the config file with Dataset and rules mapping",
        callback=check_file_exist,
    ),
    is_terminal: bool = typer.Option(True, help="Output to terminal"),
    log_file_path: str = typer.Option(
        settings.DEFAULT_LOG_FILE, help="Path to the log file"
    ),
    rules_path: str = typer.Option(
        settings.DEFAULT_VALIDATION_RULES,
        help="Path to the rules file e.g. src/rules.py",
        callback=check_file_exist,
    ),
):
    console_out = get_console(is_terminal, log_file_path)
    virus = VirusEngine(config_path, rules_path)
    schema_mapping = virus._get_schema_mapping()
    is_error = False

    # if schema_mapping is empty, log error and exit
    if schema_mapping:
        for each_path, dataset_schema in schema_mapping.items():
            if dataset_schema:
                for each_file, each_df in virus.retrieve_dataset(each_path):
                    response, error = virus.validate_with_schema(
                        dataset_schema, each_df
                    )
                    if error:
                        is_error = True
                    console_log(console_out, response, each_file)
            else:
                log.error(f"Schema not found for {each_path}")
                is_error = True
    else:
        log.error("Schema not found in the config file")
        is_error = True
    return sys.exit(1) if is_error else sys.exit(0)


@app.command("list")
def list_schema(
    schema_path: Path = typer.Option(
        (Path.cwd() / settings.DEFAULT_DATASET_RULES),
        help="Path to the schema file",
        callback=check_file_exist,
    )
):
    config_dict = json.loads(schema_path.read_text(encoding="UTF-8"))
    console = Console()
    table = Table(show_header=True, header_style="bold", title="Schema List")
    table.add_column("Dataset Path", justify="left", style="cyan", no_wrap=True)
    table.add_column("Schema Name", justify="left", style="magenta")

    for each_path, each_schema in config_dict.items():
        table.add_row(each_path, each_schema)
    console.print(table)


def main():
    app()
