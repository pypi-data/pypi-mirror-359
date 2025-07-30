"""
Storage management for todo items
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console

from todo.models import TodoItem

console = Console()


class TodoStorage:
    """Handles reading and writing todo items to file storage."""
    
    def __init__(self, file_path: Optional[str] = None):
        """Initialize storage with optional custom file path."""
        if file_path:
            self.file_path = Path(file_path)
        else:
            self.file_path = Path.home() / ".todo.json"
    
    def initialize(self, force: bool = False) -> bool:
        """Initialize the todo file. Returns True if created, False if already exists."""
        if self.file_path.exists() and not force:
            return False
        
        initial_data = {
            "todos": [],
            "next_id": 1,
            "created_at": "2024-01-01T00:00:00",
            "version": "1.0"
        }
        
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.file_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
        
        return True
    
    def exists(self) -> bool:
        """Check if the todo file exists."""
        return self.file_path.exists()
    
    def load_data(self) -> Dict[str, Any]:
        """Load the raw JSON data from the file."""
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Todo file not found at {self.file_path}. Run 'todo init' first."
            )
        
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValueError(
                f"Invalid JSON in todo file at {self.file_path}. File may be corrupted."
            )
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """Save the raw JSON data to the file."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_todos(self) -> List[TodoItem]:
        """Load all todo items from storage."""
        data = self.load_data()
        todos = []
        
        for todo_data in data.get("todos", []):
            try:
                todo = TodoItem.from_dict(todo_data)
                todos.append(todo)
            except Exception as e:
                console.print(f"[red]Warning: Skipping invalid todo item: {e}[/red]")
        
        return todos
    
    def save_todos(self, todos: List[TodoItem]) -> None:
        """Save all todo items to storage."""
        try:
            data = self.load_data()
        except FileNotFoundError:
            data = {"todos": [], "next_id": 1, "created_at": "2024-01-01T00:00:00", "version": "1.0"}
        
        data["todos"] = [todo.to_dict() for todo in todos]
        
        # Update next_id to be one more than the highest current ID
        if todos:
            max_id = max(todo.id for todo in todos)
            data["next_id"] = max_id + 1
        
        self.save_data(data)
    
    def get_next_id(self) -> int:
        """Get the next available ID for a new todo item."""
        try:
            data = self.load_data()
            return data.get("next_id", 1)
        except FileNotFoundError:
            return 1
    
    def add_todo(self, todo: TodoItem) -> None:
        """Add a single todo item to storage."""
        todos = self.load_todos()
        
        # Set the ID if not already set
        if todo.id == 0:
            todo.id = self.get_next_id()
        
        todos.append(todo)
        self.save_todos(todos)
    
    def update_todo(self, todo_id: int, updates: Dict[str, Any]) -> bool:
        """Update a todo item by ID. Returns True if found and updated."""
        todos = self.load_todos()
        
        for todo in todos:
            if todo.id == todo_id:
                for key, value in updates.items():
                    if hasattr(todo, key):
                        setattr(todo, key, value)
                self.save_todos(todos)
                return True
        
        return False
    
    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo item by ID. Returns True if found and deleted."""
        todos = self.load_todos()
        original_count = len(todos)
        
        todos = [todo for todo in todos if todo.id != todo_id]
        
        if len(todos) < original_count:
            self.save_todos(todos)
            return True
        
        return False
    
    def get_todo(self, todo_id: int) -> Optional[TodoItem]:
        """Get a specific todo item by ID."""
        todos = self.load_todos()
        
        for todo in todos:
            if todo.id == todo_id:
                return todo
        
        return None


# Global storage instance
_storage = TodoStorage()

def get_storage() -> TodoStorage:
    """Get the global storage instance."""
    return _storage