"""
Complete command for marking todo items as completed
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from todo.storage import get_storage

console = Console()


def complete_command(todo_id: int) -> None:
    """Mark a todo item as completed."""
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
        
        # Check if already completed
        if todo.status == "completed":
            console.print(
                Panel(
                    Text(f"Todo {todo_id} is already completed!", style="yellow"),
                    title="Warning",
                    title_align="left",
                    border_style="yellow",
                )
            )
            console.print(f"Task: [dim strikethrough]{todo.content}[/dim strikethrough]")
            return
        
        # Mark as completed
        todo.complete()
        
        # Update in storage
        storage.update_todo(todo_id, {
            "status": todo.status,
            "completed_at": todo.completed_at
        })
        
        # Success message
        console.print(
            Panel(
                Text(f"Todo {todo_id} marked as completed!", style="green"),
                title="Success",
                title_align="left",
                border_style="green",
            )
        )
        console.print(f"Task: [dim strikethrough]{todo.content}[/dim strikethrough]")
        
    except Exception as e:
        console.print(
            Panel(
                Text(f"Failed to complete todo: {str(e)}", style="red"),
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
        raise typer.Exit(1)