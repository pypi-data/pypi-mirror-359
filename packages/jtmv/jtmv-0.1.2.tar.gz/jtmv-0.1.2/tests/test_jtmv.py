import subprocess
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch
from tempfile import mkdtemp

from jtmv.jtmv import main


def copy_test_files(dst_dir):
    """Copy test files from tests/data to temp directory."""
    dst_dir = Path(dst_dir)

    data_dir = Path(__file__).parent / "data"
    base_name = "test_notebook"

    # Copy all paired files
    ipynb_src = data_dir / f"{base_name}.ipynb"
    py_src = data_dir / f"{base_name}.py"
    md_src = data_dir / f"{base_name}.md"

    ipynb_dst = dst_dir / f"{base_name}.ipynb"
    py_dst = dst_dir / f"{base_name}.py"
    md_dst = dst_dir / f"{base_name}.md"

    shutil.copy2(ipynb_src, ipynb_dst)
    shutil.copy2(py_src, py_dst)
    shutil.copy2(md_src, md_dst)

    return ipynb_dst, py_dst, md_dst


def test_rename_paired_files():
    """Test renaming a file with 2 other paired files."""
    dst_dir = Path(mkdtemp())

    # Copy test files
    ipynb_path, py_path, md_path = copy_test_files(dst_dir)

    # Verify files exist
    assert ipynb_path.exists()
    assert py_path.exists()
    assert md_path.exists()

    with patch(
        "sys.argv",
        ["jtmv", str(ipynb_path), str(dst_dir / "renamed_notebook.ipynb")],
    ):
        main()

    # Check that files were renamed
    new_ipynb = dst_dir / "renamed_notebook.ipynb"
    new_py = dst_dir / "renamed_notebook.py"
    new_md = dst_dir / "renamed_notebook.md"

    assert new_ipynb.exists()
    assert new_py.exists()
    assert new_md.exists()
    assert not ipynb_path.exists()
    assert not py_path.exists()
    assert not md_path.exists()
