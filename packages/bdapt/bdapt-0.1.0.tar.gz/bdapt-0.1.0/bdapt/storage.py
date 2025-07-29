"""Storage layer for bdapt with file locking."""

import fcntl
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

import typer
from rich.console import Console

from .models import BundleStorage

# Module-level console for error output
_console = Console(stderr=True)


class BundleStore:
    """Manages persistent storage of bundle definitions."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the bundle store.

        Args:
            data_dir: Directory for data storage. Defaults to ~/.local/share/bdapt
        """
        if data_dir is None:
            data_dir = Path.home() / ".local" / "share" / "bdapt"

        self.data_dir = data_dir
        self.bundles_file = data_dir / "bundles.json"
        self.lock_file = data_dir / ".bdapt.lock"

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _lock(self) -> Generator[None, None, None]:
        """Context manager for file locking."""
        lock_fd = None
        try:
            # Create lock file if it doesn't exist
            lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_WRONLY, 0o644)

            # Acquire exclusive lock
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            yield
        except OSError as e:
            _console.print(f"[red]Error: Failed to acquire lock: {e}[/red]")
            raise typer.Exit(1)
        finally:
            if lock_fd is not None:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.close(lock_fd)

    def load(self) -> BundleStorage:
        """Load bundle storage from disk with locking."""
        with self._lock():
            if not self.bundles_file.exists():
                return BundleStorage()

            try:
                with open(self.bundles_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return BundleStorage.model_validate(data)
            except (json.JSONDecodeError, ValueError) as e:
                _console.print(
                    f"[red]Error: Failed to load bundles: {e}[/red]")
                raise typer.Exit(1)

    def save(self, storage: BundleStorage) -> None:
        """Save bundle storage to disk with locking."""
        with self._lock():
            try:
                with open(self.bundles_file, "w", encoding="utf-8") as f:
                    json.dump(
                        storage.model_dump(),
                        f,
                        indent=2,
                        sort_keys=True,
                    )
            except OSError as e:
                _console.print(
                    f"[red]Error: Failed to save bundles: {e}[/red]")
                raise typer.Exit(1)
