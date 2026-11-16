"""Atomic file replacement and rollback for this installer's owned files.

Reported I/O failures restore previous bytes; this is not a cross-process
transaction service or a guarantee against machine loss during rollback.
"""
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.rf-update-', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def file_transaction(paths):
    originals = {path: path.read_bytes() if path.is_file() else None for path in paths}
    try:
        yield
    except (OSError, ValueError):
        for path, original in reversed(list(originals.items())):
            if original is None:
                path.unlink(missing_ok=True)
            elif not path.is_file() or path.read_bytes() != original:
                atomic_write(path, original)
        raise
