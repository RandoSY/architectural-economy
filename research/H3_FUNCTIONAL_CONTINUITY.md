# H3 — Functional continuity research roadmap

Proposed exploratory follow-up to version 5, 24 November 2026. No new H3 results are claimed.

## Motivation
H1: reuse trades implementation cost against dependency and coordination liability in specified computational models.
H2: the corrected K562 pilot (636 regions, 408 target genes) did not support the predicted relationship between downstream regulatory reach and nucleotide constraint. This does not establish H3.
H3: test whether independently defined functional modules retain comparable input-response behavior across species even when individual response components differ.

## First experiment
Use Hagai et al., Nature 2018, DOI 10.1038/s41586-018-0657-2. Start with bulk RNA-seq of LPS-stimulated mononuclear phagocytes in mouse, rat, rabbit and pig. Obtain processed expression, sample metadata, biological replicate identifiers and ortholog mapping from the authors' public resources (https://github.com/Teichlab/innate_evo). Verify accessions and metadata before analysis. Do not mix cell types or stimuli.

1. Freeze inclusion rules, matched time points, module definitions, preprocessing and effect-size thresholds before testing. Use independently annotated pathways (e.g. Reactome), not modules optimized on the comparison being evaluated.
2. Estimate within-species stimulated-versus-baseline log fold changes with replicate uncertainty. Use the same observation times and comparable conditions; retain response magnitude and direction.
3. Quantify cross-species agreement of individual ortholog responses, module response trajectories, peak timing and activation order. Gene orthology is used for correspondence; no enhancer sequence conservation score enters the primary test.
4. Compare module-level agreement to size-, expression-, detectability- and response-magnitude-matched random gene sets; compare same-species replicate reliability as a ceiling. Account for phylogenetic dependence and uncertainty, and test transfer to a held-out species. Treat four species as limited comparative sampling, not independent species-pair replicates.
5. Report null, mixed and positive results; a broad shared immune response alone does not demonstrate conserved causal architecture.

## Stronger second experiment
Compare responses to matched orthologous regulator perturbations across species, where data permit. Quantify preservation of module-level causal response fingerprints, including loss and recovery if measured. Explicitly distinguish measured dependence from co-expression.

## Link back to architectural economy
Test whether independently measured reuse, downstream dependency and buffering predict preservation of functional response beyond matched expression, module size, and direct regulatory importance. This requires suitable independent perturbation and regulatory mapping datasets. It is not established by the first experiment.

## Precedents
- Hagai et al. (2018), https://doi.org/10.1038/s41586-018-0657-2
- Berthelot et al. (2018), https://doi.org/10.1038/s41559-017-0377-2
- Comparative Analysis of Immune Cells Reveals a Conserved Regulatory Lexicon (2018), https://doi.org/10.1016/j.cels.2018.01.002
- Enhancer turnover and conserved regulatory function in vertebrate evolution (2013), https://doi.org/10.1098/rstb.2013.0027

The potential contribution is incremental explanatory power of architecture-based measures, not the already-established existence of conserved regulatory outputs.
