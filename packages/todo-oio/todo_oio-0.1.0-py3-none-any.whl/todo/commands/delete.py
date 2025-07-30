"""
Delete command for removing todo items
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm

from todo.storage import get_storage

console = Console()


def delete_command(todo_id: int) -> None:
    """Delete a todo item."""
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
        
        # Show the todo item that will be deleted
        console.print(f"Todo to delete:")
        console.print(f"  ID: [bold blue]{todo.id}[/bold blue]")
        console.print(f"  Task: [white]{todo.content}[/white]")
        console.print(f"  Status: [{'green' if todo.status == 'completed' else 'yellow'}]{todo.status}[/{'green' if todo.status == 'completed' else 'yellow'}]")
        console.print(f"  Priority: {todo.priority}")
        if todo.due_date:
            console.print(f"  Due: {todo.due_date}")
        console.print()
        
        # Confirm deletion
        if not Confirm.ask("Are you sure you want to delete this todo?"):
            console.print("[yellow]Deletion cancelled.[/yellow]")
            return
        
        # Delete the todo
        deleted = storage.delete_todo(todo_id)
        
        if deleted:
            console.print(
                Panel(
                    Text(f"Todo {todo_id} deleted successfully!", style="green"),
                    title="Success",
                    title_align="left",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    Text(f"Failed to delete todo {todo_id}!", style="red"),
                    title="Error",
                    title_align="left",
                    border_style="red",
                )
            )
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(
            Panel(
                Text(f"Failed to delete todo: {str(e)}", style="red"),
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
        raise typer.Exit(1)