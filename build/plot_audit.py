"""Publication figure derived only from archived independent audit results."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results/independent_audit.json').read_text())['pdp8']
keys=['inlined','shared','dual_modular','buffered_tmr']; labels=['Inlined','Shared','Dual\nmodular','Redundant\nfallback']
colors=['#5B6B7A','#B86B2B','#2E6F95','#1F7A68']
r=[data[k]['faults']['routine']['mean_blast'] for k in keys]
o=[data[k]['faults']['other_tracked']['mean_blast'] for k in keys]
allv=[(sum(data[k]['faults']['routine']['raw_blast'])+sum(data[k]['faults']['other_tracked']['raw_blast']))/(data[k]['faults']['routine']['fault_sites']+data[k]['faults']['other_tracked']['fault_sites']) for k in keys]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#9BA8B2','axes.labelcolor':'#253849','xtick.color':'#253849','ytick.color':'#253849','text.color':'#253849'})
fig,axs=plt.subplots(1,2,figsize=(10,4.35),gridspec_kw={'width_ratios':[1.15,1]})
x=np.arange(4);w=.34
ax=axs[0]; bars=ax.bar(x-w/2,r,w,color='#326C92',label='Routine words'); bars2=ax.bar(x+w/2,o,w,color='#C58C4F',label='Other tracked words'); ax.bar_label(bars,fmt='%.1f',padding=3,fontsize=9);ax.bar_label(bars2,fmt='%.1f',padding=3,fontsize=9); ax.set_ylim(0,65);ax.set_title('A. Fault scope changes the result',loc='left',fontweight='bold');ax.legend(loc='upper right',frameon=False,fontsize=9);ax.set_ylabel('Mean disrupted tasks (of 64)')
ax=axs[1];b=ax.bar(x,allv,.58,color=colors);ax.bar_label(b,fmt='%.1f',padding=4,fontsize=10);ax.set_ylim(0,20);ax.set_title('B. All tracked sites pooled',loc='left',fontweight='bold');ax.set_ylabel('Mean disrupted tasks (of 64)')
for ax in axs:
 ax.set_xticks(x,labels);ax.grid(axis='y',color='#DDE5EB',linewidth=.6);ax.set_axisbelow(True);ax.tick_params(axis='x',length=0)
fig.suptitle('Protection changes vulnerability; it does not eliminate it',x=.07,ha='left',fontsize=15,fontweight='bold');fig.subplots_adjust(left=.09,right=.98,bottom=.15,top=.80,wspace=.36)
fig.savefig(ROOT/'figures/fig9_fault_scope.png',dpi=350,bbox_inches='tight');fig.savefig(ROOT/'figures/fig9_fault_scope.svg',bbox_inches='tight');plt.close(fig)
