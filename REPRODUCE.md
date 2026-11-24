# Reproduce the computational evidence

Run from the repository root using Python 3.10+ (audit environment Python 3.13.5, NumPy 2.3.5). Install dependencies with `python -m pip install -r requirements.txt`.

```sh
python simulations/synthetic_networks.py
python simulations/pdp8_benchmark.py
python genomics/section6_2_pilot.py --demo-synthetic
python audit/reproduce_audit.py
python genomics/validation_v3.py
python simulations/generate_schematics.py
python build/plot_figures_v3.py
python build/plot_audit.py
python build/build_v3.py
```

The final command produces the DOCX. Export it to PDF in Word or LibreOffice. The restored Hilbert schematic is supplied in `figures/fig1a_hilbert.png` and its SVG source is preserved at `archive/v1/fig2.svg`.

The benchmark scripts write JSON files in `results/`; run in a clean checkout if comparing against committed results. Numerical differences may occur across library versions. The audit checks functionality of the supplied models, not complete processor fidelity or biological validity. The `validation_v3.py` synthetic fixtures are not genomic evidence. For real input data see `genomics/DATA_SOURCES.md` and the proposed design in section 6.2.

## Version 5 additions

The preceding instructions reproduce the original v3 benchmarks and document generation. For the corrected empirical pilot, install pandas, numpy, scipy and statsmodels and run:

```sh
cd genomics/corrected_pilot
python reproduce.py
```

See that directory's README for limitations and input provenance. The H3 hypothesis is prospective; no empirical H3 results are included. See `build/V5_BUILD_NOTES.md` for document provenance.
