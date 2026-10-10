"""Fail if a committed data or results file exceeds the size cap.

Larger datasets belong on Zenodo and are downloaded on first use.
"""

import subprocess
import sys

from notebooks import CHAPTER_GLOB, ROOT

MAX_BYTES = 5 * 1024 * 1024


def main() -> int:
    files = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    ).stdout.splitlines()
    too_big = []
    for name in files:
        path = ROOT / name
        in_chapter = path.parent.parent.match(CHAPTER_GLOB)
        if in_chapter and path.parent.name in {"data", "results"} and path.exists():
            size = path.stat().st_size
            if size > MAX_BYTES:
                too_big.append(f"{name} ({size / 1024**2:.1f} MB)")
    if too_big:
        print(f"Files over {MAX_BYTES // 1024**2} MB (move them to Zenodo):")
        print("  " + "\n  ".join(too_big))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
