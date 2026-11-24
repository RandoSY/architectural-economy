# Artificial Intelligence as an Experimental Model of Biological Evolution

*Investigating architectural invariance, functional equivalence and compensatory adaptation*

**Randall S. Young — Independent researcher — ORCID [0009-0003-1657-0243](https://orcid.org/0009-0003-1657-0243)**

Concept record 1.0 · 24 November 2026 · Proposed second paper · Not peer reviewed

Readable Markdown edition of the four-page research prospectus; typography and conceptual diagram are adapted for GitHub. The original PDF has not yet been transferred.

> Reverse the direction of inquiry.
>
> Use the architecture and controlled evolution of artificial intelligence to discover principles that may illuminate the evolution of biological systems.

## Executive synopsis

The foundational Architectural Economy paper (version 7) uses the PDP-8 family to illustrate a stable functional architecture across changing physical implementations. Its computational experiments identify resource–dependency trade-offs; its corrected exploratory genomic pilot did not support the predicted association between regulatory reach and sequence conservation. The next investigation moves from historical analogy to a manipulable experimental system: artificial neural networks.

Artificial networks can be inspected, perturbed, compressed, retrained and reorganized at controlled cost. They offer a way to measure the extent to which different implementations realize equivalent functions, identify mechanisms that permit such continuity, and test whether those mechanisms predict independently measured biological behavior.

| 01 HISTORY | 02 EXPERIMENT | 03 VALIDATION |
|---|---|---|
| PDP-8 | Artificial networks | Biological systems |
| Compatible instructions | Testable substitution | Independent evidence |

Conceptual research sequence; cross-domain transfer remains to be tested.

### Publication decision

Preserve version 7 as the foundation. Develop the AI investigation as an independent paper, with its own evidence, methods, limitations and reproducible archive. Cross-reference the two papers rather than treating the new hypothesis as a finding already established by the first.

## The scientific proposition

**H4 — Cross-domain architectural invariance.** Architectural properties that explain functional continuity under substitution in artificial networks may also predict functional continuity in biological regulatory systems. The objective is predictive transfer, not a claim that artificial and biological machinery are identical.

| AI experimental analogue | Biological comparison | Boundary of the analogy |
|---|---|---|
| Hardware/backend migration | Different molecular implementations | Execution hardware is not a genome. |
| Parameter or edge substitution | Changes in regulatory strengths or connections | Weights are not nucleotide sequences. |
| Pruning and redundancy | Loss and buffering of regulatory elements | Deletion is not necessarily neutral. |
| Distillation and module replacement | Alternative mechanisms preserving an output | Training is not biological reproduction. |
| Compensatory adjustment | Compensatory evolution / epistasis | Test interactions, not just final performance. |

### Three distinct levels of change

**Physical substrate.** Run the same model on different backends to measure numerical and task-level compatibility. This is the closest counterpart to the historical PDP-8 example. **Representational implementation.** Change precision, parameters or architecture and measure behavior. **Evolutionary process.** Introduce explicit variation, inheritance and selection in simulated populations; ordinary gradient training is not equivalent to Darwinian evolution.

### Falsifiable predictions

- **H4a — Tolerance:** at comparable cost and baseline performance, some network organizations preserve outputs under larger controlled changes.
- **H4b — Compensation:** constrained secondary changes restore function after primary perturbations more often than matched random controls.
- **H4c — Transfer:** architectural measurements improve held-out biological predictions over sequence, baseline activity and other conventional predictors.

Null, reversed or context-dependent effects are meaningful results. Similar outcomes alone do not demonstrate shared mechanisms; each hypothesis must be evaluated separately.

## The first experiment

Begin with small, transparent networks that can be trained and tested on ordinary computing hardware. A controlled multi-output task with reusable latent subfunctions is preferable to a single benchmark score because it exposes the cost of shared dependencies.

| Stage | Proposed protocol |
|---|---|
| 1 · Establish baseline | Train shared-trunk, dedicated-branch and modular/buffered variants. Match baseline performance and parameter or compute budgets; report both when exact matching is impossible. Repeat across independent seeds. |
| 2 · Introduce change | Sweep normalized weight perturbations, edge removals and module substitutions at multiple severities. Separate inference-only tests from retraining and recovery experiments. |
| 3 · Test compensation | Apply a fixed secondary-adjustment budget after each primary intervention; compare to random changes and equal-budget retraining controls. Retain unmodified and sham-perturbation baselines. |
| 4 · Measure continuity | Evaluate held-out input/output behavior, per-task degradation, dependency blast radius, recovery cost and robustness under shifted input conditions. |
| 5 · Test generality | Repeat on a different task and architecture. Report uncertainty across training seeds, not treating individual test inputs as independent trained models. |

### A portable functional equivalence framework

Define implementation distance D_I using a domain-appropriate perturbation measure and functional distance D_F using a prespecified response discrepancy. Classify equivalence only when uncertainty in D_F lies within a justified tolerance. Plot D_F against D_I; distinguish equivalent, different and inconclusive cases. Different domains need not share the same distance scale.

Key outcomes: tolerance curve; proportion of equivalent variants at a given perturbation severity; number of outputs disrupted by an intervention; recovery improvement per unit adjustment cost. Keep resource cost separate from function rather than imposing an arbitrary composite score.

Decision gate: if architecture does not explain reproducible tolerance beyond controls, revise or reject H4a/b before attempting cross-domain prediction. No experiment described here has yet been executed.

## From AI to biological evidence

### Research roadmap

1. **Structured literature review.** Search neural-network pruning, distillation, model stitching, robustness, neuroevolution, developmental system drift and compensatory evolution. Record search strings, databases, inclusion criteria and extraction schema. Conduct quantitative meta-analysis only for sufficiently comparable outcomes; otherwise use a structured evidence synthesis.
2. **Computational laboratory.** Execute the controlled pilot above. Release scripts, seeds, environments, benchmark definitions, raw outputs, figures and negative results. Test whether the architecture effects persist under alternative fault and resource models.
3. **Independent biological validation.** Start with public primate enhancer sequence–activity data [5]; pursue matched perturbation datasets to investigate regulatory dependencies. Test whether independently measured architecture features improve predictions beyond activity, sequence divergence, assay context and phylogeny. Do not infer organism-wide equivalence from a reporter assay.

### Preserve the intellectual estate for future AI

The archive should function as a restartable research program rather than merely a published result. A future, more capable AI may automate literature synthesis, explore larger architectures, improve causal inference, propose experiments and challenge the original assumptions. Such capabilities and discoveries are possibilities, not guarantees.

> Future handoff: preserve the question, operational definitions, source data, code, failures, decision gates and provenance. Require a future investigator to reproduce prior results and document disagreements before extending the theory.

Suggested repository: a separate companion repository cross-linked to the foundational Architectural Economy archive. Use a versioned README, research protocol, references, experiments, results, negative-results log and AI handoff notes. No new repository or experiments are claimed by this prospectus.

### Selected starting references

1. Hinton G, Vinyals O, Dean J. Distilling the Knowledge in a Neural Network (2015). [arXiv:1503.02531](https://arxiv.org/abs/1503.02531).
2. Frankle J, Carbin M. The Lottery Ticket Hypothesis (ICLR 2019). [arXiv:1803.03635](https://arxiv.org/abs/1803.03635).
3. Bansal Y, Nakkiran P, Barak B. Revisiting Model Stitching to Compare Neural Representations (NeurIPS 2021). [arXiv:2106.07682](https://arxiv.org/abs/2106.07682).
4. McColgan Á, DiFrisco J. Understanding developmental system drift. Development (2024). [doi:10.1242/dev.203054](https://doi.org/10.1242/dev.203054).
5. Klein JC et al. Functional characterization of enhancer evolution in the primate lineage. Genome Biology (2018). [doi:10.1186/s13059-018-1473-6](https://doi.org/10.1186/s13059-018-1473-6).

---

Archive note: original four-page PDF, `AI_as_a_Laboratory_for_Biological_Evolution_Research_Prospectus.pdf` (91,090 bytes). SHA-256: `5b7fed98fd7de89585f351b9b8aac3e1229fb9523e1538a5a1e9046ca5f9d81a`. PDF binary pending transfer. The foundational paper is preserved at [version 7](../../publication/Architectural_Economy_v7.txt).