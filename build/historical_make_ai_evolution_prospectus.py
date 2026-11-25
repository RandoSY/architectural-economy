from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from xml.sax.saxutils import escape
from reportlab.lib.colors import HexColor
P='/mnt/data/AI_as_a_Laboratory_for_Biological_Evolution_Research_Prospectus.pdf'
for name,f in [('Lato','Lato-Regular.ttf'),('LatoB','Lato-Bold.ttf'),('LatoI','Lato-Italic.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/lato/'+f))
pdfmetrics.registerFontFamily('Lato',normal='Lato',bold='LatoB',italic='LatoI',boldItalic='LatoB')
navy='#17344A'; teal='#197E79'; ink='#263746'; muted='#566C7D'; pale='#EDF5F5'; rule='#D5DFE4'; amber='#B07A37'
def st(n,s,l,c=ink,**kw):return ParagraphStyle(n,fontName='Lato',fontSize=s,leading=l,textColor=HexColor(c),**kw)
styles={'body':st('body',10.5,14.5,spaceAfter=8),'small':st('small',9.2,12.6,spaceAfter=5),'label':st('label',9,12,teal,fontName='LatoB') if False else st('label',9,12,teal,spaceAfter=7),'h':st('h',15,19,navy,spaceBefore=12,spaceAfter=6),'title':st('title',30,33,navy,spaceAfter=12),'sub':st('sub',13,17,muted,spaceAfter=12),'q':st('q',14,19,navy,spaceAfter=0),'table':st('table',9.3,12.2,spaceAfter=0),'thead':st('thead',9.5,12.2,'#FFFFFF'),'ref':st('ref',8.7,11.5,spaceAfter=5)}
S=[]
def p(t,k='body'):S.append(Paragraph(t,styles[k]))
def h(t):p('<b>'+t+'</b>','h')
def sp(n=6):S.append(Spacer(1,n))
def tab(rows,widths):
    a=[[Paragraph(str(cell),styles['thead' if i==0 else 'table']) for cell in row] for i,row in enumerate(rows)]
    t=Table(a,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(navy)),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,HexColor('#F2F6F7')]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,-1),(-1,-1),.5,HexColor(rule))]));S.append(t);sp(7)
def quote(text):
    t=Table([[Paragraph(text,styles['q'])]],colWidths=[504]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor(pale)),('LINEBEFORE',(0,0),(0,0),3,HexColor(teal)),('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),14),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12)]));S.append(t);sp(10)
class Road(Flowable):
    def __init__(self): Flowable.__init__(self);self.width=504;self.height=99
    def draw(self):
        c=self.canv
        data=[('01  HISTORY','PDP-8','Compatible instructions'),('02  EXPERIMENT','Artificial networks','Testable substitution'),('03  VALIDATION','Biological systems','Independent evidence')]
        for i,(a,b,d) in enumerate(data):
            x=i*174
            c.setFillColor(HexColor(navy if i!=1 else teal));c.roundRect(x,18,156,75,7,fill=1,stroke=0)
            c.setFillColor(colors.white);c.setFont('LatoB',8);c.drawString(x+11,77,a);c.setFont('LatoB',13);c.drawString(x+11,55,b);c.setFont('Lato',9);c.drawString(x+11,35,d)
            if i<2:
                c.setStrokeColor(HexColor(muted));c.setLineWidth(1.3);c.line(x+157,55,x+171,55);c.line(x+167,59,x+171,55);c.line(x+167,51,x+171,55)
        c.setFillColor(HexColor(muted));c.setFont('LatoI',8.6);c.drawString(0,3,'Conceptual research sequence; cross-domain transfer remains to be tested.')
def page(n,title):S.append(PageBreak());p(f'RESEARCH PROSPECTUS  /  {n:02d}', 'label');p('<b>'+title+'</b>','title')
p('RESEARCH PROSPECTUS  /  COMPANION INVESTIGATION  /  24 NOVEMBER 2026','label')
p('<b>Artificial Intelligence as an Experimental Model of Biological Evolution</b>','title')
p('Investigating architectural invariance, functional equivalence and compensatory adaptation','sub')
p('<b>Randall S. Young</b> · Independent researcher · ORCID 0009-0003-1657-0243<br/>Concept record 1.0 · Proposed second paper · Not peer reviewed','small')
sp(5);quote('<b>Reverse the direction of inquiry.</b><br/>Use the architecture and controlled evolution of artificial intelligence to discover principles that may illuminate the evolution of biological systems.')
h('Executive synopsis')
p('The foundational <i>Architectural Economy</i> paper (version 7) uses the PDP-8 family to illustrate a stable functional architecture across changing physical implementations. Its computational experiments identify resource–dependency trade-offs; its corrected exploratory genomic pilot did not support the predicted association between regulatory reach and sequence conservation. The next investigation moves from historical analogy to a manipulable experimental system: artificial neural networks.')
p('Artificial networks can be inspected, perturbed, compressed, retrained and reorganized at controlled cost. They offer a way to measure the extent to which different implementations realize equivalent functions, identify mechanisms that permit such continuity, and test whether those mechanisms predict independently measured biological behavior.')
S.append(Road());sp(6)
h('Publication decision')
p('Preserve version 7 as the foundation. Develop the AI investigation as an independent paper, with its own evidence, methods, limitations and reproducible archive. Cross-reference the two papers rather than treating the new hypothesis as a finding already established by the first.')
page(2,'The scientific proposition')
p('<b>H4 — Cross-domain architectural invariance.</b> Architectural properties that explain functional continuity under substitution in artificial networks may also predict functional continuity in biological regulatory systems. The objective is predictive transfer, not a claim that artificial and biological machinery are identical.')
tab([['AI experimental analogue','Biological comparison','Boundary of the analogy'],['Hardware/backend migration','Different molecular implementations','Execution hardware is not a genome.'],['Parameter or edge substitution','Changes in regulatory strengths or connections','Weights are not nucleotide sequences.'],['Pruning and redundancy','Loss and buffering of regulatory elements','Deletion is not necessarily neutral.'],['Distillation and module replacement','Alternative mechanisms preserving an output','Training is not biological reproduction.'],['Compensatory adjustment','Compensatory evolution / epistasis','Test interactions, not just final performance.']], [167,167,170])
h('Three distinct levels of change')
p('<b>Physical substrate.</b> Run the same model on different backends to measure numerical and task-level compatibility. This is the closest counterpart to the historical PDP-8 example. <b>Representational implementation.</b> Change precision, parameters or architecture and measure behavior. <b>Evolutionary process.</b> Introduce explicit variation, inheritance and selection in simulated populations; ordinary gradient training is not equivalent to Darwinian evolution.')
h('Falsifiable predictions')
p('<b>H4a — Tolerance:</b> at comparable cost and baseline performance, some network organizations preserve outputs under larger controlled changes. <b>H4b — Compensation:</b> constrained secondary changes restore function after primary perturbations more often than matched random controls. <b>H4c — Transfer:</b> architectural measurements improve held-out biological predictions over sequence, baseline activity and other conventional predictors.')
p('Null, reversed or context-dependent effects are meaningful results. Similar outcomes alone do not demonstrate shared mechanisms; each hypothesis must be evaluated separately.','small')
page(3,'The first experiment')
p('Begin with small, transparent networks that can be trained and tested on ordinary computing hardware. A controlled multi-output task with reusable latent subfunctions is preferable to a single benchmark score because it exposes the cost of shared dependencies.')
tab([['Stage','Proposed protocol'],['1 · Establish baseline','Train shared-trunk, dedicated-branch and modular/buffered variants. Match baseline performance and parameter or compute budgets; report both when exact matching is impossible. Repeat across independent seeds.'],['2 · Introduce change','Sweep normalized weight perturbations, edge removals and module substitutions at multiple severities. Separate inference-only tests from retraining and recovery experiments.'],['3 · Test compensation','Apply a fixed secondary-adjustment budget after each primary intervention; compare to random changes and equal-budget retraining controls. Retain unmodified and sham-perturbation baselines.'],['4 · Measure continuity','Evaluate held-out input/output behavior, per-task degradation, dependency blast radius, recovery cost and robustness under shifted input conditions.'],['5 · Test generality','Repeat on a different task and architecture. Report uncertainty across training seeds, not treating individual test inputs as independent trained models.']], [112,392])
h('A portable functional equivalence framework')
p('Define implementation distance D<sub>I</sub> using a domain-appropriate perturbation measure and functional distance D<sub>F</sub> using a prespecified response discrepancy. Classify equivalence only when uncertainty in D<sub>F</sub> lies within a justified tolerance. Plot D<sub>F</sub> against D<sub>I</sub>; distinguish equivalent, different and inconclusive cases. Different domains need not share the same distance scale.')
p('<b>Key outcomes:</b> tolerance curve; proportion of equivalent variants at a given perturbation severity; number of outputs disrupted by an intervention; recovery improvement per unit adjustment cost. Keep resource cost separate from function rather than imposing an arbitrary composite score.')
p('<b>Decision gate:</b> if architecture does not explain reproducible tolerance beyond controls, revise or reject H4a/b before attempting cross-domain prediction. No experiment described here has yet been executed.','small')
page(4,'From AI to biological evidence')
h('Research roadmap')
p('<b>1. Structured literature review.</b> Search neural-network pruning, distillation, model stitching, robustness, neuroevolution, developmental system drift and compensatory evolution. Record search strings, databases, inclusion criteria and extraction schema. Conduct quantitative meta-analysis only for sufficiently comparable outcomes; otherwise use a structured evidence synthesis.')
p('<b>2. Computational laboratory.</b> Execute the controlled pilot on page 3. Release scripts, seeds, environments, benchmark definitions, raw outputs, figures and negative results. Test whether the architecture effects persist under alternative fault and resource models.')
p('<b>3. Independent biological validation.</b> Start with public primate enhancer sequence–activity data [5]; pursue matched perturbation datasets to investigate regulatory dependencies. Test whether independently measured architecture features improve predictions beyond activity, sequence divergence, assay context and phylogeny. Do not infer organism-wide equivalence from a reporter assay.')
h('Preserve the intellectual estate for future AI')
p('The archive should function as a restartable research program rather than merely a published result. A future, more capable AI may automate literature synthesis, explore larger architectures, improve causal inference, propose experiments and challenge the original assumptions. Such capabilities and discoveries are possibilities, not guarantees.')
quote('<b>Future handoff:</b> preserve the question, operational definitions, source data, code, failures, decision gates and provenance. Require a future investigator to reproduce prior results and document disagreements before extending the theory.')
p('<b>Suggested repository:</b> a separate companion repository cross-linked to the foundational <a href="https://github.com/RandoSY/architectural-economy" color="#197E79">Architectural Economy archive</a>. Use a versioned README, research protocol, references, experiments, results, negative-results log and AI handoff notes. No new repository or experiments are claimed by this prospectus.','small')
h('Selected starting references')
for x in ["[1] Hinton G, Vinyals O, Dean J. Distilling the Knowledge in a Neural Network (2015). <a href='https://arxiv.org/abs/1503.02531' color='#197E79'>arXiv:1503.02531</a>.","[2] Frankle J, Carbin M. The Lottery Ticket Hypothesis (ICLR 2019). <a href='https://arxiv.org/abs/1803.03635' color='#197E79'>arXiv:1803.03635</a>.","[3] Bansal Y, Nakkiran P, Barak B. Revisiting Model Stitching to Compare Neural Representations (NeurIPS 2021). <a href='https://arxiv.org/abs/2106.07682' color='#197E79'>arXiv:2106.07682</a>.","[4] McColgan Á, DiFrisco J. Understanding developmental system drift. Development (2024). <a href='https://doi.org/10.1242/dev.203054' color='#197E79'>doi:10.1242/dev.203054</a>.","[5] Klein JC et al. Functional characterization of enhancer evolution in the primate lineage. Genome Biology (2018). <a href='https://doi.org/10.1186/s13059-018-1473-6' color='#197E79'>doi:10.1186/s13059-018-1473-6</a>."]:
 p(x,'ref')
def footer(c,d):
    c.setStrokeColor(HexColor(rule));c.line(54,43,558,43);c.setFont('Lato',8);c.setFillColor(HexColor(muted));c.drawString(54,29,'ARCHITECTURAL ECONOMY  /  COMPANION RESEARCH PROSPECTUS');c.drawRightString(558,29,f'{d.page:02d}')
    c.setFillColor(HexColor(teal));c.rect(54,758,504,3,fill=1,stroke=0)
doc=SimpleDocTemplate(P,pagesize=letter,leftMargin=54,rightMargin=54,topMargin=49,bottomMargin=56,title='Artificial Intelligence as an Experimental Model of Biological Evolution',author='Randall S. Young',subject='Proposed companion research to Architectural Economy v7')
doc.build(S,onFirstPage=footer,onLaterPages=footer)
print(P)
