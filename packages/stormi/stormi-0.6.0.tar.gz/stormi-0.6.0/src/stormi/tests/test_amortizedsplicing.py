import anndata as ad
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure
from numpyro.distributions.continuous import Gamma
from numpyro.infer.initialization import init_to_mean

import stormi.posterior as posterior_module
from stormi.guides.AmortizedSplicing import AmortizedNormal
from stormi.models.RNA_1layer import model, prepare_model_input, sample_prior
from stormi.plotting import plot_elbo_loss, predictions_vs_data
from stormi.train import train_svi

# Disable validate_args for Gamma
_orig_gamma_init = Gamma.__init__
def _no_validate_gamma_init(self, concentration, rate, validate_args=True):
    _orig_gamma_init(self, concentration, rate, validate_args=False)
Gamma.__init__ = _no_validate_gamma_init

###############################################################################
# Fixtures for amortized workflow
###############################################################################

@pytest.fixture(scope="module")
def adata_rna():
    np.random.seed(0)
    genes = [f"gene{i}" for i in range(1, 3)]  # 2 genes
    cells = [f"cell{i}" for i in range(1, 3)]  # 2 cells

    spliced = np.random.randint(0, 100, size=(len(cells), len(genes)))
    unspliced = np.random.randint(0, 100, size=(len(cells), len(genes)))

    obs = pd.DataFrame({
        "n_cells": np.random.randint(1, 11, size=len(cells)),
        "day_float": np.random.rand(len(cells)) * 100,
        "experiment": ["expA", "expB"],
    }, index=cells)
    var = pd.DataFrame(index=genes)

    adata = ad.AnnData(X=spliced, obs=obs, var=var)
    adata.layers["spliced"] = spliced
    adata.layers["unspliced"] = unspliced
    adata.raw = adata
    return adata

@pytest.fixture(scope="module")
def tf_list():
    return ["gene1", "gene2"]

@pytest.fixture
def model_input(adata_rna, tf_list):
    return prepare_model_input(
        adata_rna,
        tf_list,
        n_cells_col="n_cells",
        prior_time_col="day_float",
        batch_annotation="experiment",
    )

@pytest.fixture(scope="module")
def dummy_embedding():
    return np.random.normal(size=(2, 16))  # 2 genes × 16-dim embedding

@pytest.fixture(scope="module")
def guide(dummy_embedding):
    return AmortizedNormal(model=model, init_loc_fn=init_to_mean, embedding=dummy_embedding)

@pytest.fixture
def svi_results(guide, model_input):
    guide, svi, svi_state, losses, updated_mi = train_svi(
        model,
        guide,
        model_input=model_input,
        max_iterations=2,
        min_lr=1e-3,
        max_lr=1e-2,
        ramp_up_fraction=0.5,
        log_interval=50,
        cell_batch_size=0,
        region_batch_size=0,
    )
    return guide, svi, svi_state, losses, updated_mi

###############################################################################
# Utility
###############################################################################

def _collapse_to_matrix(arr, n_obs, n_vars):
    """
    Collapse array to (n_obs, n_vars). Supports:
    - (samples, n_obs, n_vars, quantiles)
    - (samples, n_obs, n_vars)
    - (n_obs, n_vars)
    """
    if arr.ndim == 4:
        # Average over sample and quantile dimensions
        arr = arr.mean(axis=(0, -1))
    elif arr.ndim == 3:
        # Average over sample dimension
        arr = arr.mean(axis=0)
    elif arr.ndim == 2:
        return arr
    else:
        raise ValueError(f"Unexpected shape for prediction array: {arr.shape}")

    if arr.shape != (n_obs, n_vars):
        raise ValueError(
            f"Collapsed prediction shape {arr.shape} does not match expected "
            f"({n_obs}, {n_vars})"
        )
    return arr


###############################################################################
# Tests
###############################################################################

@pytest.mark.slow
def test_svi_losses(svi_results):
    _, _, _, losses, _ = svi_results
    assert isinstance(losses, list) and losses

def test_posterior_shapes_and_plot(svi_results, adata_rna):
    guide, svi, svi_state, _, mi = svi_results
    posterior = posterior_module.extract_posterior_estimates(
        model,
        guide,
        svi,
        svi_state,
        quantiles=[],
        modes=[1],
        model_input=mi,
        deterministic_sites=["T_c", "mu"],
    )
    mu_post = posterior["deterministic"]["mu"]
    assert sorted(mu_post.shape[-2:]) == sorted((adata_rna.n_obs, adata_rna.n_vars))



