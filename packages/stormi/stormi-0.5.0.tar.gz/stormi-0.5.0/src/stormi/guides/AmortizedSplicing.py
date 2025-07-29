from functools import partial

import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro.handlers import block, seed
from numpyro.infer.autoguide import AutoGuideList, AutoNormal


def _amortized_network(params_dict: dict, data_array: jnp.ndarray, embedding: jnp.ndarray):
    """
    Compute parameters of latent distributions using a shared neural network.

    Args:
        params_dict (dict): Dictionary of learnable neural network parameters.
        data_array (jnp.ndarray): Input tensor of shape (n_cells, n_genes, n_mods).
        embedding (jnp.ndarray): Embedding tensor (e.g., cell/gene features).

    Returns:
        Tuple: Distribution parameters (loc and scale) for:
            - t_c (Normal)
            - detection_y_c (LogNormal)
            - beta (LogNormal)
            - Optional: detection_l_c (LogNormal)
    """
    def normalize_by_total_counts(data_2d):
        total_counts = jnp.sum(data_2d, axis=1, keepdims=True)
        return data_2d / (total_counts + 1e-8)

    n_cells, n_genes, n_mods = data_array.shape
    d_in = n_genes * n_mods

    data_2d = data_array.reshape((n_cells, d_in))
    data_2d_log1p = jnp.log1p(normalize_by_total_counts(data_2d))

    # ---- Cell-specific hidden layer ----
   # Extract common parameters
    V_shared = params_dict["V_shared"]
    c_shared = params_dict["c_shared"]
    V_t_c = params_dict["V_t_c"]
    c_t_c = params_dict["c_t_c"]
    V_out_t_c = params_dict["V_out_t_c"]
    c_out_t_c = params_dict["c_out_t_c"]
    V_det = params_dict["V_det"]
    c_det = params_dict["c_det"]
    V_out_det = params_dict["V_out_det"]
    c_out_det = params_dict["c_out_det"]
    V_beta = params_dict["V_beta"]
    c_beta = params_dict["c_beta"]
    V_out_beta = params_dict["V_out_beta"]
    c_out_beta = params_dict["c_out_beta"]

    # Shared layer
    hidden_shared = jax.nn.elu(
        jnp.einsum("cd,dh->ch", data_2d_log1p, V_shared) + c_shared
    )

    # t_c branch
    hidden_t_c = jax.nn.elu(jnp.einsum("ch,hm->cm", hidden_shared, V_t_c) + c_t_c)
    out_raw_t_c = jnp.einsum("cm,mo->co", hidden_t_c, V_out_t_c) + c_out_t_c
    loc_t_c_raw = out_raw_t_c[:, 0]
    scale_t_c_raw = out_raw_t_c[:, 1]
    scale_t_c = jax.nn.softplus(scale_t_c_raw) + 1e-3

    # detection_y_c branch
    hidden_det = jax.nn.elu(jnp.einsum("ch,hm->cm", hidden_shared, V_det) + c_det)
    out_raw_det = jnp.einsum("cm,mo->co", hidden_det, V_out_det) + c_out_det
    loc_det_raw = out_raw_det[:, 0]
    scale_det_raw = out_raw_det[:, 1]
    scale_det = jax.nn.softplus(scale_det_raw) + 1e-3

    # ----- Optional branch: detection_l_c -----
    if "V_det_l" in params_dict:
        V_det_l = params_dict["V_det_l"]
        c_det_l = params_dict["c_det_l"]
        V_out_det_l = params_dict["V_out_det_l"]
        c_out_det_l = params_dict["c_out_det_l"]

        hidden_det_l = jax.nn.elu(
            jnp.einsum("ch,hm->cm", hidden_shared, V_det_l) + c_det_l
        )
        out_raw_det_l = jnp.einsum("cm,mo->co", hidden_det_l, V_out_det_l) + c_out_det_l
        loc_det_l_raw = out_raw_det_l[:, 0]
        scale_det_l_raw = out_raw_det_l[:, 1]
        scale_det_l = jax.nn.softplus(scale_det_l_raw) + 1e-3
    # ---- Gene-specific branch: beta ----
    # Assume embedding is (n_cells, embed_dim), and maybe gene info is broadcasted
    # gd, dh
    #print("embedding shape:", embedding.shape)
    #print("V_beta shape:", V_beta.shape)

    hidden_beta = jax.nn.elu(jnp.einsum("ge,eh->gh", embedding, V_beta) + c_beta)
    out_raw_beta = jnp.einsum("gh,ho->go", hidden_beta, V_out_beta) + c_out_beta
    loc_beta_raw = out_raw_beta[:, 0]
    scale_beta = jax.nn.softplus(out_raw_beta[:, 1]) + 1e-3

    if loc_det_l_raw is not None:
        return loc_t_c_raw, scale_t_c, loc_det_raw, scale_det, loc_det_l_raw, scale_det_l, loc_beta_raw, scale_beta
    else:
        return loc_t_c_raw, scale_t_c, loc_det_raw, scale_det, loc_beta_raw, scale_beta


#The amortized_guide function
################################################################################


def amortized_guide(*args, predict_detection_l_c: bool = True, **kwargs):
    """
    Amortized guide for local latent variables using neural network outputs.

    Args:
        *args: Positional arguments containing data and optional embedding.
        predict_detection_l_c (bool): Whether to model detection_l_c explicitly.
        **kwargs: Keyword arguments for 'data' and 'embedding'.

    Returns:
        dict: Samples of local latent variables (t_c, detection_y_c, beta, detection_l_c).
"""

    # -------------------- 1. Get data & embedding --------------------
    data = kwargs.get("data", args[0] if args else None)
    if data is None:
        raise ValueError("Missing required input: 'data'")

  # or however many dims you want

    # Register a learnable embedding (one vector per cell)
    embedding = kwargs.get("embedding", args[1] if len(args) > 1 else None)
    if embedding is None:
        raise ValueError("embedding' is missing. You must pass it into the guide as a keyword or positional argument.")

    #print("embedding shape:", embedding.shape)

    #print("Data shape", data.shape)
    n_cells, n_genes, n_mods = data.shape
    embed_dim = embedding.shape[1]
    #print("embedding dimension", embed_dim)
    d_in = n_genes * n_mods


    # -------------------- 2. Network dimensions --------------------
    hidden_dim_shared = 256
    hidden_dim_t_c = 128
    hidden_dim_det = 128
    hidden_dim_beta = 128
    out_dim = 2  # (loc, scale)

    # -------------------- 3. Define shared + output layers --------------------
    V_shared = numpyro.param(
        "V_shared",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(1)), (d_in, hidden_dim_shared)
        )
        * 0.01,
    )
    c_shared = numpyro.param("c_shared", jnp.zeros((hidden_dim_shared,)))

    V_t_c = numpyro.param(
        "V_t_c",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(2)),
            (hidden_dim_shared, hidden_dim_t_c),
        )
        * 0.01,
    )
    c_t_c = numpyro.param("c_t_c", jnp.zeros((hidden_dim_t_c,)))
    V_out_t_c = numpyro.param(
        "V_out_t_c",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(3)), (hidden_dim_t_c, out_dim)
        )
        * 0.01,
    )
    c_out_t_c = numpyro.param("c_out_t_c", jnp.zeros((out_dim,)))

    V_det = numpyro.param(
        "V_det",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(4)),
            (hidden_dim_shared, hidden_dim_det),
        )
        * 0.01,
    )
    c_det = numpyro.param("c_det", jnp.zeros((hidden_dim_det,)))
    V_out_det = numpyro.param(
        "V_out_det",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(5)), (hidden_dim_det, out_dim)
        )
        * 0.01,
    )
    c_out_det = numpyro.param("c_out_det", jnp.zeros((out_dim,)))


    V_beta = numpyro.param("V_beta", jax.random.normal(jax.random.PRNGKey(11), (embed_dim, hidden_dim_beta)) * 0.01)
    #print(" V_beta shape:", V_beta.shape)
    c_beta = numpyro.param("c_beta", jnp.zeros((hidden_dim_beta,)))
    V_out_beta = numpyro.param("V_out_beta", jax.random.normal(jax.random.PRNGKey(12), (hidden_dim_beta, out_dim)) * 0.01)
    c_out_beta = numpyro.param("c_out_beta", jnp.zeros((out_dim,)))

    net_params = {
        "V_shared": V_shared,
        "c_shared": c_shared,
        "V_t_c": V_t_c,
        "c_t_c": c_t_c,
        "V_out_t_c": V_out_t_c,
        "c_out_t_c": c_out_t_c,
        "V_det": V_det,
        "c_det": c_det,
        "V_out_det": V_out_det,
        "c_out_det": c_out_det,
        "V_beta": V_beta,
        "c_beta": c_beta,
        "V_out_beta": V_out_beta,
        "c_out_beta": c_out_beta,
    }
    if predict_detection_l_c:
        V_det_l = numpyro.param(
            "V_det_l",
            jax.random.normal(
                jax.lax.stop_gradient(jax.random.PRNGKey(6)),
                (hidden_dim_shared, hidden_dim_det),
            )
            * 0.01,
        )
        c_det_l = numpyro.param("c_det_l", jnp.zeros((hidden_dim_det,)))
        V_out_det_l = numpyro.param(
            "V_out_det_l",
            jax.random.normal(
                jax.lax.stop_gradient(jax.random.PRNGKey(7)), (hidden_dim_det, out_dim)
            )
            * 0.01,
        )
        c_out_det_l = numpyro.param("c_out_det_l", jnp.zeros((out_dim,)))
        net_params.update(
            {
                "V_det_l": V_det_l,
                "c_det_l": c_det_l,
                "V_out_det_l": V_out_det_l,
                "c_out_det_l": c_out_det_l,
            }
        )

    # -------------------- 4. Optional detection_l_c branch --------------------

    # -------------------- 5. Forward pass --------------------
    outputs = _amortized_network(net_params, data, embedding)

    if predict_detection_l_c:
        loc_t_c, scale_t_c, loc_det, scale_det, loc_det_l, scale_det_l, loc_beta, scale_beta = outputs
    else:
        loc_t_c, scale_t_c, loc_det, scale_det, loc_beta, scale_beta = outputs

    # -------------------- 6. Sampling --------------------
    with numpyro.plate("cells", n_cells):
        t_c = numpyro.sample("t_c", dist.Normal(loc_t_c, scale_t_c))
        detection_y_c = numpyro.sample(
            "detection_y_c", dist.TransformedDistribution(dist.Normal(loc_det, scale_det), dist.transforms.ExpTransform())
        )
        if predict_detection_l_c:
            detection_l_c = numpyro.sample(
                "detection_l_c", dist.TransformedDistribution(dist.Normal(loc_det_l, scale_det_l), dist.transforms.ExpTransform()),
                infer={"is_auxiliary": True}
            )
    with numpyro.plate("genes", loc_beta.shape[0]):
        beta = numpyro.sample("beta",dist.TransformedDistribution(dist.Normal(loc_beta, scale_beta),dist.transforms.ExpTransform()),
            infer={"is_auxiliary": True}
        )


    # -------------------- 7. Return --------------------
    out_dict = {
        "t_c": t_c,
        "detection_y_c": detection_y_c,
        "beta": beta,
    }
    if predict_detection_l_c:
        out_dict["detection_l_c"] = detection_l_c

    return out_dict



################################################################################
# 3) Extraction helper functions
################################################################################


def extract_global_posterior_mean(guide, svi_state, svi):
    """
    Extract posterior means for global variables from AutoNormal guide.

    Args:
        guide: AutoGuideList object.
        svi_state: State of the optimizer after training.
        svi: SVI object.

    Returns:
        dict: Dictionary of posterior mean estimates for global variables.
    """
    auto_guide = guide._guides[0]  # AutoNormal sub-guide (global parameters)
    params = svi.get_params(svi_state)
    return auto_guide.median(params)


def extract_local_posterior_mean(guide, svi_state, svi, data, embedding):
    """
    Compute posterior means of local latent variables using the amortized network.

    Args:
        guide: AutoGuideList object.
        svi_state: Trained SVI state.
        svi: SVI object.
        data (jnp.ndarray): Input data array (n_cells, n_genes, n_mods).
        embedding (jnp.ndarray): Embedding array (e.g., for beta estimation).

    Returns:
        dict: Posterior means for t_c, detection_y_c, beta, and optionally detection_l_c.
    """
    params = svi.get_params(svi_state)
    #embedding = params["learnable_embedding"]



    needed_keys = [
        "V_shared", "c_shared",
        "V_t_c", "c_t_c", "V_out_t_c", "c_out_t_c",
        "V_det", "c_det", "V_out_det", "c_out_det",
        "V_beta", "c_beta", "V_out_beta", "c_out_beta",
    ]

    has_det_l = "V_det_l" in params
    if has_det_l:
        needed_keys += ["V_det_l", "c_det_l", "V_out_det_l", "c_out_det_l"]

    for k in needed_keys:
        if k not in params:
            raise ValueError(f"Missing param '{k}' in SVI state.")

    net_params = {k: params[k] for k in needed_keys}
    outputs = _amortized_network(net_params, data, embedding)

    if has_det_l:
        loc_t_c, _, loc_det, _, loc_det_l, _, loc_beta, _ = outputs
        detection_l_c_mean = jnp.exp(loc_det_l)
    else:
        loc_t_c, _, loc_det, _, loc_beta, _ = outputs
        detection_l_c_mean = None

    result = {
        "t_c": loc_t_c,
        "detection_y_c": jnp.exp(loc_det),
        "beta": jnp.exp(loc_beta),
    }
    if detection_l_c_mean is not None:
        result["detection_l_c"] = detection_l_c_mean

    return result


def extract_posterior_means(guide, svi_state, svi, data, embedding):
    """
    Extract both global and local posterior means from trained guide.

    Args:
        guide: AutoGuideList with global and amortized components.
        svi_state: Trained SVI state.
        svi: SVI object.
        data (jnp.ndarray): Input data tensor.
        embedding (jnp.ndarray): Embedding tensor for beta estimation.

    Returns:
        tuple: (global_means, local_means) dictionaries.
    """
    global_means = extract_global_posterior_mean(guide, svi_state, svi)
    local_means = extract_local_posterior_mean(guide, svi_state, svi, data, embedding)
    return global_means, local_means



################################################################################
# 4) The AmortizedNormal class
################################################################################


class AmortizedNormal:
    def __init__(self, model, embedding=None,predict_detection_l_c: bool = True, init_loc_fn=None):
        """
    Wrapper for combining AutoNormal with a custom amortized guide.

    This class separates global and local variable inference, and provides
    unified methods to extract posterior means and samples.

    Args:
        model: NumPyro model function.
        embedding (jnp.ndarray): Embedding tensor for beta inference.
        predict_detection_l_c (bool): Whether to model detection_l_c.
        init_loc_fn: Optional initialization function for AutoNormal.
    """
        self.model = model
        self.predict_detection_l_c = predict_detection_l_c
        self.guide_list = AutoGuideList(model)
        self.embedding = embedding

        # Seeded model for consistent param init
        seeded_model = seed(model, rng_seed=0)

        # Variables handled by amortized guide (i.e., not in AutoNormal)
        hide_list = [
            "t_c",
            "detection_y_c",
            "beta",               # NEW
            "T_c",
            "predictions",
            "mu",
            "d_cr",
            "mu_atac",
            "predictions_rearranged",
            "alpha_cg",
            "additive_term",
            "normalizing_term",
            "P_rh",
        ]
        if predict_detection_l_c:
            hide_list.append("detection_l_c")

        blocked_model = block(seeded_model, hide=hide_list)
        auto_normal_guide = AutoNormal(blocked_model, init_loc_fn=init_loc_fn)
        self.guide_list.append(auto_normal_guide)

        self.guide_list.append(partial(amortized_guide, predict_detection_l_c=self.predict_detection_l_c,embedding=self.embedding))

    def __call__(self, *args, **kwargs):
        return self.guide_list(*args, **kwargs)

    def quantiles(self, params, quantiles):
        return self.guide_list.quantiles(params, quantiles)

    def median(self, params):
        return self.guide_list.median(params)

    def sample_posterior(self, rng_key, params, sample_shape=()):
        return self.guide_list.sample_posterior(rng_key, params, sample_shape)

    def get_posterior(self, params):
        return self.guide_list.get_posterior(params)

    # ---- Convenience methods for extracting posterior means ----
    def extract_global_means(self, svi_state, svi):
        return extract_global_posterior_mean(self.guide_list, svi_state, svi)

    def extract_local_means(self, svi_state, svi, data,embedding=None):
        return extract_local_posterior_mean(self.guide_list, svi_state, svi, data, self.embedding)

    def extract_all_means(self, svi_state, svi, data):
        global_means = self.extract_global_means(svi_state, svi)
        local_means = self.extract_local_means(svi_state, svi, data,self.embedding)
        return global_means, local_means
