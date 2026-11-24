# Architectural Economy in Biological and Technological Systems

**A hypothesis for the evolutionary conservation of genomic regulatory information: from the PDP-8 to the regulatory genome**

*Author:* [confirm publication name] | Independent Researcher  
*Date:* 23 November 2026 | Revised working manuscript (v2) with computational benchmark results  

---

## Abstract

Biological systems and engineered technologies confront a shared class of architectural problems: generating diverse, reliable behavior under finite material, energetic, and informational resources. We define **architectural economy** as the context-dependent capacity to achieve a required portfolio of functions through composable primitives, reuse, modular organization, and distributed control while accommodating the costs of robustness and adaptation. The 1965 DEC PDP-8 illustrates how economical hardware supports complex software-defined behavior through subroutine reuse, while exposing a fundamental trade-off: shared control elements reduce static implementation cost but concentrate failure liability. In biological systems, conserved molecular machinery and distributed genomic regulatory networks present a mechanistically distinct yet analytically comparable trade-off.

To evaluate the general systems hypothesis quantitatively, we implement two reproducible computational benchmarks: (1) a 30-seed comparison of matched synthetic combinatorial networks implementing up to 32 identical multi-input functions, and (2) a cycle-accurate 12-bit DEC PDP-8 emulator executing up to 64 repeated shift-and-add multiplication tasks across inlined, shared, modular, and redundant architectures. In the synthetic networks ($K = 32$), unbuffered component sharing cuts distinct nodes by 50.9% and wiring by 57.3% but increases mean single-node perturbation blast radius 4.3-fold (worst-case 13.6-fold); combining bounded-fan-out modularity with shadow-node buffering strictly Pareto-dominates dedicated circuits—requiring 24.6% fewer nodes and 22.6% lower activation cost while cutting mean blast radius nearly 10-fold (0.10 vs. 0.96 outputs). On the PDP-8 emulator ($N = 64$), shared subroutines cut code memory by 70.8% (expanding 4K-core capacity 4.2-fold, from 92 to 388 tasks) at a +4.1% cycle cost, while increasing non-hanging routine-word blast radius 60-fold (0.93 to 55.82 tasks); dual modularity halves that blast radius for 24 extra words, and triple-redundant buffering masks 96.5% of non-hanging faults at 2.14× execution-cycle cost.

Building on this trade-off, we formalize a falsifiable **coordination-constraint hypothesis** for noncoding genomic elements: regulatory elements supporting broad, weakly buffered, higher-order downstream cascades should exhibit stronger evolutionary constraint than comparable elements with localized or well-buffered effects, even after accounting for conventional enhancer pleiotropy and target-gene identity via a within-target-gene fixed-effects design. Architectural economy is neither a claim of evolutionary optimality nor of universal genomic function; drift, historical contingency, and context-specific trade-offs remain essential alternatives. Computational benchmark results are reported here; empirical comparative-genomic validation remains proposed.

**Keywords:** architectural economy; PDP-8; noncoding DNA; gene regulatory networks; evolutionary constraint; modularity; robustness; enhancer buffering.

---

## 1. Introduction: complexity under constraint

A central challenge across both biological organization and engineered technology is how finite resources sustain diverse, reliable, and coordinated behavior. In a computer, constraints include logic gates, core memory, execution cycles, and energy. In an organism, constraints include molecular synthesis, cellular bioenergetics, developmental timing, and reproductive fitness. Sharing a class of architectural trade-offs does not imply a shared origin: engineered systems reflect intentional design under explicit specifications, whereas biological architectures arise through mutation, selection, genetic drift, and historical contingency [20–24]. Throughout this manuscript, the correspondence between computing and genomics is treated strictly as functional and analytical—not as a claim of implementation identity, optimality, or literal software execution in cells.

The central thesis of this article is that **architectural relationships**—specifically how components are reused, composed, and buffered—govern both the functional capacity and the perturbation vulnerability of complex systems. Reuse and composition expand functional diversity without requiring a proportional increase in distinct machinery. However, a shared control element becomes a structural dependency for multiple downstream outputs; disrupting it imposes a disproportionate system-level cost.

Only a small fraction of the human genome encodes protein sequence. The remainder comprises cis-regulatory elements, noncoding RNA genes, introns, repetitive DNA, and sequences with no established organism-level function. While the ENCODE project cataloged widespread biochemical activity across the genome [1], biochemical detection is not equivalent to evolutionary necessity or causal phenotype [2], and estimates of sequence constraint depend on evolutionary timescale and neutral background models [3,4]. Distinguishing between *specifying molecular components* and *coordinating their deployment* (timing, localization, and magnitude of expression) provides a structured entry point for asking why particular noncoding regions experience strong purifying selection—while acknowledging that protein-coding genes also encode regulatory machinery and that large fractions of noncoding DNA are non-regulatory.

---

## 2. The PDP-8 as a case study in architectural economy

Introduced in 1965, Digital Equipment Corporation's PDP-8 combined a 12-bit word, a base 4,096-word core memory, a single accumulator (`AC`), a 1-bit link register (`L`), and eight primary opcode classes (`AND`, `TAD`, `ISZ`, `DCA`, `JMS`, `JMP`, `IOT`, and `OPR`) [25,26]. Its `OPR` class combined compatible microoperations within a single instruction word, while complex arithmetic—including multiplication and division, which the base hardware lacked—was constructed from sequences of elementary instructions and reusable subroutines (Figure 1). That compactness enabled a general-purpose minicomputer at a fraction of contemporary hardware cost, though economy in one resource frequently shifts cost into another: fewer hardware opcodes increase software length, execution cycles, and programmer effort.

![](../figures/fig1_pdp8_arch.png)

**Figure 1.** PDP-8 architectural economy. Simplified stored-program architecture showing the base 4,096-word core memory configuration, single-accumulator processor, peripheral interface, and eight primary opcode classes [25,26].

The PDP-8 family also demonstrates how a stable architectural interface outlasts individual physical implementations: preserving instruction-set compatibility made existing software and subroutines reusable across hardware generations. In biology, conserved core cellular processes and the regulatory rewiring of their deployment achieve an analogous decoupling of reusable machinery from context-specific outputs [20], even though cells possess no centralized processor, instruction pointer, or clean hardware/software boundary (Table 1).

| Architectural principle | PDP-8 / computing | Biological candidate |
| :--- | :--- | :--- |
| **Primitive reuse** | Arithmetic & logic microoperations | Conserved core molecular machinery |
| **Composition** | Instruction sequences & subroutines | Combinatorial cis-regulatory inputs & pathways |
| **Modular control** | Program modules & stable interfaces | Regulatory subcircuits & cell-state modules |
| **Shared dependencies** | Shared subroutines & common interfaces | Pleiotropic regulators & developmental kernels |
| **Fault tolerance** | Modular duplication & redundant voting | Shadow/overlapping enhancers & feedback loops |

**Table 1.** Functional analogies across engineered and biological control architectures; physical substrates and evolutionary/design origins differ.

*(Note on recursive generative analogies: Mathematical constructions such as Hilbert space-filling curves—where $4^n - 1$ segments emerge from a compact recursive rule—illustrate that output complexity need not scale linearly with primitive count. Because developmental gene regulation relies primarily on parallel, context-dependent combinatorial signaling rather than sequential stack recursion, we emphasize compositional reuse and shared dependency trade-offs rather than procedural recursion.)*

---

## 3. Architectural economy as a general systems principle

Herbert Simon's analysis of hierarchical, nearly decomposable systems established that structural organization—not component count alone—governs the behavior and stability of complex systems [27]. In evolutionary biology, Kirschner and Gerhart showed how conserved, versatile core processes enable phenotypic diversity through regulatory recombination [20]; Kitano formalized biological robustness and its unavoidable trade-offs [21]; and Castle et al. linked evolvability directly to engineering design theory [22].

We define **architectural economy** operationally as achieving a specified portfolio of functions and minimum reliability within a domain-specific resource budget. Relevant costs cannot be equated numerically across domains: logic gates, memory words, execution cycles, and power in a processor differ fundamentally from molecular synthesis, expression burden, developmental time, and fitness costs in an organism. Furthermore, a system economical in one resource may be expensive in another: redundancy raises static component cost but lowers expected failure cost, and neutral or weakly deleterious sequences readily persist in multicellular genomes whenever population-genetic drift overwhelms weak purifying selection [23,24].

Accordingly, meaningful comparisons must evaluate **feasible architectures achieving matched functional portfolios and reliability** across a multiobjective frontier—trading off resource demand, functional coverage, perturbation resilience, and adaptability—rather than comparing raw genome or program sizes.

---

## 4. Molecular implementation of economical coordination

Yan et al. compared the transcriptional regulatory network of *Escherichia coli* with the Linux kernel function-call graph [5] and revealed a striking topological contrast: software call graphs rely heavily on **fan-in** (many high-level callers invoking reusable low-level subroutines), whereas bacterial transcriptional networks exhibit pronounced **fan-out** (relatively few regulators controlling many downstream targets) (Figure 2). Rather than invalidating the architectural comparison, this contrast sharpens it: both fan-in (shared subroutines) and fan-out (shared regulators) create **high-leverage single points of failure** whose disruption propagates across many outputs. In Section 6.1, we test both regimes directly—fan-out in synthetic combinatorial networks and fan-in in a PDP-8 subroutine benchmark.

![](../figures/fig2_hierarchies.png)

**Figure 2.** Contrasting control-network hierarchies. Stylized fan-out in bacterial transcriptional regulation and fan-in in software function calls, redrawn from Yan et al. [5]; node counts and edges are illustrative rather than empirical data.

Closer mechanistic grounding comes from experimentally reconstructed developmental gene regulatory networks (GRNs), notably in sea urchin embryos, where cis-regulatory modules integrate signaling and transcription-factor inputs into cell-fate commitments [6–8]. Four interacting molecular layers implement economical, distributed coordination:

### 4.1 Sequence-specific combinatorial logic
Transcription factors recognize degenerate DNA motifs in enhancers, promoters, and silencers, integrating activating and repressing signals in a context-dependent manner [7–9] (Figure 3). Unlike idealized Boolean logic gates, cis-regulatory responses are graded, concentration-dependent, stochastic, and sensitive to binding-site syntax and chromatin kinetics. Crucially, the same transcription factor acts across thousands of loci, and a single enhancer can operate across multiple tissues or developmental stages.

![](../figures/fig3_molecular_logic.png)

**Figure 3.** Combinatorial regulation as molecular logic. Idealized AND–NOT integration illustrating multi-input cis-regulatory computation [7–9]; actual molecular responses are graded and context-dependent.

### 4.2 Spatial organization and dynamic connectivity
Three-dimensional chromatin folding—shaped in part by CTCF and cohesin-mediated loop extrusion [10,11]—modulates contact probabilities between distal enhancers and target promoters (Figure 4). Because acute cohesin depletion eliminates loop domains without uniformly abolishing transcription [11], 3D topology acts as a quantitative, context-sensitive constraint rather than a rigid wiring harness. Combining enhancer biochemical activity with physical contact frequency yields strong predictive models of enhancer–promoter regulation [12].

![](../figures/fig4_chromatin_loop.png)

**Figure 4.** Spatial organization of regulatory interactions. Chromatin looping brings a distal enhancer and target promoter into three-dimensional proximity [10–12]; physical contact alone does not guarantee transcriptional activation.

### 4.3 RNA-mediated control and persistent regulatory state
Long noncoding RNAs and chromatin modifiers establish persistent, context-specific regulatory states. For example, *Xist* recruits SHARP/HDAC3 silencing complexes across the inactive X chromosome [13], while DNA methylation, histone modifications, and chromatin accessibility stabilize cell-state memory [14]. These layers act jointly with protein and RNA machinery rather than constituting an autonomous "epigenetic code."

### 4.4 Distributed control, feedback, and redundancy
Biological regulation operates through coupled local processes rather than a central supervisory kernel (Figure 5). Feedback and feedforward motifs shape response dynamics and noise filtering [15]—for example, *Hes7*-mediated negative feedback drives vertebrate segmentation-clock oscillations [16]—while overlapping ("shadow") enhancers buffer developmental phenotypes against single-element perturbations [17].

![](../figures/fig5_distributed_control.png)

**Figure 5.** Distributed regulatory control. Coupled interactions among regulatory DNA sequences, chromatin/RNA state, execution machinery, and cellular feedback [5–17].

Together, these mechanisms represent competing architectural strategies: shared regulators minimize distinct molecular machinery, modular enhancers allow context-specific deployment, and shadow enhancers add fault tolerance at the cost of extra regulatory DNA and coordination complexity.

---

## 5. Conservation of components versus conservation of coordination

Comparative genomics demonstrates substantial purifying selection outside protein-coding exons. Bejerano et al. identified 481 ultraconserved elements ($\ge 200$ bp identical across human, mouse, and rat), many of them noncoding [18]. The Zoonomia consortium's 240-mammal alignment estimated that roughly 10.7% of human bases are unusually constrained and cataloged 4,552 nearly perfectly conserved elements, with the majority of constrained individual bases lying outside coding exons (even though coding sequence remains more constrained per base overall) [4]. Deleting selected ultraconserved enhancers near *Arx* in mice yields viable animals with clear neurological and developmental abnormalities [19], confirming functional necessity for at least a subset of these loci.

Two established lines of work already connect regulatory architecture to conservation:
1. **Developmental regulatory kernels:** Davidson and Erwin proposed that deeply conserved subcircuits ("kernels") resist evolutionary rewiring because their internal wiring underpins body-plan specification [28].
2. **Enhancer pleiotropy:** Singh and Yi demonstrated that human enhancers active across multiple tissues and linked to more target genes exhibit stronger sequence conservation [29].

The open question addressed here is narrower and empirically testable: **after controlling for direct target count, tissue activity breadth, and target-gene identity, does higher-order downstream coordination—moderated by local enhancer buffering—explain additional variation in evolutionary sequence constraint?** (Figure 6).

![](../figures/fig6_coordination_conservation.png)

**Figure 6.** Conservation of coordination versus components. A functionally compatible module substitution (A) preserves system output, whereas disruption of a shared upstream regulator (B) places multiple downstream modules at risk [20,28,29].

We formalize two distinct, separately falsifiable hypotheses:

* **H1 (Architectural economy hypothesis):** In systems sustaining diverse functions under finite resources, reusing composable components reduces static implementation cost relative to functionally equivalent dedicated circuits, but amplifies shared failure dependencies. Modularity and targeted redundancy mitigate those liabilities at a quantifiable resource cost—and can yield Pareto-dominant operating points.
* **H2 (Coordination-constraint hypothesis):** Within a defined class of functional noncoding elements, regulatory elements supporting broader, weakly buffered **higher-order downstream coordination** exhibit stronger evolutionary constraint than comparable elements with localized or well-buffered effects, even after controlling for sequence composition, enhancer activity breadth, direct target count, and invariant properties of their direct target gene(s).

---

## 6. Formalization, computational benchmarks, and empirical research plan

We separate the general systems hypothesis (H1), which we test computationally below, from the specific comparative-genomic hypothesis (H2), for which we specify a confounder-controlled empirical protocol.

### 6.1 Controlled computational benchmarks (testing H1)

To evaluate H1 quantitatively under both **fan-out** (regulatory-like) and **fan-in** (subroutine-like) reuse regimes, we implemented two fully reproducible Python benchmarks (`simulations/synthetic_networks.py` and `simulations/pdp8_benchmark.py`). All compared architectures in each benchmark were verified to compute **bit-exact identical outputs** across all unperturbed test inputs.

#### Benchmark A: Synthetic multi-output combinatorial networks (fan-out regime)
We generated matched portfolios of $K \in \{4, 8, 12, 16, 24, 32\}$ predefined multi-input functions over $M = 12$ binary inputs (256 test states, 30 random seeds per $K$), where each output integrates two 3-input combinatorial motifs (`A ∧ B ∧ ¬C` or `A ∧ (B ∨ C)`, analogous to Figure 3) sampled from a Zipf-distributed pool of 16 regulatory primitives. Four matched architectures implemented the identical portfolio:
1. **Dedicated:** private motif copies per output (zero sharing).
2. **Shared reusable:** full deduplication of shared motifs across outputs.
3. **Modular shared ($d_{\max} = 4$):** reuse capped at four downstream outputs per motif node before spawning a new module copy.
4. **Modular + buffered:** modular shared architecture augmented with a redundant parallel ("shadow") backup for every motif node shared by $\ge 2$ outputs, combined via disjunctive buffering against single-node loss-of-function.

| Architecture ($K = 32$, 30 seeds) | Distinct nodes | Directed edges | Active nodes / eval | Mean blast (outputs) | Max blast (outputs) | Single-KO reliability | Zero-blast rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dedicated (no reuse)** | 96.0 ± 0.0 | 256.0 ± 0.0 | 23.77 ± 1.49 | 0.96 ± 0.02 | 1.00 ± 0.00 | 99.58% | 3.9% |
| **Shared reusable** | 47.1 ± 1.0 | 109.3 ± 3.1 | 12.61 ± 0.89 | 4.08 ± 0.27 | 13.63 ± 1.85 | 98.23% | 0.9% |
| **Modular shared ($d_{\max} = 4$)** | 54.4 ± 1.4 | 131.2 ± 4.1 | 14.33 ± 0.96 | 2.75 ± 0.17 | 4.00 ± 0.00 | 98.81% | 0.9% |
| **Modular + buffered** | **72.4 ± 2.0** | **244.9 ± 7.8** | **18.40 ± 1.24** | **0.10 ± 0.04** | **1.00 ± 0.00** | **99.96%** | **89.6%** |

**Table 2.** Matched synthetic network architecture comparison at $K = 32$ output functions (mean ± SD across 30 random seeds). All architectures compute identical unperturbed outputs.

**Key findings (Figure 7):**
* Pure reuse (**Shared**) cuts distinct internal nodes by **50.9%** (96.0 → 47.1), directed edges by **57.3%** (256.0 → 109.3), and mean activation cost by **46.9%** (23.77 → 12.61), but increases mean single-node blast radius **4.3-fold** (0.96 → 4.08 outputs) and worst-case blast radius **13.6-fold** (1.00 → 13.63 outputs).
* Adding bounded fan-out (**Modular shared**) requires only +7.3 extra nodes over raw sharing while cutting worst-case blast radius by **70.7%** (13.63 → 4.00).
* Combining modularity with targeted shadow buffering (**Modular + buffered**) **strictly Pareto-dominates Dedicated circuits on every measured metric simultaneously** at $K = 32$: **24.6% fewer nodes**, **4.3% fewer edges**, **22.6% lower activation cost**, **9.6× lower mean blast radius** (0.10 vs. 0.96), higher single-node knockout reliability (99.96% vs. 99.58%), and 89.6% complete fault masking.

![](../figures/fig7_synthetic_networks.png)

**Figure 7.** Controlled computational comparison across four matched synthetic network families (30 seeds, $K = 4$–$32$). Panel C shows the cost–vulnerability Pareto plane at $K = 32$; the shaded region denotes strict dominance over the dedicated baseline.

#### Benchmark B: Cycle-accurate 12-bit DEC PDP-8 emulator (fan-in regime)
To test the engineering trade-off directly on the historical architecture motivating Section 2, we built a cycle-accurate 12-bit DEC PDP-8 emulator supporting all eight primary opcode classes, 4,096-word core memory, Page-0/current-page addressing, indirect addressing, and auto-index registers (`0010–0017` octal). Because the base 1965 PDP-8 lacked hardware multiplication, we assembled an $N$-task 6-bit unsigned shift-and-add multiplication workload ($N \in \{1, 2, 4, 8, 16, 32, 64\}$) in four bit-exact-verified architectures: (1) **Inlined** (dedicated copy per task), (2) **Shared (`JMS`)** (single shared `MUL` subroutine), (3) **Dual-modular** (two independent `MUL` copies splitting tasks evenly), and (4) **Buffered TMR** (two primary `MUL` copies compared per call, falling back to a third copy on mismatch). We then injected single-word loss-of-function (`NOP`) faults into every executable routine word individually, separating **non-hanging functional faults** from **control-flow hangs** (infinite loops caused by disrupting `ISZ` loop counters).

| PDP-8 architecture ($N = 64$ tasks) | Code words (% 4K core) | Max tasks in 2,944 words | Memory cycles | Non-hang mean blast (tasks) | All-fault mean blast (tasks) | Non-hang fault masking |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Inlined (dedicated)** | 1,631 (39.8%) | 92 | 8,868 | 0.93 | 5.91 | 7.3% |
| **Shared subroutine (`JMS`)** | 477 (11.6%) | 388 | 9,228 (+4.1%) | 55.82 | 57.38 | 11.8% |
| **Dual-modular (2× `MUL`)** | 501 (12.2%) | 385 | 9,230 (+4.1%) | 28.94 | 34.69 | 11.4% |
| **Buffered TMR (3× `MUL`)** | 551 (13.5%) | 378 | 19,731 (+122.5%) | 2.25 | 8.13 | 96.5% |

**Table 3.** Cycle-accurate 12-bit DEC PDP-8 benchmark across $N = 64$ verified multiplication tasks and exhaustive single-word routine fault injection.

**Key findings (Figure 8):**
* **Memory economy vs. cycle overhead:** Shared `JMS` subroutines reduce static code footprint by **70.8%** (1,631 → 477 words) and expand task capacity in the 2,944-word code region **4.2-fold** (from 92 to 388 tasks), at a modest **+4.1%** execution-cycle overhead (8,868 → 9,228 cycles).
* **Shared-dependency amplification:** Single-word non-hanging routine faults corrupt an average of **0.93 tasks** when inlined, but surge **60-fold to 55.82 of 64 tasks** under a single shared subroutine.
* **Cost of mitigation:** Dual-modularity costs just **+24 words** (+5.0% over Shared) and zero meaningful cycle penalty while halving non-hanging blast radius (55.82 → 28.94). Triple-redundant buffering cuts static memory by 66.2% relative to inlining and masks **96.5% of non-hanging faults**, but pays a **2.14× execution-cycle cost** (19,731 cycles)—quantifying the multiobjective trade-off between static space, dynamic energy/time, and reliability.
* **A concrete limit of the computer analogy revealed by the emulator:** Even in the **Inlined** PDP-8 architecture, all-fault mean blast radius was 5.91 tasks (not 0.93) and buffered TMR still failed on 3.5% of non-hanging words (subroutine return jumps `JMP I`) plus loop-control hangs (`ISZ`). Why? Because a von Neumann processor executes tasks serially through a **single shared program counter (`PC`)**: a control-flow hang in Task 1 prevents Tasks 2–64 from ever running. By contrast, distributed biological gene regulation executes across parallel cellular pathways without a single global instruction pointer—underscoring why computational benchmarks illuminate shared-dependency trade-offs without implying implementation identity.

![](../figures/fig8_pdp8_benchmark.png)

**Figure 8.** Cycle-accurate 12-bit DEC PDP-8 benchmark executing $N = 1$–$64$ verified shift-and-add multiplications. Panel C maps the three-way trade-off among static code memory, dynamic execution cycles, and non-hanging fault blast radius at $N = 64$.

---

### 6.2 Comparative genomics empirical protocol (testing H2)

Testing H2 requires separating **higher-order downstream coordination** from two major confounders: (1) conventional enhancer pleiotropy (tissue breadth and direct target count) and (2) **direct target-gene identity** (an enhancer linked to a master developmental transcription factor automatically inherits its target gene's broad downstream network unless target-gene properties are rigorously controlled).

#### Operational variable definitions (strictly conservation-free predictors)
Represent each cellular or developmental context $c$ as a directed, weighted regulatory graph $G(c)$ linking candidate enhancers $e$ to direct target genes $g$ (via CRISPRi perturbations or Activity-by-Contact [ABC] scores [12]) and linking target genes $g$ to downstream transcriptional modules (via independent Perturb-seq / experimental TF-target regulons, *never* using sequence-conservation features to define edges or modules). For each noncoding candidate enhancer $e$ mapped to primary target gene $g(e)$:

* **$B(e)$ — Context-specific higher-order downstream reach:** Number of distinct downstream co-expression or Perturb-seq functional modules reachable in $\ge 2$ hops from $e$ through its direct target(s) within the specific contexts $c$ where $e$ is active, subject to prespecified edge-confidence and path-length thresholds.
* **$T(e)$ — Enhancer activity breadth (pleiotropy baseline):** Number of distinct biosamples or cell states in which $e$ exhibits active enhancer chromatin state (e.g., ENCODE cCRE / DNase + H3K27ac [14]). To avoid collinearity, activity breadth enters exclusively as $T(e)$ and is not duplicated inside covariate vector $Z$.
* **$R(e)$ — Local regulatory buffering index:** Total ABC-weighted activity of *other* co-active enhancers targeting the same promoter $g(e)$ in the same context(s) (proxy for shadow-enhancer redundancy [12,17]), cross-checked where available against CRISPRi effect-size attenuation.
* **$Z_{\text{elem}}(e)$ — Element-level baseline covariates:** Element length, local neutral substitution rate, GC content, mappability/alignment quality, peak chromatin accessibility/H3K27ac signal, linear distance to promoter, and direct target-gene count.
* **$Z_{\text{gene}}(g)$ — Target-gene covariates:** Target-gene coding constraint (e.g., gnomAD LOEUF/pLI), transcription-factor status, gene expression breadth across tissues, and gene-level network centrality.

#### Statistical models: global and within-target-gene specifications
We specify two complementary statistical models (proposed statistical frameworks, not biological laws):

1. **Global hierarchical model:**
   $$\text{Constraint}(e) = \alpha + \beta_1 B(e) + \beta_2 T(e) + \beta_3 R(e) + \beta_4 B(e)R(e) + \gamma_1 \cdot Z_{\text{elem}}(e) + \gamma_2 \cdot Z_{\text{gene}}(g(e)) + u_{g(e)} + \varepsilon(e)$$
   where $u_{g(e)}$ is a target-gene random intercept accounting for correlated enhancers sharing the same promoter.

2. **Within-target-gene fixed-effects (paired-enhancer) model:**
   $$\text{Constraint}(e) = \alpha_{g(e)} + \beta_1 B(e) + \beta_2 T(e) + \beta_3 R(e) + \beta_4 B(e)R(e) + \gamma_1 \cdot Z_{\text{elem}}(e) + \varepsilon(e)$$
   Restricting to target genes with $\ge 2$ mapped enhancers across contexts, the gene fixed effect $\alpha_{g(e)}$ absorbs **all** invariant properties of target gene $g$ (TF status, essentiality, global coding constraint). This design directly tests whether an enhancer activating gene $g$ in a **higher-cascade, weakly buffered context** is more evolutionarily constrained than another enhancer driving the *exact same gene* $g$ in a narrower or more redundantly buffered context.

#### Data sources, leakage prevention, and nested validation
* **Datasets:** Zoonomia 240-mammal phyloP constraint scores [4] as outcome; ENCODE cCREs and cell-state annotations [14]; enhancer–gene maps from CRISPRi perturbation compendia and ABC models [12].
* **Strict controls:** Restrict initial analysis to one genome assembly (GRCh38) and well-characterized perturbation-rich contexts (e.g., K562, plus matched developmental lineages as Perturb-seq/ABC maps permit). Exclude all exonic and splice-site overlaps; analyze promoters and distal enhancers separately. Never use conservation-derived features when constructing $G(c)$, $B(e)$, or $R(e)$.
* **Nested model ladder:** Compare held-out predictive error across chromosome-held-out splits and genomic-block bootstraps (to account for spatial autocorrelation):
  * **M0:** $Z_{\text{elem}}(e)$ (sequence & genomic context baseline)
  * **M1:** M0 + $T(e)$ + $Z_{\text{gene}}(g(e))$ (conventional pleiotropy + target-gene properties)
  * **M1b:** M0 + $T(e)$ + $\alpha_{g(e)}$ (within-target-gene fixed-effects baseline)
  * **M2:** M1 / M1b + $B(e) + R(e) + B(e)R(e)$ (higher-order reach and buffering)
* **Secondary functional outcome:** Where large-scale CRISPRi Perturb-seq data exist, evaluate the magnitude and breadth of downstream transcriptional disturbance directly as an outcome independent of evolutionary conservation.

---

### 6.3 Predictions and falsification criteria

* **P1 (Supported computationally in Section 6.1):** In matched computational architectures, reuse cuts static implementation costs but amplifies single-node perturbation blast radius; modularity and targeted buffering mitigate this liability at measurable cost and can dominate dedicated circuits on the cost–resilience Pareto frontier.
* **P2 (Genomic incremental effect):** Higher-order downstream reach $B(e)$ positively predicts mammalian sequence constraint ($\beta_1 > 0$) with an attenuating buffering interaction ($\beta_4 < 0$) after controlling for $Z_{\text{elem}}$, $T(e)$, and target-gene fixed effects $\alpha_{g(e)}$.
* **P3 (Perturbation signature):** Matched high-reach, low-buffering enhancers produce broader downstream transcriptional disturbances upon CRISPRi perturbation than low-reach or strongly buffered enhancers of comparable activity.
* **P4 (Out-of-sample predictive gain):** Model M2 reduces chromosome-held-out prediction error relative to M1 and M1b across sensitivity checks (edge-confidence thresholds, module definitions, and enhancer–gene mapping uncertainty).

Failure of P2–P4—including collapse of $\beta_1$ once target-gene fixed effects $\alpha_{g(e)}$ are introduced—would falsify the genomic coordination-constraint hypothesis (H2) independently of the computational findings in Section 6.1.

---

## 7. Limitations and alternative explanations

Several biological and methodological factors constrain interpretation:

1. **Non-coordination drivers of sequence conservation:** Evolutionary constraint reflects purifying selection, local mutation-rate variation, and historical contingency. High noncoding conservation can arise from overlapping RNA processing signals, dosage sensitivity, structural chromatin roles, or single indispensable developmental transitions—none of which require broad multi-module reach.
2. **Binding-site turnover and sequence decoupling:** Regulatory network topology can remain conserved even while underlying transcription-factor binding sites turn over via compensatory mutations [2,3,17]. Conserved coordination therefore does not strictly imply nucleotide-level conservation, biasing tests of H2 conservatively toward null findings.
3. **Ascertainment bias and static graph limits:** Well-studied developmental regulators appear artificially central in incomplete perturbation networks. Moreover, topological reachability in a static graph approximates—but does not replace—time-resolved dynamical sensitivity; quantitative Perturb-seq effect sizes are essential complements.
4. **Non-universal buffering effects:** Redundant ("shadow") enhancers do not universally relax sequence constraint; multiple enhancers often experience independent purifying selection because their buffering roles diverge across environmental stresses or developmental temperatures [17].
5. **Population-genetic drift limits:** In organisms with small effective population sizes such as mammals, the bioenergetic cost of synthesizing extra noncoding DNA is often far below the drift barrier ($1 / 2N_e$) [23,24]. Architectural economy in mammalian genomes therefore operates primarily through **functional selection on developmental fidelity and perturbation risk**, not through nucleotide-level metabolic minimization.
6. **Structural limits of the computing analogy:** As demonstrated directly in our PDP-8 fault-injection benchmark, stored-program computers couple tasks through a shared sequential program counter (`PC`) and separate code from execution hardware. Genomes lack a central kernel, encode the very machinery that reads them, and self-assemble from inherited cellular states.

---

## 8. Conclusion

Architectural economy frames a shared systems trade-off: reusing composable primitives reduces static implementation cost but creates high-leverage shared dependencies. Our controlled synthetic network simulations and cycle-accurate DEC PDP-8 benchmarks quantify this trade-off directly, showing both how reuse amplifies single-node perturbation blast radius and how bounded modularity plus targeted buffering can outperform dedicated designs.

Extending this lens to comparative genomics yields a clear, falsifiable question: whether context-specific higher-order downstream coordination—moderated by shadow-enhancer buffering and isolated from target-gene identity via within-gene controls—explains evolutionary sequence constraint beyond established pleiotropy predictors. If empirical testing confirms P2–P4, architectural economy will provide a quantitative explanatory bridge between systems architecture and regulatory genomics; if it fails, the computational trade-off remains sound while the genomic extension must be revised or discarded.

---

## Declarations and manuscript status

* **Article type:** Hypothesis and perspective with original computational benchmark simulations; empirical comparative-genomic analysis remains proposed.
* **Code and data availability:** All simulation code (`simulations/synthetic_networks.py`, `simulations/pdp8_benchmark.py`), JSON outputs (`results/`), and figure scripts (`simulations/plot_figures.py`) are self-contained and reproducible in Python 3 (`numpy`, `matplotlib`). Proposed empirical genomic sources are listed in the References.
* **Funding and competing interests:** [Author to confirm before submission.]
* **Author affiliation and contact information:** [Author to confirm before submission.]
* **Generative AI disclosure (author to confirm):** Generative AI tools (ChatGPT for initial literature discovery, organization, and drafting; Antigravity/Gemini for critical review, statistical model refinement, computational benchmark implementation, and manuscript editing) were used during preparation. The human author has independently reviewed all sources, code, and claims and accepts full responsibility for the final work. This manuscript has not undergone independent peer review.

---

## References

1. ENCODE Project Consortium. An integrated encyclopedia of DNA elements in the human genome. *Nature*. 2012;489:57–74. https://doi.org/10.1038/nature11247
2. Kellis M, et al. Defining functional DNA elements in the human genome. *Proc Natl Acad Sci USA*. 2014;111:6131–6138. https://doi.org/10.1073/pnas.1318948111
3. Rands CM, Meader S, Ponting CP, Lunter G. 8.2% of the human genome is constrained: variation in rates of turnover across functional element classes in the human lineage. *PLoS Genet*. 2014;10:e1004525. https://doi.org/10.1371/journal.pgen.1004525
4. Zoonomia Consortium. Evolutionary constraint and innovation across hundreds of placental mammals. *Science*. 2023;380:eabn3943. https://doi.org/10.1126/science.abn3943
5. Yan KK, Fang G, Bhardwaj N, Alexander RP, Gerstein M. Comparing genomes to computer operating systems in terms of the topology and evolution of their regulatory control networks. *Proc Natl Acad Sci USA*. 2010;107:9186–9191. https://doi.org/10.1073/pnas.0914771107
6. Davidson EH, et al. A genomic regulatory network for development. *Science*. 2002;295:1669–1678. https://pubmed.ncbi.nlm.nih.gov/11872831/
7. Levine M, Davidson EH. Gene regulatory networks for development. *Proc Natl Acad Sci USA*. 2005;102:4936–4942. https://doi.org/10.1073/pnas.0408031102
8. Istrail S, Ben-Tabou De-Leon S, Davidson EH. The regulatory genome and the computer. *Dev Biol*. 2007;310:187–195. https://doi.org/10.1016/j.ydbio.2007.08.009
9. Andersson R, Sandelin A. Determinants of enhancer and promoter activities of regulatory elements. *Nat Rev Genet*. 2020;21:71–87. https://doi.org/10.1038/s41576-019-0173-8
10. Schoenfelder S, Fraser P. Long-range enhancer–promoter contacts in gene expression control. *Nat Rev Genet*. 2019;20:437–455. https://doi.org/10.1038/s41576-019-0128-0
11. Rao SSP, et al. Cohesin loss eliminates all loop domains. *Cell*. 2017;171:305–320.e24. https://doi.org/10.1016/j.cell.2017.09.026
12. Fulco CP, et al. Activity-by-contact model of enhancer–promoter regulation from thousands of CRISPR perturbations. *Nat Genet*. 2019;51:1664–1669. https://doi.org/10.1038/s41588-019-0538-0
13. McHugh CA, et al. The Xist lncRNA interacts directly with SHARP to silence transcription through HDAC3. *Nature*. 2015;521:232–236. https://doi.org/10.1038/nature14443
14. ENCODE Project Consortium. Expanded encyclopaedias of DNA elements in the human and mouse genomes. *Nature*. 2020;583:699–710. https://doi.org/10.1038/s41586-020-2493-4
15. Alon U. Network motifs: theory and experimental approaches. *Nat Rev Genet*. 2007;8:450–461. https://doi.org/10.1038/nrg2102
16. Bessho Y, Hirata H, Masamizu Y, Kageyama R. Periodic repression by the bHLH factor Hes7 is an essential mechanism for the somite segmentation clock. *Genes Dev*. 2003;17:1451–1456. https://pubmed.ncbi.nlm.nih.gov/12783854/
17. Osterwalder M, et al. Enhancer redundancy provides phenotypic robustness in mammalian development. *Nature*. 2018;554:239–243. https://doi.org/10.1038/nature25461
18. Bejerano G, et al. Ultraconserved elements in the human genome. *Science*. 2004;304:1321–1325. https://pubmed.ncbi.nlm.nih.gov/15131266/
19. Dickel DE, et al. Ultraconserved enhancers are required for normal development. *Cell*. 2018;172:491–499.e15. https://pubmed.ncbi.nlm.nih.gov/29358049/
20. Kirschner M, Gerhart J. Evolvability. *Proc Natl Acad Sci USA*. 1998;95:8420–8427. https://doi.org/10.1073/pnas.95.15.8420
21. Kitano H. Biological robustness. *Nat Rev Genet*. 2004;5:826–837. https://doi.org/10.1038/nrg1471
22. Castle SD, Grierson CS, Gorochowski TE. Towards an engineering theory of evolution. *Nat Commun*. 2021;12:3326. https://doi.org/10.1038/s41467-021-23573-3
23. Lynch M, Conery JS. The origins of genome complexity. *Science*. 2003;302:1401–1404. https://pubmed.ncbi.nlm.nih.gov/14631042/
24. Lynch M, Marinov GK. The bioenergetic costs of a gene. *Proc Natl Acad Sci USA*. 2015;112:15690–15695. https://pubmed.ncbi.nlm.nih.gov/26575626/
25. Digital Equipment Corporation. *Small Computer Handbook*. March 1967. https://bitsavers.trailing-edge.com/pdf/dec/pdp8/handbooks/SmallComputerHandbook_Mar67.pdf
26. Johnstone A. The Young Person's Guide to... The PDP-8. *Computer Conservation Society, Resurrection*, issue 1. May 1990. https://www.computerconservationsociety.org/resurrection/res01.htm
27. Simon HA. The architecture of complexity. *Proc Am Philos Soc*. 1962;106:467–482. https://www.sfipress.org/21-simon-1962
28. Davidson EH, Erwin DH. Gene regulatory networks and the evolution of animal body plans. *Science*. 2006;311:796–800. https://doi.org/10.1126/science.1113832
29. Singh D, Yi SV. Enhancer pleiotropy, gene expression, and the architecture of human enhancer–gene interactions. *Mol Biol Evol*. 2021;38(9):3898–3909. https://pubmed.ncbi.nlm.nih.gov/33749795/
