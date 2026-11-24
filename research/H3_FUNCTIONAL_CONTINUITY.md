# The next frontier: continuity of coordination (H3)

**Research agenda following Architectural Economy, v5**  
Randall S. Young · 24 November 2026 · Prospective research, not a report of new findings.

> The enduring property of a complex system may reside not in the permanence of its components, but in the continuity of their coordination.

## The question that survives the experiment

The PDP-8 demonstrates a useful distinction: a stable instruction architecture permits software to operate across changing physical implementations. Our controlled simulations quantify the economies and liabilities of reuse, modularity and redundancy (H1). Our exploratory K562 study, by contrast, found no convincing association between downstream regulatory reach and individual enhancer sequence conservation (H2; 636 regions, 408 genes). That result neither proves functional continuity nor rules out other sequence-level relationships.

The next question is whether the organization of a biological response can be more stable than the molecular elements realizing it—and whether architectural features predict that stability. The existence of conserved biological outputs is established in prior work; the potential contribution is a predictive, perturbation-based account of their continuity.

## Four propositions, four tests

| Proposition | Observable test | Evidence against the proposition |
|---|---|---|
| H3a — Functional continuity | Independently defined functional modules show greater cross-species response agreement than matched control gene groups. | No reproducible module-level advantage above matched controls. |
| H3b — Temporal continuity | Relative activation order and response trajectories remain similar under matched stimuli. | Timing agreement is no better than matched null models, within measurement resolution. |
| H3c — Dependency continuity | Equivalent regulator perturbations produce similar module-level response fingerprints even where individual gene responses differ. | Causal response fingerprints diverge beyond prespecified tolerance. |
| H3d — Architectural explanation | Independently estimated modularity, reuse and buffering improve held-out prediction of functional continuity beyond conventional biological covariates. | No incremental predictive value or unstable effects on replication. |

H3a/b concern observed behavior; H3c requires interventions; H3d is the strongest and most distinctive test of the architecture-based explanation. A positive result at one level does not establish the next.

## Study 1 — A biological compatibility test

Use the published cross-species immune-response study of Hagai et al. (Nature, 2018). The phagocyte arm contains LPS-stimulated mouse, rat, rabbit and pig cells. Single-cell time points include untreated, 2, 4 and 6 hours; the bulk phagocyte comparison has 0 and 4 hours. Start with the processed single-cell counts for trajectories, and use bulk data for an independent measurement modality where matched.

- Paper: https://doi.org/10.1038/s41586-018-0657-2
- Data: https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-6754
- Authors' analysis code: https://github.com/Teichlab/innate_evo
- Potential independent replication: https://pmc.ncbi.nlm.nih.gov/articles/PMC7386301/

**Protocol (before examining outcomes):**
1. Verify sample identities, cell type, stimulus, time points, ortholog mappings, donor/replicate structure and data reuse conditions. Do not treat individual cells as independent organisms. If replication is inadequate, report descriptive results only.
2. Freeze inclusion criteria, independent pathway definitions, gene universe, normalization, effect-size thresholds, equivalence tolerances and missing-data handling. Record the protocol and input checksums.
3. Estimate within-species responses to LPS relative to baseline, using donor/sample-level pseudobulk where possible. Retain direction, magnitude and uncertainty. Match measurement times and cell populations.
4. Compare gene-level and independently annotated module-level response trajectories. Report response agreement, magnitude differences and activation-order agreement separately; do not equate correlation with identical output.
5. Use null gene sets matched on size, expression, detectability, ortholog coverage and relevant response characteristics. Account for averaging-induced stability; compare against same-species replicate reliability. Use held-out species or independent datasets for validation, and acknowledge phylogenetic dependence and the small number of species.
6. Publish all results, including disagreements and null effects. Do not use enhancer sequence conservation in the primary test; ortholog correspondence is still required and may use sequence-derived annotations.

A shared response to LPS can arise from different causal mechanisms. This experiment measures functional correspondence, not preservation of internal wiring.

## Study 2 — Perturbation fingerprints

Seek comparable regulator perturbation data across species and matched cell states. For each intervention, estimate a vector of changes in predefined biological modules, including response direction, magnitude and recovery if measured. Compare corresponding perturbations to matched noncorresponding interventions and within-species reproducibility. Define similarity/equivalence criteria in advance. If such datasets do not exist, publish a prospective experimental protocol rather than imply causal evidence.

This is the analogue of running the same diagnostic and fault tests on successive PDP-8 implementations. Similar normal outputs alone are insufficient to establish similar dependency structure.

## Study 3 — Architectural predictors

Use separately measured regulatory connections or perturbation evidence to estimate shared dependencies, effective reach, redundancy and modularity. Model functional continuity as an outcome, with baseline predictors including expression, pathway size, direct target importance, perturbation strength, context and phylogenetic relatedness. Compare baseline versus architecture-augmented models with genuinely held-out data. Avoid deriving predictor and outcome from the same measurements without independent validation or cross-fitting.

This tests whether the engineering framework has explanatory value beyond established biological accounts. Redundancy may introduce coordination vulnerabilities; effects need not be monotonic.

## Study 4 — Generalization and falsification

Replicate in a different biological domain (e.g., homologous developmental cell states). Compare both output conservation and intervention-response conservation where possible. After the primary functional analysis, quantify implementation divergence separately (enhancer turnover or regulatory rewiring). A result independent of sequence scores is not by itself proof that implementation changed.

## Deliverables and decision gates

| Milestone | Deliverable | Decision gate |
|---|---|---|
| A | Versioned protocol, data manifest and reproducible preprocessing | Matched data and replicates established |
| B | Module and gene response plots, matched-null comparisons, uncertainty | Determine whether H3a/b merit replication |
| C | Intervention-response comparison or documented data gap | Determine whether causal dependencies can be tested |
| D | Held-out architectural predictor analysis | Determine whether H3d adds explanatory power |
| E | Independent replication and manuscript supplement | Report positive, mixed, null or inconclusive outcomes |

Do not change primary endpoints after observing results without clearly labeling the change exploratory. Keep all scripts, results, exclusions, provenance and version history in this repository. The Functional Continuity Index is initially a set of separate measurements; introduce a composite only after validation.

**Research principle:** the goal is not to prove an analogy, but to discover where it predicts something measurable that existing explanations do not.
