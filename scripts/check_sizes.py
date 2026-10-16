"""Fail if a committed data or results file exceeds the size cap.

Covers chapter `data/` and `results/` folders and the shared `data/` folder.

Larger datasets belong on Zenodo and are downloaded on first use.
"""

import subprocess
import sys

from notebooks import CHAPTER_GLOB, DATA_DIR, ROOT

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
        chapter_file = in_chapter and path.parent.name in {"data", "results"}
        if (chapter_file or path.is_relative_to(DATA_DIR)) and path.exists():
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
