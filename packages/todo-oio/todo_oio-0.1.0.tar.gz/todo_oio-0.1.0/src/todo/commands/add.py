"""
Add command for creating new todo items
"""

import typer
from datetime import datetime, date, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import Optional

from todo.models import TodoItem
from todo.storage import get_storage

console = Console()


def parse_due_date(due_str: str) -> Optional[date]:
    """Parse a due date string into a date object."""
    if not due_str:
        return None
    
    due_str = due_str.lower().strip()
    
    # Handle relative dates
    if due_str in ["today"]:
        return date.today()
    elif due_str in ["tomorrow"]:
        return date.today() + timedelta(days=1)
    elif due_str in ["next week"]:
        return date.today() + timedelta(days=7)
    elif due_str in ["next month"]:
        return date.today() + timedelta(days=30)
    
    # Handle ISO format dates (YYYY-MM-DD)
    try:
        return date.fromisoformat(due_str)
    except ValueError:
        pass
    
    # Handle other common formats
    try:
        # Try parsing MM/DD/YYYY
        return datetime.strptime(due_str, "%m/%d/%Y").date()
    except ValueError:
        pass
    
    try:
        # Try parsing DD-MM-YYYY
        return datetime.strptime(due_str, "%d-%m-%Y").date()
    except ValueError:
        pass
    
    return None


def add_command(task: str, priority: Optional[str] = None, due: Optional[str] = None) -> None:
    """Add a new todo item."""
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
    
    # Validate priority
    valid_priorities = ["low", "medium", "high"]
    if priority and priority not in valid_priorities:
        console.print(
            Panel(
                Text(f"Invalid priority: {priority}. Must be one of: {', '.join(valid_priorities)}", style="red"),
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
        raise typer.Exit(1)
    
    # Parse due date
    due_date = None
    if due:
        due_date = parse_due_date(due)
        if due_date is None:
            console.print(
                Panel(
                    Text(f"Invalid due date format: {due}", style="red"),
                    title="Error",
                    title_align="left",
                    border_style="red",
                )
            )
            console.print(
                "Supported formats:\n"
                "• [bold]today[/bold], [bold]tomorrow[/bold], [bold]next week[/bold], [bold]next month[/bold]\n"
                "• [bold]YYYY-MM-DD[/bold] (e.g., 2024-01-15)\n"
                "• [bold]MM/DD/YYYY[/bold] (e.g., 01/15/2024)\n"
                "• [bold]DD-MM-YYYY[/bold] (e.g., 15-01-2024)"
            )
            raise typer.Exit(1)
    
    try:
        # Create new todo item
        todo = TodoItem(
            id=storage.get_next_id(),
            content=task,
            priority=priority or "medium",
            due_date=due_date
        )
        
        # Add to storage
        storage.add_todo(todo)
        
        # Create success message
        success_text = f"Added todo: {task}"
        if priority:
            success_text += f" [Priority: {priority}]"
        if due_date:
            success_text += f" [Due: {due_date}]"
        
        console.print(
            Panel(
                Text(success_text, style="green"),
                title="Success",
                title_align="left",
                border_style="green",
            )
        )
        console.print(f"Todo ID: [bold blue]{todo.id}[/bold blue]")
        
    except Exception as e:
        console.print(
            Panel(
                Text(f"Failed to add todo: {str(e)}", style="red"),
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
        raise typer.Exit(1)