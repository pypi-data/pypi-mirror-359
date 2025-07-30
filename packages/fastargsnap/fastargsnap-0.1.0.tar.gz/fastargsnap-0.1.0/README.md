# FastArgSnap

A fast argument completion library that uses a snapshot-based approach to provide instant tab completion for argparse-based CLI tools without importing the full application.

## Problem

Traditional argcomplete-based tab completion requires importing the entire CLI application, which can be slow when the application has heavy dependencies (like matplotlib, numpy, pandas, etc.). This results in poor user experience with delays of several seconds when pressing Tab.

## Solution

FastArgSnap generates a lightweight JSON snapshot of the argument parser structure during development/build time. At runtime, it provides instant completions by reading this snapshot instead of importing the full application.

## Features

- **Instant completions**: No import delays, completions appear immediately
- **Lightweight**: JSON snapshots are typically <10KB
- **Comprehensive**: Captures all arguments, subcommands, choices, and help text
- **Easy integration**: Simple decorator or function call to enable
- **Backward compatible**: Works alongside existing argcomplete setups

## Installation

```bash
pip install fastargsnap
```

## Quick Start

### 1. Generate a snapshot

```python
# In your CLI application
from fastargsnap import generate_snapshot
import argparse

def create_parser():
    parser = argparse.ArgumentParser(description="My CLI tool")
    # ... your argument definitions ...
    return parser

# Generate snapshot (run this during development/build)
if __name__ == "__main__":
    parser = create_parser()
    generate_snapshot(parser, "mycli_snapshot.json")
```

### 2. Use the snapshot for completions

```python
# In your CLI application
from fastargsnap import FastArgSnap
import argparse

def create_parser():
    parser = argparse.ArgumentParser(description="My CLI tool")
    # ... your argument definitions ...
    return parser

def main():
    parser = create_parser()

    # Enable fast completions
    fast_snap = FastArgSnap("mycli_snapshot.json")
    fast_snap.autocomplete(parser)

    args = parser.parse_args()
    # ... your CLI logic ...

if __name__ == "__main__":
    main()
```

### 3. Register shell completion

```bash
# For bash/zsh
eval "$(register-python-argcomplete mycli)"

# Or use the fastargsnap CLI
fastargsnap register mycli
```

## Advanced Usage

### Decorator approach

```python
from fastargsnap import fast_complete

@fast_complete("mycli_snapshot.json")
def main():
    parser = argparse.ArgumentParser()
    # ... your parser setup ...
    args = parser.parse_args()
    # ... your logic ...
```

### Custom snapshot paths

```python
from fastargsnap import FastArgSnap

# Use custom snapshot location
fast_snap = FastArgSnap("/path/to/custom/snapshot.json")
fast_snap.autocomplete(parser)
```

### Fallback to argcomplete

```python
from fastargsnap import FastArgSnap
import argcomplete

fast_snap = FastArgSnap("snapshot.json")
if not fast_snap.autocomplete(parser):
    # Fallback to regular argcomplete if snapshot fails
    argcomplete.autocomplete(parser)
```

## CLI Tool

FastArgSnap includes a CLI tool for managing snapshots:

```bash
# Generate snapshot from existing CLI
fastargsnap generate mycli mycli_snapshot.json

# Register completion for a CLI tool
fastargsnap register mycli

# List registered completions
fastargsnap list

# Remove completion registration
fastargsnap unregister mycli
```

## Performance Comparison

| Approach | Startup Time | Completion Time | Memory Usage |
|----------|-------------|----------------|--------------|
| Traditional argcomplete | 2-30 seconds | 2-30 seconds | High |
| FastArgSnap | <100ms | <100ms | Low |

## Integration Examples

### With Click

```python
import click
from fastargsnap import FastArgSnap

@click.command()
@click.option('--name', help='Your name')
def hello(name):
    click.echo(f"Hello {name}!")

if __name__ == "__main__":
    # Convert Click to argparse for snapshot
    parser = hello.to_argparse()
    fast_snap = FastArgSnap("hello_snapshot.json")
    fast_snap.autocomplete(parser)
    hello()
```

### With Typer

```python
import typer
from fastargsnap import FastArgSnap

app = typer.Typer()

@app.command()
def hello(name: str):
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    # Convert Typer to argparse for snapshot
    parser = app.to_argparse()
    fast_snap = FastArgSnap("typer_app_snapshot.json")
    fast_snap.autocomplete(parser)
    app()
```

## Development

```bash
git clone https://github.com/udayayya/fastargsnap
cd fastargsnap
pip install -e '.[dev]'

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
