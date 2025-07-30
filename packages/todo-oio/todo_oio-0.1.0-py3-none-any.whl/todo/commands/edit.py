"""
Edit command for modifying existing todo items
"""

import typer
from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from typing import Optional

from todo.storage import get_storage
from todo.commands.add import parse_due_date

console = Console()


def edit_command(todo_id: int) -> None:
    """Edit an existing todo item."""
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
        
        # Show current todo details
        console.print(f"Current todo details:")
        console.print(f"  ID: [bold blue]{todo.id}[/bold blue]")
        console.print(f"  Task: [white]{todo.content}[/white]")
        console.print(f"  Status: [{'green' if todo.status == 'completed' else 'yellow'}]{todo.status}[/{'green' if todo.status == 'completed' else 'yellow'}]")
        console.print(f"  Priority: {todo.priority}")
        if todo.due_date:
            console.print(f"  Due: {todo.due_date}")
        console.print()
        
        # Collect new values
        updates = {}
        
        # Edit task content
        new_content = Prompt.ask(
            "New task content (press Enter to keep current)",
            default=todo.content,
            show_default=False
        )
        if new_content != todo.content:
            updates["content"] = new_content
        
        # Edit priority
        current_priority = todo.priority
        new_priority = Prompt.ask(
            "New priority (low/medium/high, press Enter to keep current)",
            default=current_priority,
            show_default=False
        )
        if new_priority != current_priority:
            if new_priority not in ["low", "medium", "high"]:
                console.print(f"[red]Invalid priority: {new_priority}. Keeping current priority.[/red]")
            else:
                updates["priority"] = new_priority
        
        # Edit due date
        current_due = str(todo.due_date) if todo.due_date else "none"
        new_due = Prompt.ask(
            "New due date (YYYY-MM-DD, 'today', 'tomorrow', 'none', or press Enter to keep current)",
            default=current_due,
            show_default=False
        )
        
        if new_due != current_due:
            if new_due.lower() == "none":
                updates["due_date"] = None
            else:
                parsed_due = parse_due_date(new_due)
                if parsed_due is None:
                    console.print(f"[red]Invalid due date format: {new_due}. Keeping current due date.[/red]")
                else:
                    updates["due_date"] = parsed_due
        
        # Edit status
        if todo.status == "pending":
            if Confirm.ask("Mark as completed?", default=False):
                updates["status"] = "completed"
                updates["completed_at"] = date.today()
        elif todo.status == "completed":
            if Confirm.ask("Mark as pending?", default=False):
                updates["status"] = "pending"
                updates["completed_at"] = None
        
        # Apply updates if any
        if not updates:
            console.print("[yellow]No changes made.[/yellow]")
            return
        
        # Confirm changes
        console.print("\nChanges to be made:")
        for key, value in updates.items():
            console.print(f"  {key}: {value}")
        
        if not Confirm.ask("\nApply these changes?", default=True):
            console.print("[yellow]Changes cancelled.[/yellow]")
            return
        
        # Update the todo
        success = storage.update_todo(todo_id, updates)
        
        if success:
            console.print(
                Panel(
                    Text(f"Todo {todo_id} updated successfully!", style="green"),
                    title="Success",
                    title_align="left",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    Text(f"Failed to update todo {todo_id}!", style="red"),
                    title="Error",
                    title_align="left",
                    border_style="red",
                )
            )
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(
            Panel(
                Text(f"Failed to edit todo: {str(e)}", style="red"),
                title="Error",
                title_align="left",
                border_style="red",
            )
        )
        raise typer.Exit(1)