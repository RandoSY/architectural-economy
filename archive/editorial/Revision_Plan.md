# Architectural Economy: Revision Plan, Related Work, and H2 Pilot

Prepared for Randall S. Young, 24 November 2026. Working notes for revising the v3 preprint candidate, "Architectural Economy in Biological and Technological Systems."

*Note: citations in the related-work draft are from recall. Check every one against its source before it goes into the manuscript.*

## 1. Revision plan

### Before you post the preprint (a week or so)

1. Regenerate Figures 7-9 directly from code as plain plots, and redraw the schematics by hand. Drop the "AI-assisted illustration" labels from the data figures.
2. Remove the to-do text from the declarations ("the author must review...", "\[Author to confirm\]").
3. Push the repository, mint a Zenodo DOI, and put it in the paper.
4. Verify all 30 references against the sources, starting with \[17\] and the turnover citations in Section 7.
5. Add the related-work section below.
6. Add sensitivity sweeps for Benchmark A (library size 8/16/32/64, Zipf exponent) and a one-paragraph acknowledgment that blast radius under shared reuse is close to analytic.

### Before journal submission

7. Run the H2 pilot (section 3) and report it whatever it shows.
8. Tighten the framing: lead with H2, and shorten the PDP-8 material. Consider splitting the PDP-8 trade-off into its own paper.
9. Get two or three informal reads, ideally one comparative genomicist and one reliability engineer.

### Optional

10. Stratify the PDP-8 fault sites by role (routine, wrapper, I/O) and separate missing from incorrect outputs. You already flag this as future work, and it would answer the "wrapper vulnerability" point properly.

## 2. Related-work section (draft)

**Related work.** The tension between economy through reuse and fragility through shared dependence has a long history in engineering and systems biology. In reliability theory, von Neumann's analysis of building reliable organisms from unreliable components (1956) already established that redundancy requires coordinating machinery, such as voters, that is itself a failure point. In complex-systems theory, highly optimized tolerance (Carlson & Doyle, 1999; 2002) and the bow-tie architectures of Csete & Doyle (2002) describe systems that are robust to anticipated perturbations yet fragile to rare or structural ones; Doyle & Csete (2011) generalize this to architecture-constraint-behavior trade-offs. Kitano (2004) and Wagner (2005; 2008) relate robustness to evolvability in biological networks, and Hartwell et al. (1999) argue for modular organization as a unit of biological explanation.

In network biology, the closest antecedent to H2 is the centrality-lethality hypothesis, which holds that highly connected nodes are more likely to be essential (Jeong et al., 2001). Subsequent work has shown that the relationship is real but modest and partly confounded (Hahn & Kern, 2005; Zotenko et al., 2008), which motivates our emphasis on confounder control. At the regulatory level, Davidson and Erwin (2006) proposed that deeply conserved kernels resist evolutionary change, and Singh and Yi (2021) showed that enhancer pleiotropy correlates with sequence conservation. Our contribution is narrower: we ask whether *higher-order* downstream reach, moderated by local buffering, explains constraint beyond direct target number, tissue breadth, and target-gene identity.

Two bodies of work temper the prediction. First, the cost-of-complexity literature (Fisher, 1930; Orr, 2000) and genomic analyses of pleiotropy (Wang et al., 2010) suggest that fitness effects of pleiotropy need not scale linearly with the number of affected traits. Second, shadow enhancers confer phenotypic robustness (Hong et al., 2008; Frankel et al., 2010; Perry et al., 2010; Osterwalder et al., 2018) and are pervasive in developmental networks (Cannavò et al., 2016), yet their sequences are often individually constrained, and regulatory function can persist despite binding-site turnover (Ludwig et al., 2000; Odom et al., 2007; Villar et al., 2015). These findings make the sign and size of the buffering interaction (β4) an open empirical question rather than a settled one.

Finally, our computational benchmarks relate to earlier comparisons of regulatory networks with software systems (Yan et al., 2010; Istrail et al., 2007). We use them to illustrate and bound the reuse-liability trade-off within explicit models, not to infer biological mechanism.

*Two tweaks:* Carlson & Doyle's 2002 PNAS paper is "Complexity and robustness." Ludwig et al. (2000) is the *Nature* paper on stabilizing selection in the *even-skipped* stripe 2 enhancer.

## 3. Minimal pilot for H2

The goal is the smallest analysis that could plausibly show an effect, run in one cell line with public data on a laptop.

### Data (all public)

- **Elements and targets:** ABC enhancer-gene predictions for K562, with CRISPRi-validated pairs (Fulco 2019, Gasperini 2019) as a high-confidence subset.
- **B (downstream reach):** genome-scale K562 Perturb-seq (Replogle 2022). For each target gene g, count genes or modules significantly changed when g is knocked down.
- **R (buffering):** summed *raw* activity × contact of other ABC enhancers for the same gene. Raw, not normalized, as the manuscript already specifies.
- **T (breadth):** number of biosamples where the element is an active ENCODE distal cCRE.
- **Outcome:** mean Zoonomia phyloP over the element, excluding exonic and promoter overlaps, with a GC- and mappability-matched local background for comparison.

### One design problem to settle first

If B is defined as the reach of the target gene, it is constant across enhancers of the same gene. So in a single cell line, the within-gene model can only test R. Run the between-gene mixed model as the primary analysis and keep within-gene as a secondary test of R and the interaction. State this up front, because it is exactly what a reviewer will notice.

### Confounds to control beyond the current list

- Target expression level and CRISPRi knockdown efficiency. Both inflate detectable downstream effects.
- Perturb-seq coverage bias: genes that can be perturbed and detected are expressed and strongly acting.
- Target-gene constraint (LOEUF) and transcription-factor status, as already specified.

### Models

Fit the M0, M1, M2 ladder as a gene-random-intercept mixed model. Evaluate on held-out chromosomes, and use genomic-block bootstrap for uncertainty. Add a permutation null that shuffles B among genes matched on expression and LOEUF.

### Before touching the real data

- Preregister (OSF) the primary prediction (β1 > 0, β4 < 0), the thresholds, and the decision rule.
- Run a power simulation using the `validation_v3.py` fixtures with plausible effect sizes. Per-enhancer phyloP is noisy, so declare the minimum detectable effect in advance. If power is low, say so and call the study exploratory.

### Decision rule

A well-powered null or reversed sign counts against H2, and low power or poor proxy validity is reported as inconclusive. Either outcome is publishable, which is what makes this worth doing.

### Effort

Roughly two to four focused weekends. The tools are Python, pandas, pyBigWig, bedtools, and statsmodels. The slow part is harmonizing enhancer-gene maps with the Perturb-seq gene IDs.
