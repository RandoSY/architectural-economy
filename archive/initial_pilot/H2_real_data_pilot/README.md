# H2 — real genomic data pilot, stage 1

Status: analysis runner tested on synthetic fixture; no empirical genomic result. Public source records located; network downloads from ChatGPT execution environment failed. This package is not an end-to-end downloader/harmonizer. It requires the prepared input table below. Do not treat the software check as evidence for H2.

## Frozen exploratory scope
K562 single context; human GRCh38, autosomal distal noncoding enhancers. Use 0-based half-open coordinates. Use original experimental perturbation statistics as the preferred reach metric. H2a: larger gene-level perturbation reach predicts enhancer constraint after adjustment (between genes). H2b: the reach-by-buffering interaction is negative. The within-gene secondary model estimates buffering and its interaction with gene-level reach, not the reach main effect. This is an observational association, not a causal inference and not the full multicellular developmental H2.

## Public inputs
- Replogle et al., Cell 2022, doi:10.1016/j.cell.2022.05.013. Supplemental differential-expression Anderson–Darling p-values: https://doi.org/10.25452/figshare.plus.21632564 ; normalized pseudobulk data: https://doi.org/10.25452/figshare.plus.20029387 . Use K562 genome-wide dataset; do not combine essential-screen and genome-wide counts. Obtain target expression, knockdown and cell-count metadata from matching screen. Count non-target responding genes at per-perturbation BH FDR 0.05, with fixed expressed-gene universe; compare threshold sensitivity and a noise-adjusted transcriptome-wide effect metric. Missing perturbation is not zero reach. Alternative summary (not identical to reach): https://zenodo.org/records/21631935/files/RMS_combined_output.csv.gz?download=1 ; requires inspection of metric and screen before use.
- ABC: https://osf.io/uhnb4/ (Fulco 2019; hg19), https://www.engreitzlab.org/resources/ (Nasser 2021; full predictions). Use full, unthresholded K562 candidate links for raw alternative activity×contact totals. Lift hg19 coordinates with explicit chain and reject ambiguous/failed lifts; no mixing genome builds. Require independent CRISPRi validated links as secondary subset. Avoid conservation-derived features in selection. Record assembly and source version.
- Zoonomia UCSC GRCh38: https://hgdownload.soe.ucsc.edu/goldenPath/hg38/cactus241way/cactus241way.phyloP.bw . Mean per-base signed phyloP on finite positions; record coverage. Prefer pyBigWig range access on a network-enabled Linux machine, or local download. Do not fill missing bases with zero.
- ENCODE SCREEN: https://screen.wenglab.org/ ; use versioned registry and biosample-specific distal enhancer activity matrix, overlap with ABC intervals by a prespecified rule (e.g. >=50% reciprocal overlap, sensitivity check). Count distinct measured biosamples; record assay coverage.
- gnomAD: https://gnomad.broadinstitute.org/downloads ; versioned gene LOEUF. Human TF list Lambert et al. 2018; GTEx expression breadth https://gtexportal.org/ . Use stable Ensembl IDs and log all mappings/drops; derive centrality independently of conservation.
- GENCODE GRCh38 gene annotations https://www.gencodegenes.org/human/ ; exclude promoter (predefine ±2 kb from any TSS), exon and splice overlaps. Compute GC from reference, alignment coverage and independently estimated local neutral substitution rate; choose neutral sites without using enhancer outcome scores to filter predictors. Match local comparison intervals by GC and mappability; this matched analysis is a planned extension, not implemented here.

## Required harmonized CSV schema
One row per unique enhancer (primary target chosen without reference to phyloP); maintain all original links in a separate audit file. Cis links only. Columns:
```
enhancer_id,target_gene,chrom,start,end,constraint_phyloP,B_reach,T_breadth,R_buffering,elem_length,gc_content,neutral_rate,align_qual,chromatin_act,log_dist_tss,direct_targets,gene_loeuf,gene_is_tf,gene_expr_breadth,gene_centrality,gene_expression,knockdown_efficiency,perturbed_cells
```
B_reach = gene-level response count (identical within gene). R_buffering = log1p(sum of raw activity×contact of other co-active distal enhancers linked to same gene), not sum of normalized ABC scores; proxy only, not experimentally demonstrated redundancy. T_breadth = number of active biosamples. Other fields correspond to Section 6.2 plus expression, knockdown and cell count. Retain original values and transform definitions. Use unique IDs; exclude ambiguous mapping in primary analysis, then sensitivity analysis with multi-target model. Before running, record frozen inclusion criteria and source URLs, versions, SHA256, genome assembly, mapping/drop counts, code version, exact definitions and known limitations in manifest.json. Do not use placeholders for absent covariates or fabricate values.

## Run
```
python -m pip install -r requirements.txt
python run_h2.py --self-test --out synthetic_test.json
python run_h2.py --input k562_enhancers.csv --manifest manifest.json --out real_results.json
```
The runner uses nested OLS with target-locus block-clustered uncertainty (exploratory alternative to proposed mixed model/block bootstrap), fold-local scaling, leave-one-chromosome-out prediction, and held-out within-gene contrasts. Fixed effects are demeaning and cannot predict absolute values for new genes. 5 Mb blocks are assigned using median enhancer position per gene, not true TSS, a limitation. The permutation null, power simulation, matched backgrounds, mixed-effects model and robustness analyses remain to be implemented before confirmatory interpretation. Review missingness, sample composition, effective gene counts, cluster count, model rank, uncertainty and predictive gain. Do not infer biological validity from a successful run.

## Decision criteria to preregister before observing outcomes
Positive reach coefficient and negative interaction with sufficiently precise intervals, improved held-out error over M1, robustness to thresholds and independent perturbation measures are supportive of the operationalized H2, not proof. A sufficiently powered null or reverse sign weakens it; low power, poor coverage or invalid proxies are inconclusive. Report all outcomes. One leukemia cell line cannot establish a universal principle of genome evolution.
