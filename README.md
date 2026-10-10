# Bayesian Biomechanics

An interactive textbook on Bayesian data analysis for biomechanics, built with
[Quarto](https://quarto.org) and [marimo](https://marimo.io) notebooks and
published at <https://jobindjohn.github.io/bayesian-biomechanics/>.

## Setup

Install [pixi](https://pixi.prefix.dev), then:

```bash
pixi run -e dev install-hooks   # pre-commit hook: runs `pixi run -e dev check`
```

| Command | What it does |
| --- | --- |
| `pixi run lesson <notebook.py>` | Open a lesson in marimo |
| `pixi run refit <notebook.py>` | Refit a lesson's models and overwrite its saved results |
| `pixi run -e dev check` | ruff, `marimo check`, typos (British prose), data size cap |
| `pixi run -e dev check-notebooks` | Run every notebook standalone from its own header |
| `pixi run -e docs preview` | Live preview of the book |
| `pixi run -e docs render` | Build the site into `_site/` (also exports notebooks) |
| `pixi run -e docs links` | Check internal links (`links-all` includes external) |

## Layout

Each chapter is a folder (`NN-name/`) with its `index.qmd`, lesson
notebook(s), `data/` and `results/`. Add new chapters to `_quarto.yml`.

## Writing a lesson

A lesson is a marimo notebook in a chapter folder. Its PEP 723 header is the
source of truth for its dependencies, and says where it runs:

```python
# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = ["marimo>=0.25", "numpy>=2.0"]
#
# [tool.uv]
# exclude-newer = "2026-10-10T00:00:00Z"
#
# [tool.bb]
# target = "wasm"   # or "local" for PyMC/Bambi lessons
# ///
```

- **PyPI first.** Use conda (a `[tool.pixi.dependencies]` table in the
  header, and `[dependencies]` in `pixi.toml`) only for packages not on PyPI.
  Add new packages to `pixi.toml` too.
- **`wasm` lessons** run in the browser via Pyodide, so use only packages
  Pyodide supports (no PyMC). Read data with
  `mo.notebook_location() / "data" / ...`.
- **`local` lessons** load committed results from `results/` when present and
  fit otherwise (`BB_REFIT=1` or `--refit` forces a refit). The site shows a
  static export.
- Embed a lesson in its chapter with `{{< lesson notebook.py >}}`.
- Files in `data/` and `results/` must be at most 5 MB; put larger datasets
  on Zenodo.

## Licence

Text and figures: [CC BY 4.0](LICENSE-CONTENT). Code: [MIT](LICENSE).
