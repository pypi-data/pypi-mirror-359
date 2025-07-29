# models

- RNA_1layer_simple - the simplest implementation of dynamical transcription + measurment model, using a 1 layer neural net to link spliced counts to the transcription rate
- RNA_1layer - a more complex model including latent protein levels, NB instead of Poisson distribution for the likelihood etc. , but still just a 1 layer NN to for the transcription rate
- RNA_1layer_constantDiffusion - base stochastic model in diffrax, consisting of RNA_1layer model with a constant diffusion term added.
- RNA_1layer_constantDiffusion_LogNormal - extension to base stochastic model that replaces gamma distributions with LogNormal and other minor adjustments for numerical stability
- ATAC_RNA - base model for joint ATAC+RNA data, using a mechanistic model of TF binding to DNA regions (using prior knowledge about motifs and genomic distances) to link latent protein levels to the transcription rate.
- RNA_1layer_ManualEuler - an implementation of the RNA_1layer model that uses a manual implementation of Euler integration in JAX, rather than the diffrax version. This improves training speed.
- RNA_1layer_ManualEuler - a two instead of one layer neural net for the transcription rate, improves fit to data and ability to describe all gene expression patterns, even with a small number of TF inputs.
- RNA_1layer_constantDiffusion - base stochastic model consisting of RNA_1layer_simple model with a constant diffusion term added.
- RNA_2layers_ManualEuler_MultiplePaths_Enumeration - A 2 layer neural net describes the transcription rate regulation for each path, where the path identity is assigned to cells with a categorical variable, suitable for inference via Enumeration
- RNA_2layers_ManualEuler_MultiplePaths_SoftWeights - A 2 layer neural net describes the transcription rate regulation for each path, where the path identity is assigned with a continuous weight, so that inference via Enumeration is not necessary.
- RNA_2layers_MultiplePaths_SDE - A 2 layer neural net for the transcription rate, with independent SDE noise realizations learned for each path to ensure divergence into different terminal states.
- RNA_4layers_MultiplePaths_ODE - A 4 layer neural net for the transcription rate, with deterministic dynamics and independent initial conditions for each path that ensure divergence into different terminal states.
  