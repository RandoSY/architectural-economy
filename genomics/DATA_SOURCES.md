# Section 6.2 Empirical Pilot — Public Data Sources & Schema Guide

`genomics/section6_2_pilot.py` is designed to accept a single harmonized enhancer-level CSV table built strictly from **publicly available, conservation-free predictors** (plus Zoonomia mammalian constraint strictly as the outcome variable).

## Public Data Sources (GRCh38)

1. **Outcome — Mammalian Sequence Constraint (`constraint_phyloP`):**
   - **Zoonomia 240-mammal phyloP (GRCh38):** `241-mammalian-2020v2.bigWig` (Zoonomia Consortium, *Science* 2023 [4]; UCSC Genome Browser / Cactus alignment hub).
   - Compute mean (and 90th-percentile sensitivity check) phyloP across each candidate enhancer interval after excluding all GENCODE exonic and ±10 bp splice-site overlaps.
2. **Candidate Cis-Regulatory Elements & Activity Breadth (`T_breadth`, `chromatin_act`):**
   - **ENCODE Registry of cCREs (v3/v4, GRCh38):** `GRCh38-cCREs.bed` (ENCODE Project Consortium, *Nature* 2020 [14]; SCREEN portal).
   - `T_breadth` = count of distinct biosamples in which the enhancer meets active dELS/pELS chromatin thresholds.
3. **Enhancer–Gene Links & Local Buffering (`target_gene`, `direct_targets`, `R_buffering`):**
   - **ENCODE-rE2G / Fulco et al. Activity-by-Contact (ABC) predictions (K562 & multi-biosample):** Fulco et al., *Nat Genet* 2019 [12] & ENCODE-rE2G public portal.
   - `R_buffering` = sum of ABC scores of *other* co-active enhancers mapped to the same `target_gene` in the same context(s), excluding enhancer $e$ itself.
4. **Higher-Order Downstream Reach (`B_reach`):**
   - **Replogle et al. K562 Genome-Scale Perturb-seq** (*Cell* 2022) or independent experimental TF–target regulons (e.g., ENCODE ChIP-seq + Perturb-seq DEG co-expression modules).
   - **Leakage rule:** Never include motif-conservation or phyloP-filtered edges when constructing the downstream graph $G(c)$.
5. **Target-Gene Covariates (`gene_loeuf`, `gene_is_tf`, `gene_expr_breadth`, `gene_centrality`):**
   - **gnomAD v4** gene constraint table (`lof.oe_ci.upper` = LOEUF).
   - **Lambert et al.** (*Cell* 2018) human transcription factor catalog (`gene_is_tf`).
   - **GTEx v8** tissue expression breadth (`gene_expr_breadth`).

## Expected CSV Columns for `--input-csv`

`enhancer_id, chrom, start, end, target_gene, constraint_phyloP, B_reach, T_breadth, R_buffering, elem_length, gc_content, neutral_rate, align_qual, chromatin_act, log_dist_tss, direct_targets, gene_loeuf, gene_is_tf, gene_expr_breadth, gene_centrality`

## Running the Pipeline

```powershell
# 1. Verify estimator behavior on synthetic confounded-null vs. true-effect dry-runs
python genomics/section6_2_pilot.py --demo-synthetic

# 2. Run on prepared real genomic dataset
python genomics/section6_2_pilot.py --input-csv data/k562_enhancers.csv
```
