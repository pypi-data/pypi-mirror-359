# Todo OIO

A modern, intuitive command-line todo application built with Python. Features beautiful terminal UI, priority levels, due dates, and more.

## Installation

Install from PyPI:
```bash
pip install todo-oio
```

Or install from source:
```bash
git clone https://github.com/todo-oio/todo-oio.git
cd todo-oio
pip install -e .
```

## Quick Start

1. Initialize your todo list:
```bash
todo init
```

2. Add your first todo:
```bash
todo add "Buy groceries"
```

3. List all todos:
```bash
todo list
```

## Commands

### Initialize
```bash
todo init                    # Create a new todo list
todo init --force            # Reinitialize (overwrites existing)
```

### Add Tasks
```bash
todo add "Task description"                    # Basic task
todo add "Important task" --priority high      # With priority
todo add "Meeting" --due tomorrow              # With due date
todo add "Project" --priority high --due 2024-01-15  # Both
```

### List Tasks
```bash
todo list                           # Show all tasks
todo list --status pending         # Show only pending tasks
todo list --status completed       # Show only completed tasks
todo list --priority high          # Show only high priority tasks
todo list --sort priority          # Sort by priority
todo list --sort due               # Sort by due date
```

### Manage Tasks
```bash
todo complete 1                    # Mark task as completed
todo edit 1                        # Edit task interactively
todo delete 1                      # Delete task (with confirmation)
```

## Features

- **Beautiful terminal UI** with colors and clean formatting
- **Due dates** with flexible parsing (today, tomorrow, YYYY-MM-DD, etc.)
- **Priority levels** (low, medium, high)
- **Status tracking** (pending, completed)
- **Filtering and sorting** options
- **JSON storage** in your home directory
- **Interactive editing** with confirmation prompts
- **Overdue detection** with visual indicators
- **Individual todo details** with `todo show` command

## Priority Levels

- **High**: Critical tasks that need immediate attention
- **Medium**: Important tasks with normal priority (default)
- **Low**: Tasks that can be done when time permits

## Due Date Formats

Flexible date parsing supports:
- `today`, `tomorrow`
- `next week`, `next month`
- `YYYY-MM-DD` (e.g., `2024-01-15`)
- `MM/DD/YYYY` (e.g., `01/15/2024`)
- `DD-MM-YYYY` (e.g., `15-01-2024`)

## Data Storage

Your todos are stored in `~/.todo.json` in your home directory. The file is automatically created when you run `todo init`.

## Examples

```bash
# Initialize and add some tasks
todo init
todo add "Write project proposal" --priority high --due tomorrow
todo add "Review code" --priority medium
todo add "Update documentation" --priority low --due "next week"

# List tasks with different views
todo list                                # All tasks
todo list --status pending --sort priority  # Pending tasks by priority
todo list --priority high                   # High priority tasks only

# Manage tasks
todo complete 1                         # Mark first task as done
todo edit 2                             # Edit second task
todo delete 3                           # Delete third task
```

## Command Reference

### Core Commands
- `todo init` - Initialize a new todo list
- `todo add <task>` - Add a new todo item
- `todo list` - Show all todos
- `todo show <id>` - Show detailed todo information
- `todo complete <id>` - Mark todo as completed
- `todo edit <id>` - Edit todo interactively
- `todo delete <id>` - Delete todo with confirmation

### Options
- `--priority` / `-p` - Set priority (low, medium, high)
- `--due` / `-d` - Set due date
- `--status` / `-s` - Filter by status (pending, completed, all)
- `--sort` - Sort by (created, priority, due)

## Development

This project uses modern Python tooling:

- **Framework**: [Typer](https://typer.tiangolo.com/) for CLI
- **UI**: [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- **Testing**: pytest
- **Code Quality**: black, isort, flake8, mypy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see the [LICENSE](LICENSE) file for details.