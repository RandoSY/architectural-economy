from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from copy import deepcopy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path
P=Path('/mnt/data')
# Original conceptual diagram: identical interface across changing implementations.
fig,ax=plt.subplots(figsize=(9,4.3),dpi=320); ax.set_xlim(0,12); ax.set_ylim(0,6.2); ax.axis('off'); fig.patch.set_facecolor('white')
ink='#263C4B'; blue='#E8F0F6'; blue_edge='#4D7693'; green='#E8F3EC'; ge='#347E68'; amber='#F8F0E5'; ae='#AB7840'
def box(x,y,w,h,txt,fc,ec,fs=10):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04,rounding_size=0.10',facecolor=fc,edgecolor=ec,linewidth=1.25)); ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=fs,color=ink,linespacing=1.4)
for y,head,labels,stable,fc,ec in [(4.15,'A   ENGINEERED CONTINUITY', ['PDP-8 (1965)\nDiscrete transistors','PDP-8/I (1968)\nTTL integrated circuits','PDP-8/E (1970)\nTTL MSI logic'], 'Compatible core instruction semantics  →  reusable software',blue,blue_edge),(1.05,'B   EVOLUTIONARY CONTINUITY  •  PROPOSED ANALOGY',['Ancestral locus\nRegulatory element A','Intermediate locus\nA + compensating element B','Descendant locus\nRegulatory element B'],'Preserved input–output regulatory behavior  →  coordinated function',amber,ae)]:
 ax.text(.15,y+1.48,head,fontsize=11.2,fontweight='bold',color=ink)
 for i,l in enumerate(labels):
  x=.18+i*4; box(x,y+.55,3.62,.68,l,fc,ec,9.6)
  ax.add_patch(FancyArrowPatch((x+1.81,y+.55),(x+1.81,y+.14),arrowstyle='-|>',mutation_scale=12,color=ec,lw=1.2))
  if i<2: ax.add_patch(FancyArrowPatch((x+3.67,y+.89),(x+3.98,y+.89),arrowstyle='-|>',mutation_scale=10,color=ec,lw=1.05))
 box(.18,y-.53,11.62,.62,stable,green,ge,10.2)
ax.plot([.18,11.8],[3.0,3.0],color='#C9D4DB',lw=.8)
ax.text(.18,.04,'Conceptual comparison: compatibility is engineered in computers; regulatory continuity is an empirical question in biology.',fontsize=8.5,color='#52616D')
fig.subplots_adjust(left=.015,right=.985,top=.985,bottom=.025); fig.savefig(P/'functional_continuity_v5.png',bbox_inches='tight',pad_inches=.06);plt.close(fig)
d=Document(P/'Architectural_Economy_v4.docx'); p=list(d.paragraphs)
def replace(i,txt):
 p[i].text=txt

def before(i,txt,style='Body Text'):
 return p[i].insert_paragraph_before(txt,style)
replace(1,'Architectural economy, shared dependencies and functional continuity: from the PDP-8 to the regulatory genome')
replace(2,p[2].text.replace('Version 4.0 — working preprint','Version 5.0 — preprint candidate'))
replace(7,'An exploratory genomic pilot tested whether weakly buffered downstream regulatory influence predicts stronger noncoding sequence constraint (H2), combining K562 perturbation profiles, ABC enhancer–gene maps and 241-way mammalian phyloP scores (636 regions, 408 genes). The predicted association was not supported: adjusted reach β = −0.026 (95% CI −0.094 to 0.042); reach–buffering interaction β = 0.012 (−0.056 to 0.080). Held-out chromosome prediction deteriorated with the added predictors. The limitations of the pilot preclude a definitive test of H2. A distinct prospective hypothesis (H3) asks whether consequential regulatory functions remain stable across changes in their molecular implementation, as compatible software can survive changes in computer hardware. This is not a finding of the present genomic analysis. The framework therefore distinguishes architectural economy, sequence constraint and functional continuity as separate empirical questions.')
replace(8,'Keywords: architectural economy; PDP-8; noncoding DNA; gene regulatory networks; evolutionary constraint; regulatory turnover; functional continuity; robustness.')
replace(12,p[12].text+' A further question is whether functional architecture persists as its implementation changes. This distinction links the historical PDP-8 example to the interpretation of our genomic pilot.')
replace(19,'The PDP-8 family also demonstrates how a stable architectural interface can outlast individual implementations. The transistor-based PDP-8, the TTL integrated-circuit PDP-8/I and the MSI-based PDP-8/E retained a compatible core instruction architecture [25,26,36]. Programs depending on that interface could be reused, although peripheral-specific software, timing assumptions and extensions could require changes. In biology, conserved core cellular processes and regulatory rewiring [20] suggest a comparable distinction between a function and its implementation. The analogy concerns continuity of behavior, not a literal hardware/software partition in cells (Table 1).')
# fix the overly broad interpretation of the abstract all-node number
replace(6,p[6].text.replace('or 0.485 when output-integrator faults are included','or 0.485 under the broader internal-node fault model'))
replace(146,'7.1 Functional continuity: a refined hypothesis (H3)')
replace(147,'The PDP-8 case distinguishes an invariant functional interface from changing physical implementations. Biology requires an analogous distinction among three independently measured quantities: (i) nucleotide sequence conservation, (ii) conservation of regulatory activity and (iii) conservation of coordinated network behavior. These need not covary. Selection acts through fitness consequences rather than a count of downstream transcripts; both indispensable local regulation and buffered widespread regulation are possible. The present K562 analysis measures sequence constraint, not functional continuity across species.')
replace(148,'Existing research establishes that such decoupling is biologically possible. Ludwig et al. showed compensatory evolution of a Drosophila enhancer [34], while Villar et al. documented widespread turnover of mammalian liver enhancer activity [35]. Domené et al. demonstrated that nonhomologous mammalian and fish regulatory elements can support conserved neuronal Pomc expression [37]. Berthelot et al. associated complex regulatory landscapes with evolutionary stability of mammalian gene expression [38]. These findings establish precedent, not novelty for the general idea of regulatory turnover. Our proposed contribution is to ask whether measured architectural dependency and buffering improve prediction of functional continuity beyond established regulatory and evolutionary predictors.')
# insert figure and new prospective protocol before conclusion
before(149,'H3 (functional continuity hypothesis). Among homologous biological modules compared in matched contexts, greater fitness-relevant coordination demands predict greater conservation of perturbational input–output behavior, after accounting for regulatory activity breadth, expression, essentiality and phylogeny. Molecular sequences and individual network edges may change while this behavior persists. The hypothesis does not require every important module to remain unchanged, nor does it assert that all sequence turnover preserves function.')
q=before(149,'','Body Text');q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.add_run().add_picture(str(P/'functional_continuity_v5.png'),width=Inches(6.1));q.paragraph_format.keep_with_next=True
q=before(149,'Figure 11. Functional continuity despite implementation change. (A) A compatible PDP-8 instruction architecture permits reuse of compatible software across transistor and integrated-circuit implementations [25,26,36]. (B) A conceptual regulatory turnover trajectory in which a compensating element allows preservation of regulatory behavior [34,35,37,38]. Biological panel is an illustrative scenario, not observed data or evidence for H3.','Body Text');q.paragraph_format.space_after=Pt(8)
# copy caption run format from existing caption
for r in q.runs:
 r.font.size=Pt(9);r.italic=True
before(149,'Proposed test. Define orthologous regulatory modules and matched species, tissues and developmental stages before inspecting outcomes. For each module, independently quantify baseline expression, regulator and enhancer activity, and responses to standardized perturbations. Compare response vectors across species using a prespecified similarity measure on orthologous outputs; require agreement in direction, magnitude and timing where data permit. Measure sequence conservation and enhancer turnover separately. Distinguish stable baseline expression from stable responses to perturbation: only the latter directly probes continuity of coordination. Where feasible, compare single and combined enhancer perturbations to estimate buffering rather than relying solely on activity–contact proxies.')
before(149,'The analysis should compare a baseline model containing gene essentiality, expression, tissue breadth, direct target count, regulatory landscape complexity, sequence composition and phylogenetic relationships with an augmented model including independently measured reach and buffering. Use held-out species or clades and phylogenetically informed uncertainty, and avoid defining module membership from the very outcome being predicted. Prespecify minimum effect sizes, measurement reliability and falsification criteria. Failure to improve prediction of functional continuity in a sufficiently powered test would count against H3; stable output alone would not establish conserved internal wiring. No cross-species perturbational analysis has yet been performed here.')
replace(149,'8. Conclusion: conservation of architecture rather than implementation')
replace(150,'Architectural economy provides a shared framework for understanding how complex functionality can arise under finite resources. In the PDP-8 and synthetic network benchmarks, composable reuse reduces static implementation cost but concentrates shared dependencies. Modularization and targeted redundancy mitigate selected failures, yet the machinery that coordinates protection introduces dependencies of its own. Economy, resilience and adaptability must therefore be assessed together, under explicit resource and fault models. These are demonstrated properties of the computational models, not claims of universal evolutionary optimization.')
replace(151,'Our exploratory genomic analysis did not establish the predicted relationship between downstream regulatory reach and individual enhancer sequence conservation. The additional predictors did not improve held-out performance. This result neither establishes H2 nor demonstrates that enhancer turnover caused its failure. It does, however, clarify a critical distinction: architectural importance cannot be inferred from nucleotide conservation alone.')
before(152,'The history of the PDP-8 makes the distinction concrete. Across successive hardware generations, implementation technology changed while a compatible instruction architecture permitted continued execution of existing software. What endured was the functional contract, rather than the circuitry that realized it. Regulatory evolution offers experimentally documented cases in which molecular changes coexist with preserved biological output [34,37,38], although functional continuity must not be confused with invariant network topology.')
before(152,'The refined research question is consequently whether selection can preserve consequential coordination while permitting its molecular implementation to change, and whether measures of architecture offer explanatory power beyond existing models of regulatory evolution. This prospective hypothesis is independently testable and is not a reinterpretation of the negative pilot as confirmation. The enduring property of a complex system may reside not in the permanence of its components, but in the continuity of their coordination.')
# refs are numbered via paragraph numbering; clone formatting from last one
for txt in ['Jones DW. Frequently asked questions about the DEC PDP-8 family. University of Iowa. https://homepage.cs.uiowa.edu/~jones/pdp8/faqs/ (accessed 24 November 2026).','Domené S, Bumaschny VF, de Souza FSJ, Franchini LF, Nasif S, Low MJ, Rubinstein M. Enhancer turnover and conserved regulatory function in vertebrate evolution. Philos Trans R Soc Lond B Biol Sci. 2013;368:20130027. https://doi.org/10.1098/rstb.2013.0027','Berthelot C, Villar D, Horvath JE, Odom DT, Flicek P. Complexity and conservation of regulatory landscapes underlie evolutionary resilience of mammalian gene expression. Nat Ecol Evol. 2018;2:152–163. https://doi.org/10.1038/s41559-017-0377-2']:
 q=d.add_paragraph(txt,style='Compact'); q._p.remove(q._p.pPr); q._p.insert(0,deepcopy(p[195]._p.pPr))
# Preserve live page field
for s in d.sections:
 for q in s.footer.paragraphs:
  for r in q.runs:
   if '(v4)' in r.text: r.text=r.text.replace('(v4)','(v5)')
d.core_properties.title='Architectural Economy in Biological and Technological Systems'; d.core_properties.subject='Architectural economy, shared dependencies and functional continuity';d.core_properties.author='Randall S. Young'; d.core_properties.version='5.0'
d.save(P/'Architectural_Economy_v5.docx')
