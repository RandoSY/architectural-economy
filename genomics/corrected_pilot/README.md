# Corrected H2 exploratory pilot — 24 November 2026

Supersedes the earlier invalid hg19-as-hg38 conservation analysis. Input BED and conservation records were supplied after CrossMap conversion. The mapping is internally consistent, but the chain conversion and BigWig extraction have not been independently repeated here. The original cohort was assembled without using conservation scores.

Reproduce using Python 3 with pandas, numpy, scipy, statsmodels: `python reproduce.py`.

Primary complete-case set: 636 regions, 408 target genes. Gene-clustered OLS; log-transformed reach and standardized predictors. The seven baseline terms are region length, distance, activity, direct target count, perturbed cell count, UMI count and residual expression. No cross-context breadth, GC, neutral mutation rate, LOEUF, or independent expression controls. The ABC buffering proxy is thresholded and not experimentally verified. Results are exploratory, not preregistered or confirmatory.

Primary H2 reach and interaction coefficients do not support the predicted signs and are not significant. Held-out chromosome MSE worsens when architectural terms are added. Excluding the one unchanged coordinate does not alter the conclusion. The within-gene R term is nominally significant (p=.046) but reverses sign and is nonsignificant (p=.129) when focal ABC numerator is included; therefore not robust. The gene's reach is invariant within a single context, so the within-gene model cannot estimate its main effect.

Included: original cohort CSV, original and corrected BED, corrected conservation TSV, mapping checks, analysis source and outputs. Source cohort creation and original upstream public datasets are in the project research archive / stage 2 resources, not duplicated in this compact package. Do not use prior incorrect conservation data in publication.
