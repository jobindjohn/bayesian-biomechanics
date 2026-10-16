# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo>=0.25",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "polars>=1.33",
#     "scipy>=1.14",
# ]
#
# [tool.uv]
# exclude-newer = "2026-10-10T00:00:00Z"
#
# [tool.bb]
# target = "wasm"
# data = ["Wood-1969"]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import polars as pl
    from scipy import stats

    return Path, mo, np, pl, plt, stats


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # How stiff is skull bone?

    *Draft.* Young's modulus $E$ tells us how much a material resists being
    stretched. Before looking at any measurements, what do you believe $E$ is for
    the cortical bone of the human skull? In this lesson we write that belief down
    as a **prior**, then update it one tensile test at a time.

    The tests come from Wood (1969): coupons of outer-table cranial bone pulled
    to failure. We use the 18 slowest tests (strain rate 0.0015–0.02 /s) because
    bone gets stiffer the faster it is loaded.
    """)
    return


@app.cell(hide_code=True)
def _(Path, mo, pl):
    DATA_URL = (
        "https://raw.githubusercontent.com/jobindjohn/bayesian-biomechanics/main/data"
    )

    def read_data(dataset, file):
        """Read a CSV from the repo's data/ folder, or from GitHub if not on disk.

        In the browser the notebook has no folder of its own, so the data come
        from GitHub; Pyodide's polars cannot fetch URLs, so we fetch the text.
        """
        local = Path(str(mo.notebook_location())).parent / "data" / dataset / file
        if local.exists():
            return pl.read_csv(local)
        url = f"{DATA_URL}/{dataset}/{file}"
        try:
            from pyodide.http import open_url
        except ImportError:  # e.g. a downloaded copy of the notebook
            return pl.read_csv(url)
        return pl.read_csv(open_url(url).read().encode())

    tests = read_data("Wood-1969", "skull_tension_tests.csv")
    slow = tests.filter(
        pl.col("layer") == "outer table",
        pl.col("test_type") == "failure",
        pl.col("strain_rate_per_s") < 0.05,
        pl.col("modulus_gpa").is_not_null(),
    ).sort("sheet_row")
    modulus = slow["modulus_gpa"].to_numpy()
    slow.select("test_id", "donor_id", "strain_rate_per_s", "modulus_gpa")
    return (modulus,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Updating the mean, with the scatter known

    To start simple we assume we already know how much one test differs from
    the next: a standard deviation of $\sigma = 1.5$ GPa (*placeholder value*).
    Only the mean modulus $\mu$ is unknown:

    $$
    E_i \sim \mathcal{N}(\mu, \sigma), \qquad \mu \sim \mathcal{N}(\mu_0, \tau_0).
    $$

    With a normal prior and a normal likelihood, the posterior for $\mu$ is
    normal as well, so each new test updates two numbers: a mean and a standard
    deviation.
    """)
    return


@app.cell(hide_code=True)
def _(mo, modulus):
    sigma_known = 1.5  # GPa, placeholder
    prior_mean = mo.ui.slider(5, 25, value=15, step=0.5, label="Prior mean μ₀ (GPa)")
    prior_sd = mo.ui.slider(0.5, 10, value=5, step=0.5, label="Prior SD τ₀ (GPa)")
    n_tests = mo.ui.slider(0, len(modulus), value=0, step=1, label="Tests observed")
    shuffle = mo.ui.button(
        value=0, on_click=lambda count: count + 1, label="Shuffle test order"
    )
    mo.vstack([prior_mean, prior_sd, n_tests, shuffle])
    return n_tests, prior_mean, prior_sd, shuffle, sigma_known


@app.cell(hide_code=True)
def _(modulus, n_tests, np, prior_mean, prior_sd, shuffle, sigma_known):
    def update_normal(mu0, tau0, y, sigma):
        """Posterior mean and SD of a normal mean with known sigma."""
        precision = 1 / tau0**2 + len(y) / sigma**2
        mean = (mu0 / tau0**2 + y.sum() / sigma**2) / precision
        return mean, precision**-0.5

    # Click count 0 is the order in Wood's table; each click is a fixed seed
    order = (
        np.arange(len(modulus))
        if shuffle.value == 0
        else np.random.default_rng(shuffle.value).permutation(len(modulus))
    )
    seen = modulus[order][: n_tests.value]
    post_mean, post_sd = update_normal(
        prior_mean.value, prior_sd.value, seen, sigma_known
    )
    return order, post_mean, post_sd, seen, update_normal


@app.cell(hide_code=True)
def _(np, plt, post_mean, post_sd, prior_mean, prior_sd, seen, stats):
    _grid = np.linspace(5, 25, 801)
    _fig, _ax = plt.subplots(figsize=(7, 3))
    _ax.plot(
        _grid,
        stats.norm.pdf(_grid, prior_mean.value, prior_sd.value),
        color="#b5480f",
        lw=2,
        ls="--",
        label="Prior",
    )
    _ax.plot(
        _grid,
        stats.norm.pdf(_grid, post_mean, post_sd),
        color="#0f6e74",
        lw=2.5,
        label=f"Posterior after {len(seen)} tests",
    )
    _ax.plot(
        seen,
        np.zeros_like(seen),
        "|",
        color="#1f2328",
        ms=18,
        mew=1.5,
        label="Tests seen",
    )
    _ax.set_xlabel("Mean Young's modulus μ (GPa)")
    _ax.set_yticks([])
    _ax.spines[["left", "top", "right"]].set_visible(False)
    _ax.legend(frameon=False, loc="upper left")
    _ax.set_title(
        f"μ = {post_mean:.1f} ± {post_sd:.2f} GPa (posterior mean ± SD)",
        loc="left",
        fontsize=10,
    )
    _fig.tight_layout()
    _ax
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Does the order of the tests matter?

    Each update uses the previous posterior as the next prior. Shuffle the tests
    above: the path the posterior takes changes, but where it ends after all 18
    tests does not. The final posterior depends only on the data and the prior,
    not on the order in which we saw them.
    """)
    return


@app.cell
def _(
    modulus,
    n_tests,
    np,
    order,
    plt,
    prior_mean,
    prior_sd,
    sigma_known,
    update_normal,
):
    _k = np.arange(len(modulus) + 1)
    _fig, _ax = plt.subplots(figsize=(7, 3))
    for _idx, _colour, _label in [
        (np.arange(len(modulus)), "#1f2328", "Table order"),
        (order, "#0f6e74", "Current order"),
    ]:
        _m, _s = np.array(
            [
                update_normal(
                    prior_mean.value, prior_sd.value, modulus[_idx][:k], sigma_known
                )
                for k in _k
            ]
        ).T
        _ax.fill_between(_k, _m - 2 * _s, _m + 2 * _s, color=_colour, alpha=0.15)
        _ax.plot(_k, _m, color=_colour, lw=2, label=_label)
    _ax.axvline(n_tests.value, color="#b5480f", lw=1, ls=":")
    _ax.set_xlabel("Tests observed")
    _ax.set_ylabel("μ (GPa), mean ± 2 SD")
    _ax.spines[["top", "right"]].set_visible(False)
    _ax.legend(frameon=False)
    _fig.tight_layout()
    _ax
    return


if __name__ == "__main__":
    app.run()
