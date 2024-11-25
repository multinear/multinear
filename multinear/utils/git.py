from pathlib import Path
import subprocess
from typing import Optional


def get_git_revision(folder: Path) -> Optional[str]:
    """
    Check if folder is a git repository and return current revision hash.
    Returns None if not a git repo or if git command fails.
    """
    git_dir = folder / ".git"
    if not git_dir.is_dir():
        return None
        
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=folder,
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception as e:
        print(f"Error fetching git revision: {e}")
        return None
