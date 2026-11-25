from docx import Document
from docx.shared import Inches
from copy import deepcopy
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx.text.paragraph import Paragraph
root=Path('/mnt/data'); work=root/'v7_work'
fig,ax=plt.subplots(figsize=(10,4.3)); ax.set_xlim(0,10);ax.set_ylim(0,4.3);ax.axis('off');fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
navy='#20384b';blue='#416c90';green='#237e69';amber='#a46e2e'; gray='#526b7b'
def box(x,y,w,h,fc,ec,txt,sub=None):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.045,rounding_size=.09',facecolor=fc,edgecolor=ec,linewidth=1.1))
 ax.text(x+w/2,y+h*(.66 if sub else .5),txt,ha='center',va='center',color=navy,fontsize=11,weight='bold')
 if sub:ax.text(x+w/2,y+h*.26,sub,ha='center',va='center',color=gray,fontsize=9)
def arrow(x,y,y2):ax.annotate('',(x,y2),(x,y),arrowprops=dict(arrowstyle='-|>',lw=1.1,color=gray))
ax.text(.15,4.12,'A   Engineering precedent: PDP-8 compatible implementations',color=navy,fontsize=13,weight='bold',va='top')
for i,(name,desc) in enumerate([('PDP-8 · 1965','Discrete transistor logic'),('PDP-8/I · 1968','TTL integrated circuits'),('PDP-8/E · 1970','MSI logic / Omnibus'),('IM6100 · 1970s','CMOS processor on a chip')]):
 x=.15+i*2.45;box(x,3.05,2.32,.65,'#eef4f8',blue,name,desc);arrow(x+1.16,3.05,2.82)
box(.15,2.22,9.67,.54,'#e1f1ea',green,'Core instruction behavior preserved: compatible software can execute')
ax.text(.15,2.03,'B   Biological counterpart: developmental system drift',color=navy,fontsize=13,weight='bold',va='top')
for x,name,desc in [(.15,'Ancestral regulatory system','Original molecular implementation'),(5.3,'Derived regulatory system','Substitutions / compensatory rewiring')]:
 box(x,1.02,4.52,.62,'#f9f0e2',amber,name,desc);arrow(x+2.26,1.02,.79)
ax.annotate('',(5.27,1.33),(4.71,1.33),arrowprops=dict(arrowstyle='->',lw=1.2,color=amber));box(.15,.19,9.67,.54,'#e1f1ea',green,'Hypothesized continuity: matched regulatory responses within a defined tolerance')
fig.savefig(work/'Figure11_v7.png',dpi=300,facecolor='white');fig.savefig(work/'Figure11_v7.svg',facecolor='white');plt.close(fig)
d=Document(root/'Architectural_Economy_v6.docx');p=d.paragraphs
def change(i,t):
 p[i].runs[0].text=t
 for r in p[i].runs[1:]:r.text=''
change(2,p[2].text.replace('Version 6.0','Version 7.0'))
change(7,p[7].text.replace('We therefore distinguish sequence constraint from a prospective hypothesis of functional continuity (H3).','We distinguish sequence constraint from functional continuity (H3), grounded in developmental system drift and the historical precedent of compatible PDP-8 implementations.'))
change(8,p[8].text.replace('robustness.','robustness; developmental system drift.'))
change(19,'The PDP-8 family demonstrates how an architectural interface can outlast its implementation. The discrete-transistor PDP-8 (1965), TTL-based PDP-8/I (1968) and MSI-based PDP-8/E (introduced 1970) retained a compatible core instruction architecture [25,26,36,45]. Intersil subsequently implemented compatible instruction behavior in its CMOS IM6100 microprocessor [46]. Programs confined to the shared architecture could be reused; peripheral-specific software, timing and extensions could require adaptation. This is functional invariance within a defined interface, not identical behavior under all conditions (Table 1; Figure 11).')
change(147,'The PDP-8 case distinguishes an invariant functional interface from changing physical implementations. Its biological counterpart is developmental system drift (DSD): homologous traits can retain their phenotype while their developmental or genetic basis diverges [43,44]. Here, three measurements must remain distinct: (i) nucleotide conservation, (ii) regulatory activity and (iii) coordinated responses. Selection acts through fitness consequences, not a count of downstream transcripts. Our K562 analysis addresses sequence constraint, not cross-species continuity.')
change(148,'Experimental precedents include compensatory evolution of a Drosophila enhancer [34], mammalian enhancer turnover [35], nonhomologous regulatory elements supporting conserved neuronal Pomc expression [37], and expression stability associated with complex regulatory landscapes [38]. DSD is not a newly discovered phenomenon [43,44]. Our proposed contribution is to test whether measured architectural dependency and buffering explain variation in functional continuity beyond established predictors. Unlike deliberate engineering, evolution has no specified instruction set or external designer; functional equivalence is conditional on biological context.')
# keep original image in v6; replace with updated documented schematic in v7
for r in list(p[150].runs): p[150]._p.remove(r._r)
p[150].add_run().add_picture(str(work/'Figure11_v7.png'),width=Inches(6.1))
change(151,'Figure 11. Functional invariance under implementation change. (A) Selected milestones in PDP-8-compatible hardware; compatibility is restricted to shared instruction behavior and relevant interfaces [25,26,36,45,46]. (B) Conceptual developmental system drift: different regulatory implementations may produce equivalent responses [34,37,43,44]. Original schematic; the biological panel is not experimental data.')
change(171,'The PDP-8 makes the distinction concrete: from discrete transistors through integrated circuits to a CMOS processor, compatible implementations retained core instruction behavior, allowing compatible software to survive hardware change [25,26,36,45,46]. What endured was the operational contract, not the circuitry. Developmental system drift provides the biological counterpart [43,44]: conserved traits can arise through altered molecular mechanisms. The analogy is functional, not causal; engineering specifies compatibility deliberately, whereas evolution does not.')
change(172,'The resulting research question is whether architectural organization predicts the range of alternative implementations that can sustain a specified function. FEM provides a molecular starting point through equivalence tests and compensation studies. Comparative stimulus–response and perturbation tests then ask whether coordination itself survives change, beyond conserved baseline output. The proposed H3-M and H3 tests must distinguish equivalent outputs from equivalent causal dependencies and establish predictive value against conventional evolutionary explanations. They remain prospective, not confirmation of H2 or evidence of universal optimality.')
change(177,p[177].text.replace('complete v6 repository transfer','complete v7 repository transfer'))
for s in d.sections:
 for x in s.footer.paragraphs:
  for r in x.runs:
   if '(v6)' in r.text:r.text=r.text.replace('(v6)','(v7)')
# retain sequential reference numbering by cloning list style
for text in [
'True JR, Haag ES. Developmental system drift and flexibility in evolutionary trajectories. Evol Dev. 2001;3:109–119. https://doi.org/10.1046/j.1525-142X.2001.003002109.x',
'McColgan Á, DiFrisco J. Understanding developmental system drift. Development. 2024;151:dev203054. https://doi.org/10.1242/dev.203054',
'Digital Equipment Corporation. DIGITAL computing timeline: 1957–1997. Computer History Museum archive. https://archive.computerhistory.org/resources/text/DEC/dec.digital_%28DEC%29_timeline_1957-1997.102630354/timelinetext.htm',
'Intersil. Intercept hardware manual. Chapter 4: Software (IM6100 and PDP-8/E compatibility). https://bitsavers.trailing-edge.com/components/intersil/IM6100/InterceptHW.pdf']:
 el=deepcopy(d.paragraphs[-1]._p);d.paragraphs[-1]._p.addnext(el);q=Paragraph(el,d._body);q.runs[0].text=text
 for r in q.runs[1:]:r.text=''
d.core_properties.version='7.0';d.save(root/'Architectural_Economy_v7.docx')
