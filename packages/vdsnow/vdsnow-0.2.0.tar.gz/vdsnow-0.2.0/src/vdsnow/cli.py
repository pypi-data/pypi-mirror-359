import click
import os
from pyfiglet import Figlet
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from vdsnow import (
    __version__,
    project_folder,
    snowflake_actions,
    validation,
    connections
)


console = Console()


# The main 'app' is still the entry point
@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx: click.Context) -> None:
    """vdsnow - A CLI for Snowflake project scaffolding, execution, and validation."""
    if ctx.invoked_subcommand is None:
        _show_welcome()

# --- Group 1: Setup Commands ---
@app.group()
def setup() -> None:
    """Commands for initializing and managing project structure."""
    pass

# Attach 'init' to the 'setup' group
@setup.command()
def init() -> None:
    """Initializes a new Snowflake project structure interactively."""
    project_folder.init_snowflake_structure()

@setup.command(name="add-database")
def add_database_command() -> None:
    """Adds a new database to an existing project structure."""
    project_folder.add_database()

@setup.command(name="add-schema")
@click.argument("database_name", required=False)
@click.option("--schema", "schema_names", multiple=True, help="Name of the schema to add. Can be used multiple times.")
def add_schema_command(database_name: Optional[str], schema_names: list[str]) -> None:
    """
    Adds one or more schemas to a database.

    If run without arguments, it will be fully interactive.
    """
    project_folder.add_schema_to_database(database_name, schema_names)


@setup.command(name="refresh-scripts")
def refresh_scripts_command() -> None:
    """
    Scans the './setup' directory and regenerates all setup.sql files.
    """
    project_folder.refresh_setup_scripts()

# Attach 'recreate' to the 'setup' group
@setup.command()
def recreate() -> None:
    """Deletes the existing project structure and re-initializes it."""
    project_folder.recreate_snowflake_structure()


# --- Group 2: SQL Commands (from snowflake_actions) ---
@app.group()
def sql() -> None:
    """Commands for executing SQL against Snowflake."""
    pass

@sql.command(name="execute")
@click.option("-f", "--file", "file_path", type=click.Path(), help="Path to a .sql file to execute.")
@click.option("-q", "--query", "query_string", type=str, help="A raw SQL query string to execute.")
@click.option(
    "--local/--no-local",
    "is_local_mode",
    default=None,
    help="Force use of the default .env context. Overrides the VDSNOW_ENV variable."
)
def execute_command(file_path: Optional[str], query_string: Optional[str], is_local_mode: Optional[bool]) -> None:
    """
    Executes SQL from a file or query string with automatic context.

    In normal mode, context is derived from the file path (e.g., 'setup/db/schema').
    In local mode (--local or VDSNOW_ENV=local), context is always taken from your .env file.
    """
    if not file_path and not query_string:
        console.print("[bold red]Error:[/bold red] Please provide either a --file (-f) or a --query (-q) option.")
        return
    if file_path and query_string:
        console.print("[bold red]Error:[/bold red] Please provide either --file or --query, not both.")
        return

    # Determine if we are running in local mode
    use_local_context = False
    if is_local_mode is not None:
        # The --local/--no-local flag takes highest precedence
        use_local_context = is_local_mode
    else:
        # If the flag isn't used, fall back to the environment variable
        use_local_context = os.getenv("VDSNOW_ENV", "headless").lower() == "local"

    # Inform the user if local mode is active for a file execution
    if use_local_context and file_path:
        console.print("[yellow]--local mode active: Context will be taken from your .env file.[/yellow]")

    snowflake_actions.execute(
        file=file_path,
        query=query_string,
        use_local_context=use_local_context
    )

# --- Group 3: Check Commands ---
@app.group()
def check() -> None:
    """Commands for validating and checking project status."""
    pass

# Attach 'version' to the 'check' group
@check.command(name="version")
def version_command() -> None:
    """Checks the installed SnowCLI version."""
    snowflake_actions.check_version()

# Attach our new 'folder-structure' command
@check.command(name="folder-structure")
def folder_structure_command() -> None:
    """Validates the './snowflake_structure' directory."""
    validation.check_folder_structure()


# --- Group 4: Connection Commands ---
@app.group()
def connection() -> None:
    """Commands for managing Snowflake connections."""
    pass

@connection.command(name="init")
def init_connection_command() -> None:
    """Creates or updates a connection configuration."""
    connections.init_connection()

@connection.command(name="test")
def test_connection_command() -> None:
    """Tests the default Snowflake connection using 'snow connection test'."""
    connections.test_connection()


# The welcome message remains the same
def _show_welcome() -> None:
    figlet = Figlet(font="slant")
    ascii_banner: str = figlet.renderText("VDSNOW")

    panel = Panel(
        ascii_banner,
        title=f"[bold cyan]❄️❄️ v{__version__} ❄️❄️[/bold cyan]",
        border_style="cyan",
        padding=(1, 4),
        expand=False,
    )

    console.print(panel)
    console.print(
        "[bold cyan] ❄️ Run 'vdsnow --help' to explore available commands.[/bold cyan]\n"
    )
