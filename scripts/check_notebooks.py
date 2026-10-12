"""Run every lesson notebook standalone from its own PEP 723 header.

Catches drift between a notebook's declared dependencies and what it actually
imports. PyPI-only notebooks run with `uv run --script`; notebooks that
declare conda packages under [tool.pixi] run with `pixi run --script`.
Notebooks with committed results load them instead of refitting, so this is
quick.

Usage: python scripts/check_notebooks.py [NOTEBOOK ...]
"""

import subprocess
import sys
from pathlib import Path

from notebooks import ROOT, find_notebooks


def main(selected: list[str]) -> int:
    notebooks = find_notebooks()
    if selected:
        wanted = {Path(p).resolve() for p in selected}
        notebooks = [nb for nb in notebooks if nb.path in wanted]

    failed = []
    for nb in notebooks:
        rel = nb.path.relative_to(ROOT).as_posix()
        if nb.needs_conda:
            cmd = ["pixi", "run", "--script", str(nb.path)]
        else:
            cmd = ["uv", "run", "--script", str(nb.path)]
        print(f"--- {rel}: {' '.join(cmd[:3])}", flush=True)
        result = subprocess.run(cmd, check=False, cwd=nb.path.parent)
        if result.returncode != 0:
            failed.append(rel)

    if failed:
        print("\nFailed standalone runs:\n  " + "\n  ".join(failed))
        return 1
    print(f"\nAll {len(notebooks)} notebooks ran standalone.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
