"""
Data models for todo items
"""

from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional, Dict, Any
import json


@dataclass
class TodoItem:
    """Represents a single todo item."""
    
    id: int
    content: str
    status: str = "pending"  # pending, completed
    priority: str = "medium"  # low, medium, high
    created_at: datetime = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def complete(self):
        """Mark the todo item as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert todo item to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        if self.due_date:
            data["due_date"] = self.due_date.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TodoItem":
        """Create todo item from dictionary."""
        # Convert ISO format strings back to datetime objects
        if "created_at" in data and data["created_at"]:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "due_date" in data and data["due_date"]:
            data["due_date"] = date.fromisoformat(data["due_date"])
        if "completed_at" in data and data["completed_at"]:
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert todo item to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "TodoItem":
        """Create todo item from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @property
    def priority_weight(self) -> int:
        """Return numeric weight for priority sorting."""
        priority_weights = {"low": 1, "medium": 2, "high": 3}
        return priority_weights.get(self.priority, 2)
    
    @property
    def is_overdue(self) -> bool:
        """Check if the todo item is overdue."""
        if self.due_date is None or self.status == "completed":
            return False
        return date.today() > self.due_date