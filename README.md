# Architectural Economy in Biological and Technological Systems

**Randall S. Young — Independent Researcher**  
ORCID: [0009-0003-1657-0243](https://orcid.org/0009-0003-1657-0243)

*A hypothesis for the evolutionary conservation of genomic regulatory information: from the PDP-8 to the regulatory genome.*

This research investigates architectural economy as a cross-domain principle: reusable primitives enable complexity under resource constraints, but create shared dependencies. Modularity and targeted redundancy can mitigate them, while introducing coordination costs and new potential failures.

## Research status

Version 3 is a preprint candidate, not peer reviewed. The computational benchmarks have been reproduced in a separate execution environment. The proposed comparative-genomic hypothesis has not yet been tested on empirical genomic data.

Reported and audited findings include:
- 70.8% lower PDP-8 code footprint using shared multiplication subroutines at 64 tasks, with a 4.1% increase in modeled memory cycles.
- 16,384 correct multiplication checks and 540 exhaustive synthetic network equivalence comparisons across all 4,096 input states.
- Fault exposure depends on the architecture and the fault model; the coordination of redundant components can itself create vulnerabilities.

## Repository status

The repository has been initialized for the complete research archive. The companion publication package contains the revised manuscript (PDF and Word), figures, simulation source, result JSON, independent audit, synthetic genomic validation, prior versions and reproduction instructions. These files will be present after the package is pushed; this README alone does not constitute the full release.

## Citation and publication

Young, Randall S. (2026). *Architectural Economy in Biological and Technological Systems: A hypothesis for the evolutionary conservation of genomic regulatory information: from the PDP-8 to the regulatory genome.* Version 3, preprint candidate.

DOI pending. Journal target: BioSystems, subject to author review and submission requirements.

AI assistance: ChatGPT and Google Gemini/Antigravity were used in drafting, computational implementation, editing and checking. The author is responsible for reviewing and approving the work before formal publication.
