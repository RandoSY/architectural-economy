"""Verify mapping/coverage, rerun exploratory regressions and sensitivity checks."""
from pathlib import Path
import sys,subprocess,json
import numpy as np,pandas as pd,statsmodels.api as sm
P=Path(__file__).resolve().parent
cols=['chr','start','end','enhancer_id']; cc=['enhancer_id','size','covered','sum','mean0','phyloP']
old=pd.read_csv(P/'candidate_enhancers_hg19.bed',sep=r'\s+',names=cols)
new=pd.read_csv(P/'candidate_enhancers_hg38_clean.bed',sep=r'\s+',names=cols)
c=pd.read_csv(P/'conservation_hg38_clean.tsv',sep=r'\s+',names=cc)
d=pd.read_csv(P/'candidate_enhancers_hg19.csv.gz')
assert all(x.enhancer_id.is_unique for x in (old,new,c,d))
assert set(new.enhancer_id)==set(c.enhancer_id)<=set(old.enhancer_id)==set(d.enhancer_id)
j=old.merge(new,on='enhancer_id',suffixes=('_old','_new')).merge(c,on='enhancer_id')
assert ((j.end_old-j.start_old)==(j.end_new-j.start_new)).all()
assert ((j.end_new-j.start_new)==j['size']).all()
assert j.covered.between(0,j['size']).all()
assert np.allclose(j['mean0'],j['sum']/j['size'],atol=2e-5,rtol=1e-4)
covered=j.covered>0
assert np.allclose(j.loc[covered,'phyloP'],j.loc[covered,'sum']/j.loc[covered,'covered'],atol=2e-5,rtol=1e-4)
changed=(j.chr_old!=j.chr_new)|(j.start_old!=j.start_new)|(j.end_old!=j.end_new)
audit=dict(original=len(old),mapped=len(new),unique_score_ids=len(c),changed_coordinates=int(changed.sum()),chromosome_changed=int((j.chr_old!=j.chr_new).sum()),excluded_ids=sorted(set(old.enhancer_id)-set(new.enhancer_id)),unchanged_ids=j.loc[~changed,'enhancer_id'].tolist(),complete_coverage=int((j.covered==j['size']).sum()),zero_coverage=int((j.covered==0).sum()),partial_coverage=int(((j.covered>0)&(j.covered<j['size'])).sum()))
(P/'mapping_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
d=d[d.enhancer_id.isin(new.enhancer_id)]
d.to_csv(P/'cohort_mapped.csv.gz',index=False)
for suffix,ids in [('primary',set(new.enhancer_id)),('sensitivity',set(j.loc[changed,'enhancer_id']))]:
    if suffix=='primary': cp=P/'cohort_mapped.csv.gz'; cv=P/'conservation_hg38_clean.tsv'; out=P/'results.json'
    else:
        cp=P/'sensitivity_cohort.csv.gz';cv=P/'sensitivity_conservation.tsv';out=P/'sensitivity_results.json'
        d[d.enhancer_id.isin(ids)].to_csv(cp,index=False);c[c.enhancer_id.isin(ids)].to_csv(cv,sep='\t',header=False,index=False)
    subprocess.run([sys.executable,str(P/'analyze.py'),str(cp),str(cv),'--out',str(out)],check=True)
# Exploratory check: R subtracts focal numerator from the gene total; include focal numerator.
d=d.merge(c,on='enhancer_id');d=d[d.covered==d['size']].copy();d['B']=np.log1p(d.B_reach_reported);d['R']=d.R_buffering_thresholded
for k,v in {'length':'elem_length','distance_log':'distance','activity':'activity_base','cells':'perturbed_cells','targets':'direct_targets_thresholded','umi':'UMI_count','own_raw':'ABC.Score.Numerator'}.items():d[k]=np.log1p(d[v])
d['residual']=d.residual_expression_reported;f=['length','distance_log','activity','targets','cells','umi','residual','B','R','own_raw'];d=d.dropna(subset=f+['phyloP']);d[f]=(d[f]-d[f].mean())/d[f].std(ddof=0);d['BxR']=d.B*d.R;w=d[d.groupby('TargetGene').TargetGene.transform('size')>1].copy();cols=['length','distance_log','activity','targets','R','BxR','own_raw'];X=w[cols]-w.groupby('TargetGene')[cols].transform('mean');Y=w.phyloP-w.groupby('TargetGene').phyloP.transform('mean');m=sm.OLS(Y,X).fit(cov_type='cluster',cov_kwds={'groups':w.TargetGene},use_t=True)
out={'n':len(w),'genes':w.TargetGene.nunique(),'terms':{k:dict(beta=float(m.params[k]),p=float(m.pvalues[k]),ci95=m.conf_int().loc[k].tolist()) for k in ['R','BxR','own_raw']},'condition_number':float(np.linalg.cond(X))}
(P/'focal_activity_sensitivity.json').write_text(json.dumps(out,indent=2)+'\n')
