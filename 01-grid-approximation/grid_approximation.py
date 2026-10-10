# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo>=0.25",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "polars>=1.33",
# ]
#
# [tool.uv]
# exclude-newer = "2026-10-10T00:00:00Z"
#
# [tool.bb]
# target = "wasm"
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import polars as pl

    return mo, np, pl, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Grid approximation

    *Placeholder lesson.* We estimate the average knee flexion angle at
    initial contact, $\mu$, from a few simulated walking trials. Each trial is
    modelled as $y_i \sim \mathcal{N}(\mu, 4^\circ)$, and we evaluate the
    posterior for $\mu$ on a grid of candidate values.
    """)
    return


@app.cell
def _(mo, pl):
    data_path = mo.notebook_location() / "data" / "knee_flexion.csv"
    angles = pl.read_csv(str(data_path))["angle_deg"].to_numpy()
    return (angles,)


@app.cell
def _(angles, mo):
    prior_mean = mo.ui.slider(0, 40, value=10, step=1, label="Prior mean (°)")
    prior_sd = mo.ui.slider(1, 20, value=5, step=1, label="Prior SD (°)")
    n_obs = mo.ui.slider(0, len(angles), value=3, step=1, label="Trials observed")
    mo.vstack([prior_mean, prior_sd, n_obs])
    return n_obs, prior_mean, prior_sd


@app.cell
def _(angles, n_obs, np, prior_mean, prior_sd):
    sigma = 4.0  # measurement SD (degrees), assumed known
    grid = np.linspace(-10, 50, 601)
    y = angles[: n_obs.value]

    log_prior = -0.5 * ((grid - prior_mean.value) / prior_sd.value) ** 2
    log_lik = -0.5 * (((y[:, None] - grid[None, :]) / sigma) ** 2).sum(axis=0)
    log_post = log_prior + log_lik

    prior = np.exp(log_prior - log_prior.max())
    prior /= np.trapezoid(prior, grid)
    posterior = np.exp(log_post - log_post.max())
    posterior /= np.trapezoid(posterior, grid)
    return grid, posterior, prior, y


@app.cell
def _(grid, plt, posterior, prior, y):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(grid, prior, linestyle="--", color="0.5", label="Prior")
    ax.plot(grid, posterior, color="#0f6e74", linewidth=2, label="Posterior")
    ax.plot(y, [0] * len(y), "|", color="#b5480f", markersize=18, label="Trials")
    ax.set_xlabel("Mean knee flexion at initial contact, μ (°)")
    ax.set_yticks([])
    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    ax
    return


if __name__ == "__main__":
    app.run()
