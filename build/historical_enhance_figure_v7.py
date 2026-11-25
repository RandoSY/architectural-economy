from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon
from docx import Document
from docx.shared import Inches,Pt
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement
P=Path('/mnt/data/v7_work'); D=Path('/mnt/data/Architectural_Economy_v7.docx')
fig,ax=plt.subplots(figsize=(10,5.25));ax.set(xlim=(0,10),ylim=(0,5.25));ax.axis('off');fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
navy='#20384b';blue='#416c90';green='#237e69';amber='#a46e2e';gray='#526b7b';dark='#202a32';gold='#d99b45'
def rect(x,y,w,h,c,ec='none',lw=.8):ax.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor=ec,lw=lw))
def box(x,y,w,h,fc,ec,txt,sub=None):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.035,rounding_size=.08',facecolor=fc,edgecolor=ec,lw=1.1));ax.text(x+w/2,y+h*(.66 if sub else .5),txt,ha='center',va='center',color=navy,fontsize=11,weight='bold')
 if sub:ax.text(x+w/2,y+h*.24,sub,ha='center',va='center',color=gray,fontsize=9)
def panel(x,y,w,h):
 rect(x,y,w,h,'#e7d9bd',navy);rect(x+.04,y+.08,w-.08,h-.12,dark);rect(x+.06,y+h-.11,w-.12,.07,gold)
 for i in range(12):
  ax.add_patch(Circle((x+.11+i*(w-.22)/11,y+h*.48),.018,facecolor=gold if i%3==0 else '#eee4cd',edgecolor='none'))
  rect(x+.09+i*(w-.22)/11,y+.04,.045,.08,'#c77e37' if i%4<2 else '#f3e8d4')
def machine(cx,kind):
 if kind==0:
  x=cx-.48;rect(x,3.30,.96,1.00,'#3c5964',navy);rect(x+.055,3.63,.85,.61,'#192b36');rect(x+.47,3.63,.045,.61,'#b7bdbe');panel(x+.04,3.32,.88,.28)
 elif kind==1:
  x=cx-.70;rect(x,3.28,1.4,1.04,'#d6d0c1',navy)
  for k in range(3):
   xx=x+.04+k*.45;rect(xx,3.33,.41,.94,dark);rect(xx,4.18,.41,.09,gold)
   for j in range(2):rect(xx+.04,3.9-j*.16,.33,.12,'#586b72')
  panel(cx-.40,3.38,.80,.28)
 elif kind==2:
  x=cx-.75;rect(x,3.38,1.5,.83,'#d6d0c1',navy);rect(x+.05,3.45,1.4,.69,dark);rect(x+.07,4.04,1.36,.08,gold);panel(x+.12,3.52,1.25,.37)
 else:
  x=cx-.62;rect(x,3.56,1.24,.48,'#e6dfcf',navy);rect(x+.39,3.64,.46,.32,'#b5903e',navy)
  ax.text(cx,3.80,'6100',ha='center',va='center',fontsize=9,color=navy,weight='bold')
  for j in range(14):
   xx=x+.04+j*.087;rect(xx,3.47,.035,.09,'#ac934e');rect(xx,4.04,.035,.09,'#ac934e')
ax.text(.15,5.11,'A   Engineering precedent: PDP-8-compatible implementations',color=navy,fontsize=13,weight='bold',va='top')
for i,(n,desc) in enumerate([('PDP-8 · 1965','Discrete transistors'),('PDP-8/I · 1968','TTL integrated circuits'),('PDP-8/E · 1970','MSI logic / Omnibus'),('IM6100 · 1970s','CMOS microprocessor')]):
 cx=1.28+i*2.47;machine(cx,i);ax.text(cx,4.60,n,ha='center',fontsize=11,weight='bold',color=navy);ax.text(cx,3.13,desc,ha='center',fontsize=9,color=gray);ax.annotate('',(cx,2.85),(cx,3.03),arrowprops=dict(arrowstyle='-|>',lw=1.1,color=gray))
box(.15,2.24,9.67,.54,'#e1f1ea',green,'Preserved core instruction behavior: compatible software can execute')
ax.text(.15,2.01,'B   Biological counterpart: developmental system drift',color=navy,fontsize=13,weight='bold',va='top')
for x,n,desc in [(.15,'Ancestral regulatory system','Original molecular implementation'),(5.3,'Derived regulatory system','Substitution / compensatory rewiring')]:
 box(x,1.02,4.52,.62,'#f9f0e2',amber,n,desc);ax.annotate('',(x+2.26,.78),(x+2.26,1.02),arrowprops=dict(arrowstyle='-|>',lw=1.1,color=gray))
ax.annotate('',(5.27,1.33),(4.71,1.33),arrowprops=dict(arrowstyle='->',lw=1.2,color=amber));box(.15,.18,9.67,.54,'#e1f1ea',green,'Hypothesized continuity: equivalent regulatory responses within a defined tolerance')
fig.savefig(P/'Figure11_v7.png',dpi=300,facecolor='white');fig.savefig(P/'Figure11_v7.svg',facecolor='white');plt.close(fig)
d=Document(D);p=d.paragraphs
for r in list(p[150].runs):p[150]._p.remove(r._r)
p[150].add_run().add_picture(str(P/'Figure11_v7.png'),width=Inches(6.1))
p[151].runs[0].text='Figure 11. Functional invariance under implementation change. (A) Selected milestones in PDP-8-compatible hardware; original stylized drawings, not photographs and not to scale. Compatibility is restricted to shared instruction behavior and relevant interfaces [25,26,36,45,46]. (B) Conceptual developmental system drift: different regulatory implementations may produce equivalent responses [34,37,43,44]. The biological panel is not experimental data.'
for r in p[151].runs[1:]:r.text=''
# Photo source links in standalone companion, keeping manuscript caption concise.
D2=P/'Figure11_photo_sources.md';D2.write_text('''# Historical photographs for Figure 11\n\nThe manuscript uses original schematic drawings, not photographs. Authentic, openly licensed photographs for a future photo-based edition:\n\n- [Original PDP-8, Science Museum](https://commons.wikimedia.org/wiki/File:PDP-8_minicomputer,_Digital_Equipment_Corporation,_1965_-_Science_Museum,_London_-_DSC05572.jpg) — Daderot, CC0 1.0.\n- [PDP-8/I](https://commons.wikimedia.org/wiki/File:DEC_PDP-8-I_Minicomputer.jpg) — Ray Swi-hymn, edited by Pittigrilli, CC BY-SA 2.0.\n- [PDP-8/E](https://commons.wikimedia.org/wiki/File:PDP8E_Full_Front.jpg) — MBlairMartin, edited by Pittigrilli, CC BY-SA 4.0.\n- [Intersil IM6100 die](https://commons.wikimedia.org/wiki/File:Intersil_6100_die.JPG) — Pauli Rautakorpi, CC BY 3.0.\n\nIf reproducing these photos, credit the named creators, link the licenses and indicate changes; retain applicable share-alike terms. Photos show different system configurations and are not a scale comparison.\n''')
d.save(D)
