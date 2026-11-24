# Architectural Economy — Revised Manuscript & Computational Benchmarks

This project contains the revised manuscript (**v2**) and fully reproducible computational benchmarks testing **Section 6.1 (Hypothesis H1)** of *Architectural Economy in Biological and Technological Systems*.

## Project Structure

- `manuscript/Architectural_Economy_v2.pdf` — Publication-formatted 15-page PDF with all 8 embedded figures, shaded tables, equations, running headers/footers, and fixed references.
- `manuscript/Architectural_Economy_v2.docx` — Native Microsoft Word document (with OMML equations, styled tables, running headers/footers, and all 8 embedded figures).
- `manuscript/architectural_economy_v2.md` — Master Markdown source for v2.
- `simulations/synthetic_networks.py` — 30-seed controlled comparison of matched multi-output combinatorial networks (`dedicated`, `shared`, `modular_shared`, `modular_buffered`) across $K \in \{4, 8, 12, 16, 24, 32\}$.
- `simulations/pdp8_benchmark.py` — Cycle-accurate 12-bit DEC PDP-8 emulator executing $N \in \{1, 2, 4, 8, 16, 32, 64\}$ bit-exact-verified shift-and-add multiplication tasks across `inlined`, `shared`, `dual_modular`, and `buffered_tmr` architectures with exhaustive single-word routine fault injection.
- `simulations/generate_schematics.py` & `simulations/plot_figures.py` — Generate all 8 publication-ready figures (`figures/fig1_...` through `figures/fig8_...`).
- `build/export_documents.py` — Exports both `Architectural_Economy_v2.pdf` (ReportLab) and `Architectural_Economy_v2.docx` (Pandoc + OOXML styling).
- `genomics/section6_2_pilot.py` & `genomics/DATA_SOURCES.md` — Starter comparative-genomics empirical pipeline implementing the nested `M0 -> M1 -> M1b -> M2 -> M2b` ladder, within-target-gene fixed effects, leave-one-chromosome-out CV, and 1 Mb genomic-block bootstrap CIs.
- `results/` — Raw JSON output tables (`synthetic_networks.json`, `pdp8_benchmark.json`, `section6_2_pilot_verification.json`).
- `figures/` — Publication-ready 220–240 DPI PNG figures (Figures 1–8).

## Reproduce All Results, Figures & Documents

```powershell
python simulations/synthetic_networks.py
python simulations/pdp8_benchmark.py
python simulations/generate_schematics.py
python simulations/plot_figures.py
python build/export_documents.py
python genomics/section6_2_pilot.py --demo-synthetic
```

Requires Python 3.10+, `numpy`, `pandas`, `matplotlib`, `reportlab`, and `pandoc`.
