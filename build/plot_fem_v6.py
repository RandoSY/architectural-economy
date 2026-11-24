"""Version 6 Figure 12: conceptual functional equivalence map (not data).
Portable rendering of the schematic in the original v6 document builder.
Run from the repository root: python build/plot_fem_v6.py
"""
from pathlib import Path
import matplotlib.pyplot as plt

out = Path(__file__).resolve().parents[1] / "figures" / "FEM_figure12.png"
out.parent.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#20384b','xtick.color':'#20384b','ytick.color':'#20384b','text.color':'#20384b'})
fig,axs=plt.subplots(1,2,figsize=(8.1,3.55),gridspec_kw={'width_ratios':[1,1.1]})
a,b=axs
for ax in axs: ax.set_facecolor('white')
a.axhspan(-.35,.35,color='#e3f1eb');a.axhline(.35,c='#237e69',ls='--',lw=1);a.axhline(-.35,c='#237e69',ls='--',lw=1);a.axhline(0,c='#7a919e',lw=.6)
a.set(xlim=(0,1),ylim=(-1,1),xlabel='Aligned sequence divergence',ylabel='Signed activity difference');a.set_xticks([0,1],['Low','High']);a.set_yticks([-.35,0,.35],['−δ','0','+δ']);a.text(.98,.03,'Candidate equivalence\ndespite divergence',ha='right',va='center',fontsize=9,color='#237e69',fontweight='bold');a.text(.5,.69,'Activity differs',ha='center',color='#506775');a.text(.5,-.71,'Activity differs',ha='center',color='#506775');a.set_title('A   Sequence–function space',loc='left',fontweight='bold',fontsize=11,pad=10)
b.axvspan(-.35,.35,color='#e3f1eb');b.axvline(-.35,c='#237e69',ls='--',lw=1);b.axvline(.35,c='#237e69',ls='--',lw=1);b.axvline(0,c='#7a919e',lw=.6)
for y,mu,lo,hi,c in [(3,.08,-.12,.28,'#237e69'),(2,.60,.43,.77,'#b5792b'),(1,.20,-.21,.61,'#667f93')]:
    b.errorbar(mu,y,xerr=[[mu-lo],[hi-mu]],fmt='o',color=c,capsize=4,lw=2,ms=5)
b.set(ylim=(.45,3.55),xlim=(-.82,.91),xlabel='Signed activity difference');b.set_yticks([1,2,3],['Inconclusive','Different¹','Equivalent']);b.set_xticks([-.35,0,.35],['−δ','0','+δ']);b.set_title('B   Equivalence decision',loc='left',fontweight='bold',fontsize=11,pad=10)
fig.text(.5,.025,'Illustrative intervals and bounds only; δ must be justified before analysis.  ¹Difference exceeds the equivalence margin.',ha='center',fontsize=8,color='#506775')
fig.subplots_adjust(left=.11,right=.98,bottom=.20,top=.86,wspace=.47)
fig.savefig(out,dpi=330,facecolor='white')
plt.close(fig)
print(out)
