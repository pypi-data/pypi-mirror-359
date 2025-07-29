from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
import pandas as pd
from anndata import AnnData
from beartype import beartype
from jax import lax
from numpyro.contrib.funsor import config_enumerate
from numpyro.distributions import constraints
from numpyro.handlers import scale
from scipy import sparse

from .RNA_utils import sample_prior


@beartype
def prepare_model_input(
    adata_rna: AnnData,
    tf_list: List[str],
    n_cells_col: str = "n_cells",
    prior_time_col: Optional[str] = None,
    batch_annotation: Optional[str] = None,
    prior_path_col: Optional[str] = None,
    terminal_states: Optional[List[str]] = None,
    initial_states: Optional[List[str]] = None,
    cluster_key: Optional[str] = None,
    prior_timespan: Optional[float] = 40,
    N_steps: int = 100,
    grid_type: str = "linear",
    grid_param: float = 1.0,
    custom_grid_fn: Optional[Callable[[int], jnp.ndarray]] = None,
):
    """
    Prepare RNA input data for the model by extracting spliced and unspliced counts,
    computing transcription factor indices, and extracting cell metadata including batch
    information from adata_rna.obs if provided.  In addition, if you supply
    `cluster_key`, `initial_states`, and `terminal_states`, this will automatically
    build a “Prior Paths” (1-based) from those labels.  If you still want to pass
    in a numeric column (`prior_path_col`) you can; that takes priority if given.

    Parameters
    ----------
    adata_rna : AnnData
        AnnData object containing RNA expression data with 'spliced' and 'unspliced' layers.
    tf_list : List[str]
        List of transcription factor names.
    n_cells_col : str, optional
        Column name in `adata_rna.obs` representing the number of cells per metacell.
    prior_time_col : Optional[str], optional
        Column name in `adata_rna.obs` containing prior pseudotimes; if provided, used
        to center the prior over t_c (default: None).
    batch_annotation : Optional[str], optional
        Column name in `adata_rna.obs` that contains batch information; if provided,
        cells are assigned batch indices based on this column.
    prior_path_col : Optional[str], optional
        (legacy) Column name in `adata_rna.obs` that contains a hard‐coded 1‐based path index;
        missing/NaN entries become −1 (inference).  Takes priority over the
        automatic cluster‐based labeling described below.
    terminal_states : Optional[List[str]], optional
        If provided (and `cluster_key` is also given), defines a list of cluster names
        that should be mapped to terminal paths.  They will be assigned raw_prior = 1..P
        in the order you list them.
    initial_states : Optional[List[str]], optional
        If provided (and `cluster_key` is also given), defines a list of cluster names
        that should be mapped to raw_prior = 0 (which then becomes prior_path = −2
        internally, i.e. “initial state”).
    cluster_key : Optional[str], optional
        Column in `adata_rna.obs` whose values are compared against `initial_states`
        or `terminal_states` to build a “Prior Path” assignment.  This is only used
        if `prior_path_col` is None.
    prior_timespan : float, optional
        Used if prior_time_col is None (default span).  Otherwise recalculated from data.
    N_steps : int, optional
        Number of grid steps (default: 100).
    grid_type : str, optional
        “linear” or “linear_dt” (default: “linear”).
    grid_param : float, optional
        Parameter for “linear_dt” spacing (ignored if grid_type=“linear”).
    custom_grid_fn : Optional[Callable[[int], jnp.ndarray]], optional
        If you want to supply your own function to build `times_norm`.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
          - `data`: JAX array of shape (cells, genes, 2) with stacked unspliced and spliced counts.
          - `M_c`: JAX array of shape (cells, 1, 1) holding the per‐cell metacell size.
          - `obs2sample`: one‐hot encoding of batch indices (shape cells × n_batch).
          - `batch_index`: JAX array of shape (cells,) with batch indices.
          - `tf_indices`: JAX array of TF gene indices.
          - `total_num_cells`: int, number of cells.
          - `n_batch`: int, number of batches.
          - `prior_time`: JAX array of prior times or None.
          - `prior_timespan`: float, span of prior_time or default.
          - `prior_path`: JAX int array of shape (cells,) with −1 or 0‐based path ids;
              prior_path = −2 means “initial state,” prior_path ≥ 0 means fixed to path id.
          - `unknown_idx`: Python list of ints, indices of cells with unknown prior (prior_path < 0).
          - `unknown_count`: int, number of unknown cells.
          - `times_norm`, `dt_norm`, `T_limits`, `hidden_units`, `num_paths`
    """

    def _to_dense_f32(layer):
        if sparse.issparse(layer):
            # cast to float32 and densify in one go
            return layer.astype(np.float32).toarray()
        else:
            # if it’s already an ndarray, just ensure dtype
            return np.asarray(layer, dtype=np.float32)

    # ========== 1) STACK RAW DATA ==========
    spliced = _to_dense_f32(adata_rna.layers["spliced"])
    unspliced = _to_dense_f32(adata_rna.layers["unspliced"])
    data = jnp.array(np.stack([unspliced, spliced], axis=-1))

    # ========== 2) METACELL SIZES ==========
    M_c = jnp.array(
        np.expand_dims(np.expand_dims(adata_rna.obs[n_cells_col].to_numpy(), -1), -1),
        dtype=jnp.float32,
    )
    total_num_cells = int(data.shape[0])

    # ========== 3) PRIOR TIME ==========
    if prior_time_col is not None:
        prior_time = jnp.array(
            adata_rna.obs[prior_time_col].to_numpy(), dtype=jnp.float32
        )
        prior_timespan = float(prior_time.max() - prior_time.min())
    else:
        prior_time = None

    # ========== 4) BATCH INDEX ==========
    if batch_annotation is not None:
        batches = adata_rna.obs[batch_annotation].astype(str)
        uniq = batches.unique()
        mapping = {b: i for i, b in enumerate(uniq)}
        batch_index = jnp.array(batches.map(mapping).to_numpy(), dtype=jnp.int32)
    else:
        batch_index = jnp.zeros(total_num_cells, dtype=jnp.int32)
    n_batch = int(jnp.unique(batch_index).shape[0])
    obs2sample = jax.nn.one_hot(batch_index, num_classes=n_batch, dtype=jnp.float32)

    # ========== 5) TF INDICES ==========
    is_tf = np.isin(adata_rna.var_names, tf_list)
    tf_indices = jnp.array(np.where(is_tf)[0], dtype=jnp.int32)
    hidden_units = int(jnp.sqrt(int(np.sum(is_tf))))

    # ========== 6) PRIOR PATH (either from prior_path_col OR from clusters) ==========
    if prior_path_col is not None:
        raw_prior = adata_rna.obs[prior_path_col].to_numpy()
    else:
        if (
            (cluster_key is None)
            or (initial_states is None)
            or (terminal_states is None)
        ):
            raise ValueError(
                "Either supply `prior_path_col`, or else supply `cluster_key`, "
                "`initial_states`, and `terminal_states` so that the function can build a prior."
            )

        # Initialize everything to NA (we will treat NA as “unknown” => prior_path = −1).
        raw_prior = pd.Series(
            data=[pd.NA] * total_num_cells, index=adata_rna.obs.index, dtype="object"
        )

        # 6a) Assign initial states → raw_prior = 0
        init_mask = adata_rna.obs[cluster_key].isin(initial_states)
        raw_prior.loc[init_mask] = 0

        # 6b) Assign terminal states → raw_prior = 1,2,… in the order given
        for idx, term_label in enumerate(terminal_states, start=1):
            mask = adata_rna.obs[cluster_key] == term_label
            raw_prior.loc[mask] = idx
        raw_prior = raw_prior.to_numpy()

    valid_paths = [int(v) for v in raw_prior if pd.notna(v) and int(v) > 0]
    num_paths = max(valid_paths) if valid_paths else 1

    prior_path_np = np.full((total_num_cells,), -1, dtype=np.int32)  # −1 ⇒ unknown
    for i, v in enumerate(raw_prior):
        if pd.isna(v):
            # leave as −1
            continue
        v_int = int(v)
        if v_int == 0:
            # “initial state” → prior_path = −2
            prior_path_np[i] = -2
        else:
            # 1…P → fixed to path v−1
            prior_path_np[i] = v_int - 1

    prior_path = jnp.array(prior_path_np, dtype=jnp.int32)
    unknown_idx = [int(i) for i, p in enumerate(prior_path_np) if p < 0]
    known_idx = [i for i, p in enumerate(prior_path_np) if p >= 0]
    unknown_count = len(unknown_idx)
    known_count = len(known_idx)

    # ========== 7) BUILD TIMEGRID ==========
    if prior_time_col is None:
        T_min = -prior_timespan / 2.0
        T_max = +prior_timespan / 2.0
    else:
        T_min = prior_time.min() - prior_timespan / 6.0
        T_max = prior_time.max() + prior_timespan / 6.0

    if grid_type == "linear":
        times_norm = jnp.linspace(0.0, 1.0, N_steps + 1)
    else:
        raise ValueError(f"Unknown grid_type '{grid_type}'.")

    # ——— 8.0 observed terminal‐state proportions ———
    # only cells with prior_path >= 0 are true terminal states
    known_mask = prior_path_np >= 0
    # count how many cells fell into each of the P paths:
    obs_path_counts = np.bincount(
        prior_path_np[known_mask], minlength=num_paths
    ).astype(np.int32)         # shape (num_paths,)
    n_known = int(obs_path_counts.sum())

    # convert to float proportions if you like:
    obs_path_props = obs_path_counts.astype(np.float32) / float(n_known)

    return OrderedDict(
        [
            ("data", data),
            ("M_c", M_c),
            ("obs2sample", obs2sample),
            ("batch_index", batch_index),
            ("tf_indices", tf_indices),
            ("total_num_cells", total_num_cells),
            ("n_batch", n_batch),
            ("prior_time", prior_time),
            ("prior_timespan", prior_timespan),
            ("prior_path", prior_path),
            ("unknown_idx", jnp.array(unknown_idx)),
            ("unknown_count", unknown_count),
            ("known_idx", jnp.array(known_idx)),
            ("times_norm", times_norm),
            ("T_limits", (T_min, T_max)),
            ("hidden_units", hidden_units),
            ("num_paths", num_paths),
            ("obs_path_props", obs_path_props),

        ],
    )

def soft_clip(y, lower, upper, sharpness=1.0):
    y1 = lower + jax.nn.softplus(sharpness * (y - lower)) / sharpness
    y2 = upper - jax.nn.softplus(sharpness * (upper - y1)) / sharpness
    return y2

@jax.jit
def interpolate_solution(
    sol_grid: jnp.ndarray,
    times_grid: jnp.ndarray,
    T_c: jnp.ndarray,
) -> jnp.ndarray:
    """
    Linearly interpolate a precomputed solution grid at specified cell times.

    Parameters:
    - sol_grid (jnp.ndarray): Solution values on a regular time grid, shape (L, num_paths, num_genes, 3).
    - times_grid (jnp.ndarray): 1D array of time points corresponding to sol_grid, length L.
    - T_c (jnp.ndarray): Array of arbitrary times at which to interpolate, shape (num_cells,).

    Returns:
    - jnp.ndarray: Interpolated solution at each time in T_c, shape (num_cells, num_paths, num_genes, 3).
    """
    idx0 = jnp.searchsorted(times_grid, T_c, side="right") - 1
    idx0 = jnp.clip(idx0, 0, sol_grid.shape[0] - 2)
    t0 = times_grid[idx0]
    t1 = times_grid[idx0 + 1]
    sol0 = sol_grid[idx0]
    sol1 = sol_grid[idx0 + 1]
    w = ((T_c - t0) / (t1 - t0))[..., None, None, None]
    return sol0 * (1 - w) + sol1 * w

@jax.jit
def hill_regulation(p_tf: jnp.ndarray, params: dict[str, jnp.ndarray]) -> jnp.ndarray:
    """
    Interpretable 2-layer MLP with positive outputs:
      - Hidden modules use ReLU thresholding
      - Linear readout gives gene logits, then softplus ensures positivity

    Args:
        params: dict with 'W1','b1','W2','b2'.
        x:      Array (batch_size, num_tfs) of TF levels.

    Returns:
        Array (batch_size, num_genes) of non-negative transcription rates.
    """

    # Module activations (logical combination of TFs)
    h = jax.nn.elu(jnp.dot(p_tf, params["W1"]) + params["b1"])
    # Linear read-out to genes
    logits = jnp.dot(h, params["W2"]) + params["b2"]
    # Enforce non-negativity: softplus activation
    out = jax.nn.softplus(logits)
    return out

# Define the ODE function using the MLP
@beartype
def dstate_dt(t, state, args):
    """
    Compute the derivative of the state vector for the coupled system using a neural network.

    Args:
        t: Time scalar.
        state: State vector [u_1, ..., u_G, s_1, ..., s_G].
        args: Tuple containing parameters (G, beta_g, gamma_g, nn_params, T_ON).

    Returns:
        Derivative of the state vector
    """

    alpha_0, beta_g, gamma_g, lamda, kappa, hill_params, tf_indices = args

    u = state[..., 0]  # Unspliced counts for all genes.
    s = state[..., 1]  # Spliced counts for all genes.
    p = state[..., 2]  # Proteins for all genes.

    # Clip state values to increase numerical stability:
    u = jnp.clip(u, 0, 1e3)
    s = jnp.clip(s, 0, 1e3)
    p = jnp.clip(p, 0, 1e3)

    # Compute transcription rates using the neural network
    p_tf = p[:, tf_indices]   # (batch, num_tfs)

    reg = hill_regulation(
        p_tf,
        hill_params
    )

    alpha = jnp.clip(alpha_0 * reg, 0.0, 1e3)

    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u - gamma_g * s
    # Compute dp_dt only for TF indices
    dp_dt = jnp.zeros_like(u)
    dp_dt = dp_dt.at[:, tf_indices].set(
        lamda * s[:, tf_indices] - kappa * p[:, tf_indices]
    )

    dstate_dt = jnp.stack([du_dt, ds_dt, dp_dt], axis=-1)  # Shape: (3G,)
    return dstate_dt

def euler_integrator(
    times: jnp.ndarray,      # (L+1,)
    y0: jnp.ndarray,         # state at t0, shape (G,3)
    drift_fn: Any,           # f(t, y, args) -> dy/dt
    drift_args: Any,
    rng_key: jax.random.PRNGKey,
    sigma_noise: float = 1e-4,   # ← small noise scale
) -> jnp.ndarray:
    """
    Euler–Maruyama integrator: y_{n+1} = y_n + f(t_n,y_n)*dt + sigma_noise*sqrt(dt)*eps_n
    """
    dt = jnp.diff(times)  # (L,)
    # draw one Gaussian noise array per step
    eps = jax.random.normal(rng_key, shape=(dt.shape[0],) + y0.shape)  # (L, G, 3)

    def step(carry, inp):
        y_prev, t_prev = carry
        dt_i, eps_i = inp
        f      = drift_fn(t_prev, y_prev, drift_args)
        # scale the noise by sqrt(dt_i)
        noise  = sigma_noise * jnp.sqrt(dt_i)[None, None] * eps_i
        y_new  = y_prev + f * dt_i + noise
        # optional clipping for stability
        y_new  = jnp.clip(y_new, 0.0, 1e3)
        return (y_new, t_prev + dt_i), y_new

    (final, _), ys = lax.scan(step, (y0, times[0]), (dt, eps))
    return jnp.concatenate([y0[None], ys], axis=0)

# Define the complete NumPyro model
@config_enumerate
def model(
    data: Any,
    M_c: Any,
    obs2sample: Any,
    batch_index: Any,
    tf_indices: Any,
    total_num_cells: int,
    n_batch: int,
    prior_time: Any,
    prior_timespan: Any,
    prior_path: Any,
    unknown_idx: Any,
    unknown_count: int,
    known_idx: Any,
    times_norm: Any,
    T_limits: Any,
    hidden_units: Any,
    num_paths: int,
    obs_path_props: Any,
    return_alpha: bool = False,
    Tmax_alpha: float = 50.0,
    Tmax_beta: float = 1.0,
    splicing_rate_alpha_hyp_prior_alpha: float = 20.0,
    splicing_rate_alpha_hyp_prior_mean: float = 5.0,
    splicing_rate_mean_hyp_prior_alpha: float = 10.0,
    splicing_rate_mean_hyp_prior_mean: float = 1.0,
    degradation_rate_alpha_hyp_prior_alpha: float = 20.0,
    degradation_rate_alpha_hyp_prior_mean: float = 5.0,
    degradation_rate_mean_hyp_prior_alpha: float = 10.0,
    degradation_rate_mean_hyp_prior_mean: float = 1.0,
    transcription_rate_alpha_hyp_prior_alpha: float = 20.0,
    transcription_rate_alpha_hyp_prior_mean: float = 2.0,
    transcription_rate_mean_hyp_prior_alpha: float = 10.0,
    transcription_rate_mean_hyp_prior_mean: float = 5.0,
    lambda_alpha: float = 10.0,
    lambda_mean: float = 20.0,
    kappa_alpha: float = 1.0,
    kappa_mean: float = 2.0,
    detection_mean_hyp_prior_alpha: float = 1.0,
    detection_mean_hyp_prior_beta: float = 1.0,
    detection_hyp_prior_alpha: float = 10.0,
    detection_i_prior_alpha: float = 100.0,
    detection_gi_prior_alpha: float = 200.0,
    gene_add_alpha_hyp_prior_alpha: float = 9.0,
    gene_add_alpha_hyp_prior_beta: float = 3.0,
    gene_add_mean_hyp_prior_alpha: float = 1.0,
    gene_add_mean_hyp_prior_beta: float = 100.0,
    stochastic_v_ag_hyp_prior_alpha: float = 12.0,
    stochastic_v_ag_hyp_prior_beta: float = 3.0,
    **kwargs,
):
    """
    NumPyro model for coupled transcription and splicing dynamics.

    Args:
        data: Observed data array of shape (num_cells, num_genes, num_modalities).
        M_c: Number of cells in each metacell.
        batch_index: Array indicating batch assignments for each cell.
        tf_indices: Indices of genes that are TFs.
        total_num_cells: Number of cells in the full dataset.
        n_batch: Number of batches.
        Tmax_alpha: Alpha parameter for Tmax prior.
        Tmax_beta: Beta parameter for Tmax prior.
        ... (other hyperparameters for priors)
        key: Random number generator key.

    Returns:
        None. Defines the probabilistic model for inference.
    """

    num_cells = int(data.shape[0])
    num_genes = int(data.shape[1])
    num_modalities = int(data.shape[2])
    num_tfs = tf_indices.shape[0]
    batch_size = num_cells

    # Splicing Rates for mRNA
    splicing_alpha = numpyro.sample(
        "splicing_alpha",
        dist.Gamma(
            splicing_rate_alpha_hyp_prior_alpha,
            splicing_rate_alpha_hyp_prior_alpha / splicing_rate_alpha_hyp_prior_mean,
            validate_args=True,
        ),
    )
    splicing_alpha = jnp.clip(splicing_alpha, a_min=1e-2, a_max=1e3)

    splicing_mean = numpyro.sample(
        "splicing_mean",
        dist.Gamma(
            splicing_rate_mean_hyp_prior_alpha,
            splicing_rate_mean_hyp_prior_alpha / splicing_rate_mean_hyp_prior_mean,
            validate_args=True,
        ),
    )
    splicing_mean = jnp.clip(splicing_mean, a_min=1e-2, a_max=1e3)

    beta_g = numpyro.sample(
        "beta_g",
        dist.Gamma(splicing_alpha, splicing_alpha / splicing_mean, validate_args=True)
        .expand([num_genes])
        .to_event(1),
    )

    # Degradation Rates for mRNA
    degradation_alpha = numpyro.sample(
        "degradation_alpha",
        dist.Gamma(
            degradation_rate_alpha_hyp_prior_alpha,
            degradation_rate_alpha_hyp_prior_alpha
            / degradation_rate_alpha_hyp_prior_mean,
            validate_args=True,
        ),
    )
    degradation_alpha = degradation_alpha + 0.001  # Prevent zero

    degradation_mean = numpyro.sample(
        "degradation_mean",
        dist.Gamma(
            degradation_rate_mean_hyp_prior_alpha,
            degradation_rate_mean_hyp_prior_alpha
            / degradation_rate_mean_hyp_prior_mean,
            validate_args=True,
        ),
    )
    degradation_mean = jnp.clip(degradation_mean, a_min=1e-2, a_max=1e3)

    gamma_g = numpyro.sample(
        "gamma_g",
        dist.Gamma(
            degradation_alpha, degradation_alpha / degradation_mean, validate_args=True
        )
        .expand([num_genes])
        .to_event(1),
    )

    # Translation rate for proteins
    lamda = numpyro.sample(
        "lambda",
        dist.Gamma(lambda_alpha, lambda_alpha / lambda_mean, validate_args=True)
        .expand([num_tfs])
        .to_event(1),
    )
    # Degradation rate for proteins
    kappa = numpyro.sample(
        "kappa",
        dist.Gamma(kappa_alpha, kappa_alpha / kappa_mean, validate_args=True)
        .expand([num_tfs])
        .to_event(1),
    )

    # Time Parameters
    # sample a *single* global scaling factor
    T_min, T_max = T_limits
    T_scaling = numpyro.sample("T_scaling", dist.Beta(1.0, 3.0))
    # total_span = (T_max - T_min) * T_scaling

    # # build *static‐shape* grid (always N_steps long)
    # abs_grid   = T_min + times_norm * (T_max - T_min)
    # times_grid = T_scaling * abs_grid

    total_span = (T_max - T_min) * T_scaling

    # 2) build *static‐shape* grid (always N_steps long)
    times_grid = T_min + times_norm * total_span
    # dt = dt_norm * total_span

    # convert your absolute prior_time (if any) into a [0,1] loc/scale
    if prior_time is None:
        prior_time = T_min + (T_max - T_min) / 2
        prior_time_sd = prior_timespan / 2.0
    else:
        prior_time_sd = prior_timespan / 40.0

    with numpyro.plate("cells", batch_size):
        t_c = numpyro.sample(
            "t_c",
            dist.TruncatedNormal(
                loc=prior_time,
                scale=prior_time_sd,
                low=T_limits[0],
                high=T_limits[1],
            ),
        )
        T_c = numpyro.deterministic("T_c", T_scaling * t_c)

    # ============= Expression model =============== #

    # scale of alpha
    alpha_0 = numpyro.sample(
        "alpha_0",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([num_genes]).to_event(1),
    )

    # ______ Initial conditions ______

    # 1) Shared “root” init via Gamma (as before)
    base_init = numpyro.sample(
        "base_init",
        dist.Gamma(1.0, 1.0)
            .expand([num_genes, 3])
            .to_event(2)   # shape (G,3): [u,s,p]
    )

    # 2) Additive noise per path, but keep it all in one shot
    σ_noise = 0.01  # tune this to control spread of your inits
    init_noise = numpyro.sample(
        "init_noise",
        dist.Normal(0.0, σ_noise)
            .expand([num_paths, num_genes, 3])
            .to_event(3)   # event dims = (P,G,3)
    )

    # 3) Combine and clip at zero
    init_state_paths = numpyro.deterministic("init_state_paths",
        jnp.clip(
        base_init[None, ...] + init_noise,
        a_min=0.0,
        a_max=jnp.inf
    ))

    # ________ Neural Net Params _______________

    # Compute your scales once
    std1 = jnp.sqrt(2.0 / (num_tfs + hidden_units))
    std2 = jnp.sqrt(2.0 / (hidden_units + num_genes))

    # Grab two RNG subkeys
    key = numpyro.prng_key()
    k1, k2 = jax.random.split(key, 2)

    # Now define path-specific params via one numpyro.param each:
    W1 = numpyro.param(
        "W1",  # name in the trace
        jax.random.normal(k1, (num_paths, num_tfs, hidden_units)) * std1
    )  # → shape (P, T, H)

    b1 = numpyro.param(
        "b1",
        jnp.zeros((num_paths, hidden_units))
    )  # → shape (P, H)

    W2 = numpyro.param(
        "W2",
        jax.random.normal(k2, (num_paths, hidden_units, num_genes)) * std2
    )  # → shape (P, H, G)

    b2 = numpyro.param(
        "b2",
        jnp.zeros((num_paths, num_genes))
    )  # → shape (P, G)

    hill_params = {"W1": W1, "b1": b1, "W2": W2, "b2": b2}

    # Pass the whole dict (with leading path axis) into your ODE args:
    ode_args = (alpha_0, beta_g, gamma_g, lamda, kappa, hill_params, tf_indices)

    # Grab P different RNG keys
    base_key = jax.random.PRNGKey(0)
    keys = jax.random.split(base_key, num_paths)  # shape (P, 2) for two‐integers keys

    # leave out tf_indices from common_args:
    common_args = (alpha_0, beta_g, gamma_g, lamda, kappa)

    def run_one_path(hill_params_i, init_state_i, rng_key):
        # 1) pack your args in the correct order
        args_i = (alpha_0, beta_g, gamma_g, lamda, kappa,
                  hill_params_i, tf_indices)

        # 2) add a dummy leading batch axis so state.shape == (1, G, 3)
        y0 = init_state_i[jnp.newaxis, ...]

        # 3) run your Euler integrator
        sol = euler_integrator(times_grid, y0, dstate_dt, args_i, rng_key)
        # sol.shape == (L+1, 1, G, 3)

        # 4) remove the batch axis, returning (L+1, G, 3)
        return sol[:, 0, :, :]

    sol_paths = jax.vmap(run_one_path, in_axes=(0, 0, 0))(
        hill_params,       # (P, …)
        init_state_paths,  # (P, G, 3)
        keys,              # (P,)
    )  # -> (P, L+1, G, 3)

    sol_grid = jnp.transpose(sol_paths, (1, 0, 2, 3))

    sol_at_cells = interpolate_solution(sol_grid, times_grid, T_c)

    # Track as predictions_rearranged for compatibility purposes with some plotting functions
    numpyro.deterministic('predictions_rearranged', sol_at_cells)
    numpyro.deterministic('sol_at_cells', sol_at_cells)

    mu_expression = jnp.clip(sol_at_cells[..., :2], 1e-5, 1e5)

    # Wiggliness penalty (sum of squared curvature)
    d1 = sol_grid[1:] - sol_grid[:-1]
    d2 = d1[1:] - d1[:-1]
    penalty = jnp.sum(jnp.square(d2))/times_norm.shape[0]
    numpyro.factor("smoothness_penalty", - 10 * penalty)

    # ============= Detection efficiency of spliced and unspliced counts =============== #

    # Batch/Experiment-level scaling centered at 0.5
    with numpyro.plate("batch", n_batch):
        y_e = numpyro.sample(
            "detection_y_e",
            dist.Beta(detection_mean_hyp_prior_alpha,
                      detection_mean_hyp_prior_beta)
        )  # shape (n_batch,)

    # cell‐level scaling, centered at 1 (large variance)
    α_c = detection_hyp_prior_alpha
    with numpyro.plate("cells", batch_size):
        y_c = numpyro.sample(
            "detection_y_c",
            dist.Gamma(α_c, α_c)
        )  # shape (n_cells,)

    # Modality-level scaling, centered at 1 (moderate variance)
    detection_y_i = numpyro.sample(
        "detection_y_i",
        dist.Gamma(detection_i_prior_alpha, detection_i_prior_alpha, validate_args=True)
        .expand([1, 1, 2])
        .to_event(3),
    )

    # Modality and gene-level scaling, centered at 1 (small variance)
    detection_y_gi = numpyro.sample(
        "detection_y_gi",
        dist.Gamma(
            jnp.ones((1, 1)) * detection_gi_prior_alpha,
            jnp.ones((1, 1)) * detection_gi_prior_alpha,
            validate_args=True,
        )
        .expand([1, num_genes, 2])
        .to_event(3),
    )

    # ======= Gene-specific additive component (Ambient RNA/ "Soup") for spliced and unspliced counts ====== #

    s_g_gene_add_alpha_hyp = numpyro.sample(
        "s_g_gene_add_alpha_hyp",
        dist.Gamma(
            gene_add_alpha_hyp_prior_alpha,
            gene_add_alpha_hyp_prior_beta,
            validate_args=True,
        ).expand([2]).to_event(1)
    )

    s_g_gene_add_mean = numpyro.sample(
        "s_g_gene_add_mean",
        dist.Gamma(
            gene_add_mean_hyp_prior_alpha,
            gene_add_mean_hyp_prior_beta,
            validate_args=True,
        )
        .expand([n_batch, 1, 2])
        .to_event(3),
    )

    s_g_gene_add_alpha_e_inv = numpyro.sample(
        "s_g_gene_add_alpha_e_inv",
        dist.Exponential(s_g_gene_add_alpha_hyp).expand([n_batch, 1, 2]).to_event(3),
    )

    s_g_gene_add_alpha_e = jnp.ones((1, 1)) / s_g_gene_add_alpha_e_inv**2

    s_g_gene_add = numpyro.sample(
        "s_g_gene_add",
        dist.Gamma(
            s_g_gene_add_alpha_e,
            s_g_gene_add_alpha_e / s_g_gene_add_mean,
            validate_args=True,
        )
        .expand([n_batch, num_genes, 2])
        .to_event(3),
    )

    # ========= Gene-specific overdispersion of spliced and unspliced counts ============== #

    stochastic_v_ag_hyp = numpyro.sample(
        "stochastic_v_ag_hyp",
        dist.Gamma(
            stochastic_v_ag_hyp_prior_alpha,
            stochastic_v_ag_hyp_prior_beta,
            validate_args=True,
        )
        .expand([1, 2])
        .to_event(2),
    )

    stochastic_v_ag_inv = numpyro.sample(
        "stochastic_v_ag_inv",
        dist.Exponential(stochastic_v_ag_hyp).expand([1, num_genes, 2]).to_event(3),
    )

    stochastic_v_ag = numpyro.deterministic("stochastic_v_ag", jnp.ones((1, 1)) / stochastic_v_ag_inv**2)

    # ===================== Expected expression ======================= #

    additive_term = jnp.einsum("cb,bgi->cgi", obs2sample, s_g_gene_add)
    additive_term = additive_term[:, None, :, :]           # add path dim
    additive_term = numpyro.deterministic("additive_term", additive_term)

    normalizing_term = (
        y_e[batch_index][:, None, None, None]  # (cells,1,1,1)
        * y_c[:, None, None, None]             # (cells,1,1,1)
        * detection_y_i[None, None, :, :]      # (1,1,genes,2)
        * detection_y_gi[None, None, :, :]     # (1,1,genes,2)
        * M_c[:, None, :, :]                   # (cells,1,genes,1)
    )

    normalizing_term = numpyro.deterministic("normalizing_term", normalizing_term[0,...])

    # # ===================== DATA likelihood ======================= #
    # mu = numpyro.deterministic("mu", (mu_expression + additive_term) * normalizing_term)
    # # jax.debug.print("mu.shape = {}", mu.shape)

    # weights = numpyro.sample("weights", dist.Dirichlet(0.5 * jnp.ones(num_paths)))
    # # jax.debug.print("weights.shape = {}", weights.shape)

    # concentration = (stochastic_v_ag * M_c)
    # # jax.debug.print("concentration.shape = {}", concentration.shape)

    # with scale(scale=total_num_cells / batch_size):
    #     with numpyro.plate("cells", batch_size) as c:

    #         z = numpyro.sample(
    #             "z",
    #             dist.Categorical(logits=weights),
    #             infer={"enumerate": "parallel"}
    #         )

    #         idx = jnp.arange(batch_size)

    #         mu_selected = mu[idx, z, :, :]

    #         # jax.debug.print("z.shape = {}", z.shape)
    #         # jax.debug.print("muz.shape = {}", mu_selected.shape)

    #         rate = concentration/ mu_selected

    #         # jax.debug.print("rate.shape = {}", rate.shape)

    #         numpyro.sample(
    #             "data",
    #             dist.GammaPoisson(concentration, rate).to_event(2),
    #             obs=data,
    #         )

    # ============= DATA likelihood ============== #
    mu = numpyro.deterministic("mu", (mu_expression + additive_term) * normalizing_term)

    weights = numpyro.sample(
        "weights", dist.Dirichlet(0.5 * jnp.ones(num_paths))
    )

    # penalty: squared‐error from observed proportions
    dev = weights - obs_path_props                 # deviation vector
    penalty = jnp.sum(dev**2)                      # sum of squared deviations
    λ_penalty = 10**6                                # you can tune this scale
    numpyro.factor("path_prop_penalty", -λ_penalty * penalty)

    concentration = stochastic_v_ag * M_c

    with scale(scale=total_num_cells / batch_size):

        # 1) Unknown cells → sample z, then likelihood
        with numpyro.plate("unknown_cells", unknown_idx.shape[0]):
            z = numpyro.sample(
                "z",
                dist.Categorical(logits=weights),
                infer={"enumerate": "parallel"},
            )

            idx = unknown_idx
            mu_u   = mu[idx, z, :, :]
            rate_u = concentration[idx] / mu_u
            numpyro.sample(
                "data_unknown",
                dist.GammaPoisson(concentration[idx], rate_u).to_event(2),
                obs=data[idx],
            )

        # 2) Known cells → fixed z = prior_path, then likelihood
        with numpyro.plate("known_cells", known_idx.shape[0]):
            idx = known_idx
            z   = prior_path[idx]
            mu_k   = mu[idx, z, :, :]
            rate_k = concentration[idx] / mu_k
            numpyro.sample(
                "data_known",
                dist.GammaPoisson(concentration[idx], rate_k).to_event(2),
                obs=data[idx],
            )












