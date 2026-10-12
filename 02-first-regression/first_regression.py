# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "arviz>=1.3",
#     "bambi>=0.21",
#     "h5netcdf[h5py]>=1.4",
#     "marimo>=0.25",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "nutpie>=0.16",
#     "polars>=2.0",
#     "pymc>=6.3",
# ]
#
# [tool.uv]
# exclude-newer = "2026-10-10T00:00:00Z"
#
# [tool.bb]
# target = "local"
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import os

    import arviz as az
    import bambi as bmb
    import marimo as mo
    import numpy as np
    import polars as pl

    return az, bmb, mo, np, os, pl


@app.cell
def _(mo):
    mo.md(r"""
    # A first regression model

    *Placeholder lesson.* We relate stride length to walking speed with a
    linear regression fitted in [Bambi](https://bambinos.github.io/bambi/),
    using simulated data.
    """)
    return


@app.cell
def _(mo, os):
    # Saved results are loaded when they exist. To fit the model again, run
    # `pixi run refit <this file>`, set BB_REFIT=1, or pass `--refit`.
    refit = os.environ.get("BB_REFIT") == "1" or "refit" in mo.cli_args()
    results_path = mo.notebook_dir() / "results" / "first_regression.nc"
    return refit, results_path


@app.cell
def _(np, pl):
    rng = np.random.default_rng(2026)
    speed = rng.uniform(0.8, 1.8, size=40)  # m/s
    data = pl.DataFrame(
        {
            "speed": speed,
            "stride_length": 0.4 + 0.75 * speed + rng.normal(0, 0.06, size=40),
        }
    )
    data
    return (data,)


@app.cell
def _(az, bmb, data, refit, results_path):
    model = bmb.Model("stride_length ~ speed", data.to_pandas())

    if results_path.exists() and not refit:
        idata = az.from_netcdf(results_path).load()
    else:
        idata = model.fit(inference_method="nutpie", random_seed=2026)
        results_path.parent.mkdir(exist_ok=True)
        compress = {
            f"/{group}": {
                name: {"zlib": True, "complevel": 9}
                for name, var in idata[group].data_vars.items()
                if var.dtype.kind in "biuf"
            }
            for group in idata.children
        }
        idata.to_netcdf(results_path, engine="h5netcdf", encoding=compress)
    return (idata,)


@app.cell
def _(az, idata):
    az.summary(idata)
    return


@app.cell
def _(az, idata):
    az.plot_dist(idata).viz["figure"].item()
    return


if __name__ == "__main__":
    app.run()
