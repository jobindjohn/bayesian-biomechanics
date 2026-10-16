"""Export lesson notebooks into the rendered site (runs as a Quarto post-render).

For each notebook in a chapter folder, writes to `<site>/<chapter>/`:

- `<stem>.py`: the notebook itself, for download
- `<stem>/index.html`: the exported notebook, embedded in the chapter page
  - target "wasm": interactive WebAssembly notebook in run mode (cells run on
    load, code shown read-only) as a single small HTML file; marimo's
    frontend loads from jsDelivr, pinned to the installed marimo version.
    No data is copied: in a single-file export `mo.notebook_location()` is a
    `blob:` URL, so lessons read data from GitHub in the browser
  - target "local": static HTML with outputs, from running the notebook
    (which loads its committed results)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from notebooks import ROOT, find_notebooks


def export(nb, site: Path) -> None:
    chapter_out = site / nb.chapter
    out_dir = chapter_out / nb.path.stem
    chapter_out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(nb.path, chapter_out / nb.path.name)

    if nb.target == "wasm":
        cmd = ["export", "html-wasm", str(nb.path), "-o", str(out_dir / "index.html")]
        cmd += ["--mode", "run", "--show-code", "--single-file"]
        cmd += ["--no-sandbox", "--force"]
    else:
        cmd = ["export", "html", str(nb.path), "-o", str(out_dir / "index.html")]
        cmd += ["--no-sandbox", "--force"]

    print(f"Exporting {nb.path.relative_to(ROOT).as_posix()} ({nb.target})")
    subprocess.run([sys.executable, "-m", "marimo", *cmd], check=True, cwd=ROOT)


def main() -> None:
    site = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", ROOT / "_site"))
    if not site.is_absolute():
        site = ROOT / site
    for nb in find_notebooks():
        export(nb, site)


if __name__ == "__main__":
    main()
