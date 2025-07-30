"""
Show command for displaying individual todo details
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from todo.storage import get_storage

console = Console()


def show_command(todo_id: int) -> None:
    """Display detailed information about a specific todo item."""
    storage = get_storage()
    
    # Check if todo list is initialized
    if not storage.exists():
        console.print(
            Panel(
                Text("Todo list not initialized!", style="red"),
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
        console.print("Run [bold green]todo init[/bold green] first to create a todo list.")
        raise typer.Exit(1)
    
    try:
        # Get the todo item
        todo = storage.get_todo(todo_id)
        
        if not todo:
            console.print(
                Panel(
                    Text(f"Todo with ID {todo_id} not found!", style="red"),
                    title="Error",
                    title_align="left",
                    border_style="red",
                )
            )
            raise typer.Exit(1)
        
        # Create detailed display
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Field", style="bold cyan", width=15)
        table.add_column("Value", style="white")
        
        # Add rows
        table.add_row("ID", str(todo.id))
        table.add_row("Status", todo.status.capitalize())
        table.add_row("Priority", todo.priority.capitalize())
        table.add_row("Task", todo.content)
        
        if todo.due_date:
            table.add_row("Due Date", str(todo.due_date))
        
        table.add_row("Created", todo.created_at.strftime("%Y-%m-%d %H:%M"))
        
        if todo.completed_at:
            table.add_row("Completed", todo.completed_at.strftime("%Y-%m-%d %H:%M"))
        
        # Status-based styling for the panel
        if todo.status == "completed":
            border_style = "green"
            title_style = "green"
        elif todo.is_overdue:
            border_style = "red"
            title_style = "red"
        else:
            border_style = "blue"
            title_style = "blue"
        
        # Display the panel
        console.print(
            Panel(
                table,
                title=f"[{title_style}]Todo Details[/{title_style}]",
                title_align="left",
                border_style=border_style,
            )
        )
        
    except Exception as e:
        console.print(
            Panel(
                Text(f"Failed to show todo: {str(e)}", style="red"),
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
        raise typer.Exit(1)