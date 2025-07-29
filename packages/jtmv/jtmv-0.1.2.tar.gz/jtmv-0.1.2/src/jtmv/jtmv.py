import argparse
import subprocess
import sys
from pathlib import Path
import jupytext
from jupytext.paired_paths import paired_paths


def is_git_tracked(path: Path) -> bool:
    """Check if path is tracked in git."""
    try:
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Rename jupytext paired files while maintaining sync"
    )
    parser.add_argument(
        "source", help="Source filename with extension (e.g., difficulty_estimation.py)"
    )
    parser.add_argument(
        "dest", help="Destination filename with extension (e.g., flows.py)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually rename files, just print the commands",
    )
    args = parser.parse_args()

    source = Path(args.source)
    dest = Path(args.dest)

    # Get all synced formats from jupytext
    notebook = jupytext.read(source)
    synced_formats = notebook.metadata.get("jupytext", {}).get("formats")

    if not synced_formats:
        sys.exit(f"Error: {source} is not tracked by jupytext")

    jupy_paired_paths = paired_paths(
        str(source), {"extension": source.suffix}, synced_formats
    )

    # Rename each format
    for jupy_paired_path, jupy_fmt in jupy_paired_paths:
        ext = jupy_fmt.get("extension")
        src_file = Path(jupy_paired_path)
        dst_file = dest.with_suffix(ext)

        if src_file.exists():
            if is_git_tracked(src_file):
                if args.dry_run:
                    print(f"git mv {src_file} {dst_file}")
                else:
                    subprocess.run(['git', 'mv', str(src_file), str(dst_file)], check=True)
            else:
                if args.dry_run:
                    print(f"mv {src_file} {dst_file}")
                else:
                    src_file.rename(dst_file)


if __name__ == "__main__":
    main()
