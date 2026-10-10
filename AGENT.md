# AGENT.md

Guidance for AI agents (and humans) working in this repository.

## What this is

*Bayesian Biomechanics*: an interactive textbook teaching Bayesian data
analysis to biomechanics researchers, including readers new to Python.

- **Quarto book** (`_quarto.yml`), published to GitHub Pages at
  <https://jobindjohn.github.io/bayesian-biomechanics/>.
- **marimo notebooks** for lessons, either running in the browser (WASM via
  Pyodide) or locally with PyMC/Bambi.
- **pixi** manages every environment, task and lockfile.

## Working with the maintainer

- **Do not assume decisions.** The maintainer wants to be consulted on every
  design choice (tools, versions, layout, content, conventions). Propose a
  recommendation with trade-offs, then ask. Settled decisions are listed below.
  Do not reopen them unless something forces it, and say so when it does.
- Ask before anything outward-facing: pushing, opening or merging PRs,
  publishing, or changing GitHub settings.
- Never bypass the pre-commit hook (`--no-verify`). Fix the cause instead.
- Work on a branch and open a PR into `main`. A push to `main` deploys the site.

## Layout

```
_quarto.yml            book config (chapters, appendices, post-render hook)
_brand.yml             colours/fonts, light + dark (WCAG AA)
index.qmd              preface
NN-chapter-name/       one folder per chapter
  index.qmd            chapter text
  <lesson>.py          marimo notebook(s)
  data/                small input data (README.md says where it came from)
  results/             committed model results (.nc) for local lessons
appendix-setup/        "Running the lessons locally" appendix
references.bib, apa.csl
_extensions/
  marimo-team/marimo/  vendored quarto-marimo extension (v0.5.0); don't edit
  lesson/              our `{{< lesson file.py >}}` shortcode (Lua)
scripts/
  notebooks.py         finds lesson notebooks, parses PEP 723 headers
  export_notebooks.py  Quarto post-render: exports notebooks into _site/
  check_notebooks.py   runs each notebook standalone from its header
  check_sizes.py       5 MB cap on chapter data/ and results/ files
  install_hooks.py     installs the git pre-commit hook
.github/workflows/     check.yml (PRs, weekly), publish.yml (push to main)
```

Add new chapters to `book.chapters` in `_quarto.yml`. Chapter folders must
match `[0-9][0-9]-*`, because scripts and ruff/typos rules rely on that
pattern.

## Commands

| Command | Purpose |
| --- | --- |
| `pixi run lesson <nb.py>` | Open a lesson in the marimo editor |
| `pixi run refit <nb.py>` | Refit a local lesson's models and overwrite `results/` |
| `pixi run -e dev check` | ruff lint + format check, `marimo check --strict`, typos, size cap |
| `pixi run -e dev format` | ruff format |
| `pixi run -e dev check-notebooks [nb.py ...]` | Run notebooks standalone from their headers (uv) |
| `pixi run -e dev install-hooks` | Install or refresh the pre-commit hook |
| `pixi run -e docs render` | Render to `_site/` (post-render exports notebooks) |
| `pixi run -e docs preview` | Live preview |
| `pixi run -e docs links` | Internal link check; `links-all` also checks external links |

Environments (one solve group, so versions match across them):
`default` = lesson libraries (what learners install), `dev` = default plus
ruff, typos, lychee and uv, `docs` = dev plus Quarto.

## Settled decisions

- **Dependencies: PyPI first.** Use conda (conda-forge) only for things not
  on PyPI. Currently that is Python itself, `graphviz` (the binary), `lychee`
  and `quarto`.
- **Python** `>=3.12,<3.15`. pixi picks the newest version that solves
  (currently 3.14). The upper bound is needed: PyTensor caps it, and marimo's
  dependency `loro` has no 3.15 wheels.
- **Quarto 1.9.x from conda-forge**, pinned `>=1.9.38,<1.10`, because
  conda-forge has no 1.10 yet. Bump it when conda-forge catches up.
- **Platforms:** win-64, linux-64, osx-arm64, osx-64.
- **Sampler: nutpie**, for both PyMC (`nuts_sampler="nutpie"`) and Bambi
  (`inference_method="nutpie"`). It avoids needing a C compiler; the
  "g++ not available" warning is expected and harmless.
- **Libraries:** ArviZ 1.x with the matplotlib backend for plots, plotnine
  for any other plots, **polars** for data frames. Bambi needs pandas, so
  convert with `.to_pandas()` at that point only.
- **Prose:** British English (checked by typos) and APA 7 citations from
  `references.bib`.
- **Licences:** text and figures CC BY 4.0 (`LICENSE-CONTENT`), code MIT
  (`LICENSE`).
- **Data:** simulated, public and lab data are all allowed. Files are at most
  5 MB each in git; larger ones go on Zenodo, downloaded with a checksum.
  Every `data/` folder has a README.md stating where the data came from and
  its licence. Lab data needs ethics/consent clearance before it is released.
- **Results:** models are fitted locally and results committed; CI never
  refits.
- **Brand:** a project-specific `_brand.yml` (teal/orange, Source Sans 3,
  Source Serif 4, JetBrains Mono via Bunny Fonts). It is a proposal awaiting
  the maintainer's review.

## Lesson notebooks

Each notebook's **PEP 723 header is the source of truth** for its
dependencies. The repo's `pixi.toml` must be a superset, so add new packages
to both.

```python
# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo>=0.25",
#     "numpy>=2.0",
# ]
#
# [tool.uv]
# exclude-newer = "2026-10-10T00:00:00Z"   # bump deliberately
#
# [tool.bb]
# target = "wasm"                           # or "local"
# ///
```

- Use lower bounds plus `exclude-newer`. Do not pin exact versions.
- If a package is only on conda, put it under `[tool.pixi.dependencies]` in
  the header. `check_notebooks.py` then runs that notebook with
  `pixi run --script` instead of uv.
- `[tool.bb] target` is required; `scripts/notebooks.py` raises an error
  without it.

### `target = "wasm"` (runs in the browser)

- Pyodide only: numpy, scipy, matplotlib, polars and similar. **No PyMC,
  PyTensor or Bambi.** Check that a package exists in Pyodide (marimo 0.25
  uses Pyodide v314.0.0, with Python 3.14) before using it.
- Pyodide's polars is **1.33**, so WASM headers use `polars>=1.33`, not 2.x.
- Read data with `mo.notebook_location() / "data" / "file.csv"`. The export
  copies the chapter's `data/` folder next to the exported page, so the same
  code works locally and in the browser.
- These are exported in **edit** mode as a single HTML file
  (`--single-file`). marimo's frontend loads from jsDelivr, pinned to the
  installed marimo version; Pyodide comes from the same CDN.

### `target = "local"` (PyMC/Bambi)

Use the load-or-fit pattern from `02-first-regression/first_regression.py`:

```python
refit = os.environ.get("BB_REFIT") == "1" or "refit" in mo.cli_args()
results_path = mo.notebook_dir() / "results" / "<name>.nc"
if results_path.exists() and not refit:
    idata = az.from_netcdf(results_path).load()
else:
    idata = model.fit(inference_method="nutpie", random_seed=...)
    # save compressed: zlib level 9 on numeric variables, engine="h5netcdf"
```

- `pixi run refit <nb.py>`, `marimo edit nb.py -- --refit` and
  `python nb.py --refit` all force a refit.
- NetCDF needs `h5netcdf[h5py]`; plain `h5netcdf` does not install h5py.
- ArviZ 1.x returns an `xarray.DataTree`. A figure from arviz-plots is
  `az.plot_dist(idata).viz["figure"].item()`.
- The site shows a static export (`marimo export html`) that runs the
  notebook, so committed results keep the build fast.
- If a WASM lesson needs posterior draws, export a small Parquet table
  alongside the `.nc`, because Pyodide cannot run PyMC.

### Notebook style

- Each cell's last expression is its output, and marimo writes a trailing
  `return`. ruff's `B018` and `PLR1711` are ignored for chapter notebooks
  for this reason.
- Use fixed random seeds. Mark placeholder content as placeholder.
- Use `random_seed` for samplers and `np.random.default_rng(seed)` for
  simulated data.

### Embedding in a chapter

```markdown
{{< lesson my_lesson.py >}}            <!-- optional: height=60vh -->
```

The shortcode reads the target from the header and renders an iframe plus
"Open full page", "Download notebook" and "Open in molab" links. The molab
link uses `book.repo-url` and `repo-branch`, and adds `/wasm` for WASM
lessons.

For a small inline widget inside the prose (an "island"), give the chapter
these front-matter settings and use `python {.marimo}` cells:

```yaml
---
engine: marimo
external-env: true   # use the pixi docs env, not uv
---
```

## Build and deploy

- `quarto render` runs `scripts/export_notebooks.py` as a post-render step.
  For each notebook it writes `_site/<chapter>/<stem>.py` (the download) and
  `_site/<chapter>/<stem>/index.html` (the export).
- Exports pass `--no-sandbox`. Without it, marimo asks interactively whether
  to use a sandbox, which hangs or aborts in CI.
- There is no `_freeze/` directory: the marimo engine doesn't use freeze, and
  other pages have no code.
- **CI (`check.yml`):**
  - On PRs: lint and checks, standalone notebooks on Linux, render, internal
    links.
  - Weekly (Monday 05:00 UTC): notebooks on Linux, Windows and macOS, plus
    external links.
- **Publish (`publish.yml`):** on push to `main`, runs
  `quarto publish gh-pages`. The `gh-pages` branch already exists, and Pages
  serves from it.
- Actions are **pinned to commit SHAs** with the version in a comment.
  Dependabot proposes updates monthly. Keep SHA pins when editing workflows.
- `pixi.lock` is committed, and CI uses `locked: true`. Run `pixi lock` after
  editing `pixi.toml`, and commit the lockfile.

## Pitfalls

- **Windows consoles:** `PYTHONUTF8=1` is set in the pixi activation because
  Bambi's progress bar otherwise crashes on cp1252.
- **typos:** British spelling applies to `.qmd`/`.md` prose only. Fenced and
  inline code are skipped, and `.py` files use the default locale, so API
  names like `color=` are fine. Add genuine abbreviations to
  `[default.extend-words]` in `_typos.toml`.
- **Pre-commit hook** (`.git/hooks/pre-commit`) runs `pixi run -e dev check`.
  It exits early where there is no `pixi.toml`, such as on `gh-pages`.
- **`pixi run --script nb.py` runs a notebook headlessly** and ignores any
  command after it. To edit a single notebook standalone, use
  `uvx marimo edit --sandbox nb.py`.
- **quarto-marimo** is a preview feature. If islands break after a marimo or
  Quarto upgrade, check the extension version first
  (`quarto add marimo-team/quarto-marimo`). The extension's downloaded
  release assets are committed under `_extensions/`.
- **`SSL_CERT_DIR` warnings** from pixi on the maintainer's machine come from
  a local Anaconda environment variable and are harmless.
- **GitHub rate limits** (HTTP 429) sometimes fail `setup-pixi` in CI.
  Re-run the failed job.
