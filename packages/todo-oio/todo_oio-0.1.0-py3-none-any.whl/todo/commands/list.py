"""
List command for displaying todo items
"""

import typer
from datetime import date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import Optional, List

from todo.models import TodoItem
from todo.storage import get_storage

console = Console()


def filter_todos(todos: List[TodoItem], status: Optional[str] = None, priority: Optional[str] = None) -> List[TodoItem]:
    """Filter todos based on status and priority."""
    filtered = todos
    
    if status:
        if status == "all":
            pass  # No filtering
        elif status in ["pending", "completed"]:
            filtered = [todo for todo in filtered if todo.status == status]
        else:
            console.print(f"[red]Invalid status filter: {status}. Use 'pending', 'completed', or 'all'.[/red]")
            raise typer.Exit(1)
    
    if priority:
        if priority in ["low", "medium", "high"]:
            filtered = [todo for todo in filtered if todo.priority == priority]
        else:
            console.print(f"[red]Invalid priority filter: {priority}. Use 'low', 'medium', or 'high'.[/red]")
            raise typer.Exit(1)
    
    return filtered


def sort_todos(todos: List[TodoItem], sort_by: str = "created") -> List[TodoItem]:
    """Sort todos based on the specified criteria."""
    if sort_by == "created":
        return sorted(todos, key=lambda x: x.created_at)
    elif sort_by == "priority":
        return sorted(todos, key=lambda x: x.priority_weight, reverse=True)
    elif sort_by == "due":
        # Sort by due date, putting items without due dates at the end
        return sorted(todos, key=lambda x: (x.due_date is None, x.due_date or date.max))
    else:
        console.print(f"[red]Invalid sort option: {sort_by}. Use 'created', 'priority', or 'due'.[/red]")
        raise typer.Exit(1)


def get_priority_display(priority: str) -> str:
    """Get display string for priority level."""
    return priority.capitalize()


def format_due_date(due_date: Optional[date]) -> str:
    """Format due date with color coding."""
    if due_date is None:
        return ""
    
    today = date.today()
    days_until = (due_date - today).days
    
    if days_until < 0:
        return f"[red]{due_date} (overdue)[/red]"
    elif days_until == 0:
        return f"[yellow]{due_date} (today)[/yellow]"
    elif days_until == 1:
        return f"[orange3]{due_date} (tomorrow)[/orange3]"
    elif days_until <= 7:
        return f"[yellow]{due_date} ({days_until} days)[/yellow]"
    else:
        return f"[green]{due_date}[/green]"


def list_command(status: Optional[str] = None, priority: Optional[str] = None, sort: str = "created") -> None:
    """List all todo items with optional filtering and sorting."""
    storage = get_storage()
    
    # Check if todo list is initialized
    if not storage.exists():
        console.print(
            Panel(
                Text("Todo list not initialized!", style="red"),
                title="❌ Error",
                title_align="left",
                border_style="red",
            )
        )
        console.print("Run [bold green]todo init[/bold green] first to create a todo list.")
        raise typer.Exit(1)
    
    try:
        # Load todos
        todos = storage.load_todos()
        
        if not todos:
            console.print(
                Panel(
                    Text("No todos found!", style="yellow"),
                    title="Todo List",
                    title_align="left",
                    border_style="yellow",
                )
            )
            console.print("Add your first todo with: [bold green]todo add \"Your task here\"[/bold green]")
            return
        
        # Filter todos
        filtered_todos = filter_todos(todos, status, priority)
        
        if not filtered_todos:
            console.print(
                Panel(
                    Text("No todos match your filters!", style="yellow"),
                    title="Todo List",
                    title_align="left",
                    border_style="yellow",
                )
            )
            return
        
        # Sort todos
        sorted_todos = sort_todos(filtered_todos, sort)
        
        # Create table
        table = Table(show_header=True, header_style="bold magenta", width=120)
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Status", width=10)
        table.add_column("Priority", width=10)
        table.add_column("Task", style="white", min_width=40)
        table.add_column("Due Date", style="yellow", width=20)
        table.add_column("Created", style="dim", width=12)
        
        for todo in sorted_todos:
            status_display = todo.status
            priority_display = get_priority_display(todo.priority)
            due_display = format_due_date(todo.due_date)
            created_display = todo.created_at.strftime("%Y-%m-%d")
            
            # Style the task based on status
            if todo.status == "completed":
                task_display = f"[dim strikethrough]{todo.content}[/dim strikethrough]"
            elif todo.is_overdue:
                task_display = f"[red]{todo.content}[/red]"
            else:
                task_display = todo.content
            
            table.add_row(
                str(todo.id),
                status_display,
                priority_display,
                task_display,
                due_display,
                created_display
            )
        
        # Display table with title
        filter_info = []
        if status:
            filter_info.append(f"status:{status}")
        if priority:
            filter_info.append(f"priority:{priority}")
        if sort != "created":
            filter_info.append(f"sort:{sort}")
        
        title = "Todo List"
        if filter_info:
            title += f" ({', '.join(filter_info)})"
        
        console.print(Panel(table, title=title, title_align="left"))
        
        # Summary statistics
        total_todos = len(todos)
        completed_todos = len([t for t in todos if t.status == "completed"])
        pending_todos = total_todos - completed_todos
        overdue_todos = len([t for t in todos if t.is_overdue])
        
        summary_text = f"Total: {total_todos} | Pending: {pending_todos} | Completed: {completed_todos}"
        if overdue_todos > 0:
            summary_text += f" | [red]Overdue: {overdue_todos}[/red]"
        
        console.print(f"\n{summary_text}")
        
    except Exception as e:
        console.print(
            Panel(
                Text(f"Failed to list todos: {str(e)}", style="red"),
                title="❌ Error",
                title_align="left",
                border_style="red",
            )
        )
        raise typer.Exit(1)