"""Exploratory pilot. Requires stage2 cohort CSV and user conservation TSV.
No inference of verified coordinate provenance; no confirmatory H2 claim.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.api as sm
from scipy.stats import spearmanr
p=argparse.ArgumentParser();p.add_argument('cohort');p.add_argument('conservation');p.add_argument('--out',default='results.json');a=p.parse_args()
d=pd.read_csv(a.cohort); c=pd.read_csv(a.conservation,sep='\t',header=None,names=['enhancer_id','size','covered','sum','mean0','phyloP']); assert len(d)==len(c)==len(d.merge(c,on='enhancer_id',validate='one_to_one'))
d=d.merge(c,on='enhancer_id',validate='one_to_one'); counts={'matched':len(d),'fully_covered':int((d.covered==d['size']).sum()),'zero_covered':int((d.covered==0).sum()),'partially_covered':int(((d.covered>0)&(d.covered<d['size'])).sum())}; d=d[d.covered==d['size']].copy();d['B']=np.log1p(d.B_reach_reported);d['R']=d.R_buffering_thresholded
for k,v in {'length':'elem_length','distance_log':'distance','activity':'activity_base','cells':'perturbed_cells','targets':'direct_targets_thresholded','umi':'UMI_count'}.items():d[k]=np.log1p(d[v])
d['residual']=d.residual_expression_reported
base=['length','distance_log','activity','targets','cells','umi','residual']; features=base+['B','R']; x=d.dropna(subset=features+['phyloP']).copy()
# Scale over the complete-case analysis set for descriptive inference. For CV, fit scaling on training data only.
def scale(tr,te):
    tr,te=tr.copy(),te.copy()
    for k in features:
        m=tr[k].mean();s=tr[k].std(ddof=0) or 1
        tr[k]=(tr[k]-m)/s;te[k]=(te[k]-m)/s
    for z in (tr,te):z['BxR']=z.B*z.R
    return tr,te
z,_=scale(x,x)
models={'unadjusted_reach':['B'],'baseline':base,'adjusted_reach':base+['B'],'adjusted_full':base+['B','R','BxR']}
def fit(z,cols):
    # Cluster at target gene; correlations across adjacent genes remain a limitation.
    f=sm.OLS(z.phyloP,sm.add_constant(z[cols],has_constant='add')).fit(cov_type='cluster',cov_kwds={'groups':z.TargetGene},use_t=True)
    ci=f.conf_int();return {'r2':float(f.rsquared),'terms':{k:{'beta':float(f.params[k]),'ci95':ci.loc[k].tolist(),'p':float(f.pvalues[k])} for k in ['B','R','BxR'] if k in cols}}
res={m:fit(z,cs) for m,cs in models.items()}
cv={}
for m,cs in models.items():
    yy=[];pp=[]
    for ch in x.chr.unique():
        tr,te=scale(x[x.chr!=ch],x[x.chr==ch]); f=sm.OLS(tr.phyloP,sm.add_constant(tr[cs],has_constant='add')).fit(); yy.extend(te.phyloP);pp.extend(f.predict(sm.add_constant(te[cs],has_constant='add')))
    cv[m]=float(np.mean((np.array(yy)-np.array(pp))**2))
r,pv=spearmanr(d.B,d.phyloP)
# Within-gene contrasts: remove invariant B, retain R and BxR. Demean both predictors/outcome within gene.
w=z[z.groupby('TargetGene').TargetGene.transform('size')>1].copy(); cs=['length','distance_log','activity','targets','R','BxR']; X=w[cs]-w.groupby('TargetGene')[cs].transform('mean'); Y=w.phyloP-w.groupby('TargetGene').phyloP.transform('mean'); f=sm.OLS(Y,X).fit(cov_type='cluster',cov_kwds={'groups':w.TargetGene},use_t=True);ci=f.conf_int(); fe={'n':len(w),'genes':w.TargetGene.nunique(),'terms':{k:{'beta':float(f.params[k]),'ci95':ci.loc[k].tolist(),'p':float(f.pvalues[k])} for k in ['R','BxR']}}
out={'status':'Exploratory corrected hg38 pilot: supplied mapping internally checked; chain conversion not independently rerun','counts':counts,'fully_covered_genes':d.TargetGene.nunique(),'complete_cases':len(x),'complete_case_genes':x.TargetGene.nunique(),'chromosomes':x.chr.nunique(),'spearman_unadjusted_descriptive':{'rho':float(r),'naive_p_not_cluster_corrected':float(pv)},'regression_gene_clustered':res,'chromosome_holdout_mse':cv,'within_gene':fe,'limitations':['No cross-context activity breadth, LOEUF, independent expression, GC, local mutation rate, exon/promoter overlap verification or matched neutral controls','Thresholded ABC buffering proxy','Selected DE profiles and observational associations','Multiple tests exploratory; gene clustering does not capture genomic spatial correlation']}
Path(a.out).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
