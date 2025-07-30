import os
import subprocess
import tomli
from pathlib import Path
from typing import Tuple, Optional
import sys

from rich.console import Console

console = Console()


def check_version() -> None:
    """Run snowcli app deploy --stage <stage>."""
    try:
        cmd = ["snow", "--version"]
        print(f"✅ Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(e.returncode)


# --- Helper Functions ---

def _get_context_from_path(file_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Parses a file path to extract the database and schema names.
    Expects a path like 'setup/db_name/schema_name/file.sql'.
    """
    parts = file_path.parts
    if len(parts) >= 3 and parts[0] in ['setup', 'snowflake_structure']:
        return parts[1], parts[2]  # (database, schema)
    return None, None


def _get_default_context() -> Tuple[Optional[str], Optional[str]]:
    """
    Gets the default database and schema from config and environment variables.
    """
    try:
        with open("config.toml", "rb") as f:
            config = tomli.load(f)

        conn_name = config.get("default_connection_name")
        if not conn_name:
            return None, None

        prefix = f"SNOWFLAKE_CONNECTIONS_{conn_name.upper()}"
        db = os.getenv(f"{prefix}_DATABASE")
        schema = os.getenv(f"{prefix}_SCHEMA")
        return db, schema

    except FileNotFoundError:
        return None, None


def _run_snow_query(query: str):
    """A robust wrapper for executing 'snow sql -q'."""
    console.print(f"\n[bold cyan]Executing query via snowcli...[/bold cyan]")

    try:
        command = ["snow", "sql", "-q", query]
        # Using a list for the command is safer and handles quoting correctly.
        subprocess.run(command, check=True)

    except FileNotFoundError:
        console.print("\n[bold red]❌ ERROR: `snow` command not found.[/bold red]")
        console.print("   Please ensure the Snowflake CLI is installed and in your system's PATH.")

    except subprocess.CalledProcessError:
        console.print("\n[bold red]❌ Execution failed. See the output above from snowcli for details.[/bold red]")


# --- Public CLI-Facing Functions ---

def execute(
    file: Optional[str] = None,
    query: Optional[str] = None,
    use_local_context: bool = False
) -> None:
    """
    Executes SQL against Snowflake from either a file or a query string.
    Can be forced to use the local .env context.
    """
    final_query = ""

    if file:
        file_path = Path(file)
        if not file_path.exists():
            console.print(f"[bold red]❌ ERROR: File not found at '{file}'[/bold red]")
            return

        db, schema = (None, None)
        if use_local_context:
            # In local mode, always get context from the .env file.
            db, schema = _get_default_context()
            if not db or not schema:
                console.print("[bold red]❌ ERROR: --local mode requires default DB/Schema in .env[/bold red]")
                return
        else:
            # In normal mode, get context from the file path.
            db, schema = _get_context_from_path(file_path)
            if not db or not schema:
                console.print(f"[bold red]❌ ERROR: Could not determine context from path '{file}'[/bold red]")
                return

        final_query = f"use schema {db}.{schema}; !source ./{file_path}"

    elif query:
        # The 'query' command always uses the default/local context, so its logic is already correct.
        db, schema = _get_default_context()
        if not db or not schema:
            console.print("[bold red]❌ ERROR: Could not determine default context from .env[/bold red]")
            return
        final_query = f"use schema {db}.{schema}; {query}"

    else:
        console.print("[bold red]❌ ERROR: Must provide either a file or a query.[/bold red]")
        return

    _run_snow_query(final_query)
