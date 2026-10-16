"""Find the book's marimo lesson notebooks and read their PEP 723 metadata."""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTER_GLOB = "[0-9][0-9]-*"
DATA_DIR = ROOT / "data"  # shared datasets, one folder each
TARGETS = {"wasm", "local"}

# Reference regex from PEP 723
_METADATA = re.compile(
    r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"
)


@dataclass(frozen=True)
class Notebook:
    path: Path
    metadata: dict

    @property
    def chapter(self) -> str:
        return self.path.parent.name

    @property
    def target(self) -> str:
        return self.metadata.get("tool", {}).get("bb", {}).get("target", "")

    @property
    def data(self) -> list[str]:
        """Shared datasets (folders in `data/`) listed under [tool.bb] data."""
        return self.metadata.get("tool", {}).get("bb", {}).get("data", [])

    @property
    def needs_conda(self) -> bool:
        return "pixi" in self.metadata.get("tool", {})


def read_metadata(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    blocks = [m for m in _METADATA.finditer(text) if m.group("type") == "script"]
    if len(blocks) != 1:
        raise ValueError(
            f"{path}: expected one `# /// script` block, found {len(blocks)}"
        )
    content = "".join(
        line[2:] if line.startswith("# ") else line[1:]
        for line in blocks[0].group("content").splitlines(keepends=True)
    )
    return tomllib.loads(content)


def find_notebooks(root: Path = ROOT) -> list[Notebook]:
    notebooks = []
    for path in sorted(root.glob(f"{CHAPTER_GLOB}/*.py")):
        if "marimo.App(" not in path.read_text(encoding="utf-8"):
            continue
        notebook = Notebook(path, read_metadata(path))
        if notebook.target not in TARGETS:
            raise ValueError(
                f"{path}: set [tool.bb] target to one of {sorted(TARGETS)} "
                "in the script header"
            )
        missing = [name for name in notebook.data if not (DATA_DIR / name).is_dir()]
        if missing:
            raise ValueError(
                f"{path}: [tool.bb] data lists {missing}, but there is no such "
                f"folder in {DATA_DIR.relative_to(root).as_posix()}/"
            )
        notebooks.append(notebook)
    return notebooks


if __name__ == "__main__":
    for nb in find_notebooks():
        print(f"{nb.target:6} {nb.path.relative_to(ROOT).as_posix()}")
