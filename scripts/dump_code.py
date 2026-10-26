"""Dump all project code into a single text file for review."""
from pathlib import Path

ROOT = Path(".")
OUTPUT = Path("PROJECT_CODE_DUMP.txt")

# Folders to ignore
IGNORE_DIRS = {"venv", "__pycache__", ".git", "chroma_db", ".cache", "data"}

def dump_dir(directory: Path, outfile):
    for path in sorted(directory.iterdir()):
        if path.is_dir():
            if path.name not in IGNORE_DIRS:
                dump_dir(path, outfile)
        elif path.suffix in [".py", ".yaml", ".yml", ".toml"]:
            outfile.write(f"\n\n{'='*80}\n")
            outfile.write(f"FILE: {path}\n")
            outfile.write(f"{'='*80}\n\n")
            try:
                content = path.read_text(encoding="utf-8")
                outfile.write(content)
            except Exception as e:
                outfile.write(f"Error reading file: {e}")

def main():
    print(f"Scanning project and writing to {OUTPUT}...")
    with open(OUTPUT, "w", encoding="utf-8") as outfile:
        dump_dir(ROOT, outfile)
    print(f"Done! You can open {OUTPUT} to read the code.")

if __name__ == "__main__":
    main()