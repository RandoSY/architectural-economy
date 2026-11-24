# Proposed manuscript extension: Functional Equivalence Mapping (H3-M)

Draft for a future version of Architectural Economy, following Section 7.1 of version 5. No new experimental results are claimed.

## Manuscript-ready subsection: 7.2 — Molecular functional equivalence despite sequence substitution

A more direct molecular test of functional continuity is to distinguish changes in nucleotide sequence from changes in independently measured biological activity. Synonymous coding substitutions can preserve amino-acid identity, while compensatory substitutions and regulatory turnover can preserve aspects of function even when molecular components differ. The PDP-8 analogy is an invariant functional interface rather than invariant circuitry: multiple implementations can satisfy the same operational requirements.

For noncoding regulatory elements, functional equivalence can be evaluated by comparing orthologous and reconstructed ancestral sequences in standardized reporter assays. Klein et al. (2018) measured 5,426 present-day and reconstructed ancestral sequences drawn from 344 successfully assayed human-active enhancer tiles in HepG2 cells. Whalen et al. (2023) investigated human-accelerated regions and identified substitutions with opposing predicted regulatory effects, with experimental reporter-assay evidence consistent with compensation. These studies establish precedent for the sequence–function distinction; the existence of such substitutions is not a new discovery of this paper.

We propose Functional Equivalence Mapping (FEM), a descriptive framework for identifying sequence-divergent implementations that retain activity within prespecified equivalence limits, and for subsequently testing whether independent measures of architectural organization predict this tolerance. Its molecular component (H3-M) is subordinate to H3, not a replacement for the network-level hypothesis. Molecular equivalence in a reporter assay does not establish equivalence of endogenous gene regulation, developmental outcomes or organisms. Nor does a null difference demonstrate equivalence.

## First experiment — Primate enhancer activity

- Primary source: Klein JC et al. (2018), Genome Biology 19:99, https://doi.org/10.1186/s13059-018-1473-6. Additional file 2, Table S4, contains ortholog scores. Retrieve sequence alignments and replicate-level measurements or count data from the linked source resources, including BioProject PRJNA454716, and verify identifiers. The summary table alone may not support formal equivalence testing.
- Replication and mechanistic follow-up: Whalen S et al. (2023), Neuron, https://pubmed.ncbi.nlm.nih.gov/36640767/ ; GEO GSE110760. Human and chimpanzee neural progenitor cell reporter measurements; determine which variant combinations are actually assayed before inferring compensation.

1. Freeze cohort, sequence alignment policy, missing-data handling, activity and precision filters, and a biologically meaningful equivalence margin before testing.
2. Measure nucleotide divergence as substitutions per aligned comparable base; handle indels separately. Compare activity differences in log2 reporter enrichment in a common assay context.
3. Use replicate-aware uncertainty. Classify pairs as functionally equivalent only if an appropriately constructed equivalence interval falls within the prespecified margin (e.g., TOST); classify convincing differences separately and keep inconclusive results distinct.
4. Estimate the fraction of divergent, active sequences retaining activity, with uncertainty clustered by enhancer/tile and accounting for phylogenetic dependence. Compare with matched controls and a prespecified sequence–activity baseline. Do not generalize the ascertained human-active sample to the entire genome.
5. Test the stronger architectural proposition only where independent measures of motif redundancy, shared regulatory dependencies, or buffering are available. Ask whether they improve held-out prediction beyond sequence divergence, baseline activity, length, assay context, and phylogeny. Avoid using the same response data to define predictors and evaluate their performance.
6. For candidate compensation, compare measured ancestral, individual-substitution and combined-substitution constructs where available. Restoration of activity in the combined construct supports compensation; opposing individual effects alone need not demonstrate nonadditive epistasis. Without appropriate constructs, treat compensation as a candidate explanation only.

## Decision criteria

- Molecular equivalence in divergent sequences is evidence of assay-level continuity, not of architectural causation.
- Failure of architecture-based predictors to improve reproducible out-of-sample prediction counts against the stronger explanatory claim.
- Inadequate replicate uncertainty or low precision makes equivalence unresolvable, not disproven.
- Report negative and inconclusive results alongside positive examples.

## Proposed figure

Plot aligned sequence divergence (x) against absolute log2 activity difference (y). Show prespecified equivalence boundary, uncertainty and distinct categories for equivalent, different and inconclusive pairs. Label illustrative examples as such until real data are analyzed. Follow with a small ancestral-to-descendant activity trajectory panel and a compensation panel only where supported by measured constructs.

## References

Klein JC et al. Functional characterization of enhancer evolution in the primate lineage. Genome Biology. 2018;19:99. doi:10.1186/s13059-018-1473-6.

Whalen S et al. Machine learning dissection of human accelerated regions in primate neurodevelopment. Neuron. 2023. PMID:36640767.

Lakens D. Equivalence tests: a practical primer for t tests, correlations, and meta-analyses. Social Psychological and Personality Science. 2017. doi:10.1177/1948550617697177.

The enduring property of a complex system may reside not in the permanence of its components, but in the continuity of their coordination.
