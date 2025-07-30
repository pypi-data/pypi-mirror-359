"""
Main CLI application entry point
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from todo.commands.init import init_command
from todo.commands.add import add_command
from todo.commands.list import list_command
from todo.commands.complete import complete_command
from todo.commands.delete import delete_command
from todo.commands.edit import edit_command
from todo.commands.show import show_command

console = Console()
app = typer.Typer(
    name="todo",
    help="A modern, intuitive CLI todo application",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


@app.command("init")
def init(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force initialization even if todo file exists"
    )
):
    """Initialize a new todo list in your home directory."""
    init_command(force)


@app.command("add")
def add(
    task: str = typer.Argument(..., help="Task description"),
    priority: Optional[str] = typer.Option(
        "medium", "--priority", "-p", help="Priority level (low, medium, high)"
    ),
    due: Optional[str] = typer.Option(
        None, "--due", "-d", help="Due date (e.g., 'tomorrow', '2024-01-15')"
    ),
):
    """Add a new todo item."""
    add_command(task, priority, due)


@app.command("list")
def list_todos(
    status: Optional[str] = typer.Option(
        None, "--status", "-s", help="Filter by status (pending, completed, all)"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", "-p", help="Filter by priority (low, medium, high)"
    ),
    sort: Optional[str] = typer.Option(
        "created", "--sort", help="Sort by (created, priority, due)"
    ),
):
    """List all todo items."""
    list_command(status, priority, sort)


@app.command("complete")
def complete(
    todo_id: int = typer.Argument(..., help="ID of the todo item to complete")
):
    """Mark a todo item as completed."""
    complete_command(todo_id)


@app.command("delete")
def delete(
    todo_id: int = typer.Argument(..., help="ID of the todo item to delete")
):
    """Delete a todo item."""
    delete_command(todo_id)


@app.command("edit")
def edit(
    todo_id: int = typer.Argument(..., help="ID of the todo item to edit")
):
    """Edit an existing todo item."""
    edit_command(todo_id)


@app.command("show")
def show(
    todo_id: int = typer.Argument(..., help="ID of the todo item to show")
):
    """Show detailed information about a todo item."""
    show_command(todo_id)


@app.callback()
def main():
    """
    Todo CLI - A modern, intuitive command-line todo application.
    
    Initialize with: [bold green]todo init[/bold green]
    Add a task: [bold green]todo add "Your task here"[/bold green]
    List tasks: [bold green]todo list[/bold green]
    """
    pass


if __name__ == "__main__":
    app()