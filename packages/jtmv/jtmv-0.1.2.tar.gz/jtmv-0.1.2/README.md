# `jtmv`

Command-line tool for renaming all jupytext paired files while maintaining their synchronization.

## Purpose

Jupytext allows two-way sync of notebook content between files with different formats (`.ipynb`, `.py`, `.md`, etc.). Users have two options to rename these files:

1. Rename _one_ file, regenerate all formats with `juptext sync`, and then delete all files with the old name.
2. Rename _all_ files and restablish synchronization with `jupyext set-formats`. 

This tool handles the renaming of _all_ paired formats in one step. 

## Installation

```bash
pip install jtmv
```

## Usage

```sh
jtmv source dest [--dry-run]
```

### Examples

```sh
# Rename a jupytext paired file
jtmv workflow.py flow.py

# Dry run to see what would happen
jtmv utility.md utils.md --dry-run
```

### Options

- `source`: Source filename with extension (e.g., `workflow.py`)
- `dest`: Destination filename with extension (e.g., `flow.py`)
- `--dry-run`: Do not actually rename files, just print the commands that would be executed

## How it works

1. **Detects paired formats**: Reads the jupytext metadata to find all synced formats
2. **Git-aware moves**: If files are tracked in git, uses `git mv` to preserve history

## License

MIT License - see LICENSE file for details.
