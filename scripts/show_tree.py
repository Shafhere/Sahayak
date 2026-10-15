"""Print the Sahayak project tree with file sizes and counts."""
import os
from pathlib import Path


# Folders/files to skip (noise)
SKIP_DIRS = {
    "venv", ".venv", "__pycache__", ".git", ".cache",
    "chroma_db", ".pytest_cache", ".mypy_cache",
    "node_modules", ".idea", ".vscode",
}

SKIP_FILES = {
    ".DS_Store", "Thumbs.db",
}


def human_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def count_files(path: Path) -> tuple[int, int]:
    """Return (file_count, total_size) for a directory."""
    files = 0
    total = 0
    for root, dirs, filenames in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in filenames:
            if f in SKIP_FILES:
                continue
            files += 1
            try:
                total += (Path(root) / f).stat().st_size
            except OSError:
                pass
    return files, total


def walk(path: Path, prefix: str = "", is_last: bool = True):
    """Recursively print the tree."""
    entries = sorted(
        [e for e in path.iterdir()
         if e.name not in SKIP_DIRS and e.name not in SKIP_FILES],
        key=lambda e: (not e.is_dir(), e.name.lower()),
    )

    for i, entry in enumerate(entries):
        last = i == len(entries) - 1
        connector = "└── " if last else "├── "

        if entry.is_dir():
            file_count, total_size = count_files(entry)
            print(f"{prefix}{connector}{entry.name}/  "
                  f"[{file_count} files, {human_size(total_size)}]")
            extension = "    " if last else "│   "
            walk(entry, prefix + extension, last)
        else:
            try:
                size = human_size(entry.stat().st_size)
            except OSError:
                size = "?"
            print(f"{prefix}{connector}{entry.name}  ({size})")


def main():
    root = Path(".")
    print(f"\n{'='*70}")
    print(f"Sahayak — Project Tree")
    print(f"Root: {root.resolve()}")
    print(f"{'='*70}\n")
    print(f"{root.name}/")
    walk(root)

    # Summary
    total_files, total_size = count_files(root)
    print(f"\n{'='*70}")
    print(f"Total: {total_files} files, {human_size(total_size)}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()