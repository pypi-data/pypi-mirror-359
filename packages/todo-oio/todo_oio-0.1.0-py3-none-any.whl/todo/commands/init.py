"""
Initialize command for creating a new todo list
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from todo.storage import get_storage

console = Console()


def init_command(force: bool = False) -> None:
    """Initialize a new todo list in the user's home directory."""
    storage = get_storage()
    
    if storage.exists() and not force:
        console.print(
            Panel(
                Text("Todo list already exists!", style="yellow"),
                title="Warning",
                title_align="left",
                border_style="yellow",
            )
        )
        console.print(
            f"Location: [blue]{storage.file_path}[/blue]\n"
            f"Use [bold green]todo init --force[/bold green] to reinitialize."
        )
        return
    
    try:
        created = storage.initialize(force=force)
        
        if created or force:
            console.print(
                Panel(
                    Text("Todo list initialized successfully!", style="green"),
                    title="Success",
                    title_align="left",
                    border_style="green",
                )
            )
            console.print(
                f"Location: [blue]{storage.file_path}[/blue]\n"
                f"Start adding todos with: [bold green]todo add \"Your first task\"[/bold green]"
            )
        else:
            console.print(
                Panel(
                    Text("Todo list already exists!", style="yellow"),
                    title="Warning",
                    title_align="left",
                    border_style="yellow",
                )
            )
            console.print(
                f"Location: [blue]{storage.file_path}[/blue]"
            )
    
    except Exception as e:
        console.print(
            Panel(
                Text(f"Failed to initialize todo list: {str(e)}", style="red"),
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
        raise typer.Exit(1)