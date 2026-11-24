"""H2 exploratory single-context pilot. No real results bundled. Python 3.10+."""
import argparse, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

Y='constraint_phyloP'
E=['elem_length','gc_content','neutral_rate','align_qual','chromatin_act','log_dist_tss','direct_targets']
G=['gene_loeuf','gene_is_tf','gene_expr_breadth','gene_centrality','gene_expression','knockdown_efficiency','perturbed_cells']
BASE=E+['T_breadth']+G
ARCH=['B_reach','R_buffering','B_x_R']
RAW=BASE+ARCH[:2]
IDS=['enhancer_id','target_gene','chrom','start','end']

def validate(d):
    missing=set(IDS+RAW+[Y])-set(d)
    if missing: raise ValueError(f'Missing columns: {sorted(missing)}')
    d=d[IDS+RAW+[Y]].copy()
    for c in RAW+[Y,'start','end']: d[c]=pd.to_numeric(d[c],errors='raise')
    n=len(d); d=d.dropna(); d=d.loc[np.isfinite(d[RAW+[Y,'start','end']]).all(axis=1)].copy()
    if d.enhancer_id.duplicated().any(): raise ValueError('Primary analysis requires unique enhancer IDs; resolve ambiguous links without using conservation')
    if (d.start<0).any() or (d.end<=d.start).any(): raise ValueError('Invalid BED intervals')
    if d.groupby('target_gene').chrom.nunique().max()>1: raise ValueError('Resolve chromosome/target mapping before analysis')
    if d.groupby('target_gene').B_reach.nunique().max()>1: raise ValueError('Single-context B must be invariant within gene')
    if d.chrom.nunique()<3 or d.target_gene.nunique()<30: raise ValueError('Need >=3 chromosomes and >=30 genes for this exploratory runner')
    if (d[['B_reach','R_buffering','perturbed_cells']]<0).any().any(): raise ValueError('Negative reach, buffering or cell count')
    return d.reset_index(drop=True),n-len(d)

def prep(tr,te):
    tr=tr.copy(); te=te.copy()
    for c in RAW:
        mu=tr[c].mean(); sd=tr[c].std(ddof=0)
        if sd<1e-12: sd=1.
        tr[c]=(tr[c]-mu)/sd; te[c]=(te[c]-mu)/sd
    for x in [tr,te]: x['B_x_R']=x.B_reach*x.R_buffering
    return tr,te

def design(d, cols, within=False):
    if within:
        d=d.loc[d.groupby('target_gene').enhancer_id.transform('size')>=2]
        x=d[cols]-d.groupby('target_gene')[cols].transform('mean')
        y=d[Y]-d.groupby('target_gene')[Y].transform('mean')
    else:
        x=d[cols].copy(); x.insert(0,'intercept',1.); y=d[Y]
    return x,y

def rankcols(x):
    keep=[]; rank=0
    for c in x:
        a=x[keep+[c]].to_numpy(); r=np.linalg.matrix_rank(a)
        if r>rank: keep.append(c);rank=r
    return keep

MODELS={'M0':(E,False),'M1':(BASE,False),'M2':(BASE+ARCH,False),'FE1':(E+['T_breadth'],True),'FE2':(E+['T_breadth','R_buffering','B_x_R'],True)}
def cv(d):
    res={m:[[],[]] for m in MODELS}
    for ch in sorted(d.chrom.unique()):
        tr,te=prep(d[d.chrom!=ch],d[d.chrom==ch])
        for m,(cols,within) in MODELS.items():
            x,y=design(tr,cols,within); xx,yy=design(te,cols,within)
            if len(yy)==0: continue
            keep=rankcols(x); beta=np.linalg.lstsq(x[keep],y,rcond=None)[0]
            res[m][0].extend(yy);res[m][1].extend(xx[keep].to_numpy()@beta)
    out={}
    for m,(y,p) in res.items():
        y,p=np.array(y),np.array(p)
        if len(y):
            ss=np.sum((y-y.mean())**2)
            out[m]={'n':len(y),'mse':float(np.mean((y-p)**2)),'r2':float(1-np.sum((y-p)**2)/ss) if ss>0 else None}
    return out

def infer(d, model):
    cols,within=MODELS[model]; x,y=design(d,cols,within); keep=rankcols(x)
    # Cluster by 5 Mb target locus (all enhancers of a gene share its block).
    gene_pos=d.groupby('target_gene').start.median().astype(int)
    block=d.chrom+':'+(d.target_gene.map(gene_pos)//5_000_000).astype(str)
    groups=block.loc[x.index]; n=groups.nunique()
    if n<10: raise ValueError('Too few genomic blocks for exploratory clustered inference')
    fit=sm.OLS(y,x[keep]).fit(cov_type='cluster',cov_kwds={'groups':groups,'use_correction':True},use_t=True)
    ci=fit.conf_int(); terms={c:{'beta':float(fit.params[c]),'ci95':[float(ci.loc[c,0]),float(ci.loc[c,1])],'p':float(fit.pvalues[c])} for c in ARCH if c in keep}
    return {'n':len(y),'blocks':n,'terms':terms,'aliased_columns':[c for c in x if c not in keep]}

def synthetic():
    rng=np.random.default_rng(51); rows=[]
    for i in range(180):
        b=rng.normal(); expr=rng.normal(); gene={c:rng.normal() for c in G};gene.update(gene_expression=expr,perturbed_cells=100,knockdown_efficiency=.8,gene_is_tf=i%2)
        for j in range(5):
            r=rng.normal(); y=.35*b-.25*b*r+.2*r+rng.normal(scale=.65)
            row={c:rng.normal() for c in E}; row.update(gene); row.update(enhancer_id=f'e{i}_{j}',target_gene=f'g{i}',chrom=f'chr{i%6+1}',start=6_000_000*i+100*j,end=6_000_000*i+100*j+100,B_reach=b+6,R_buffering=r+6,T_breadth=rng.normal(),constraint_phyloP=y);rows.append(row)
    return pd.DataFrame(rows)

def main():
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True);g.add_argument('--input');g.add_argument('--self-test',action='store_true');p.add_argument('--out',required=True);p.add_argument('--manifest');a=p.parse_args()
    if a.input and not a.manifest: p.error('--manifest is required for real inputs')
    d=pd.read_csv(a.input) if a.input else synthetic(); d,removed=validate(d)
    z,_=prep(d,d)
    out={'status':'SYNTHETIC SOFTWARE CHECK ONLY' if a.self_test else 'USER-SUPPLIED DATA; PROVENANCE REQUIRES HUMAN VERIFICATION; EXPLORATORY','n_enhancers':len(d),'n_genes':d.target_gene.nunique(),'n_chromosomes':d.chrom.nunique(),'rows_dropped_missing':removed,'cross_validation':cv(d),'between_gene':infer(z,'M2'),'within_gene_contrasts':infer(z,'FE2'),'caution':'Single-context reach is gene-level, not enhancer-specific; FE2 does not estimate a reach main effect. Cluster intervals are exploratory, not the proposed block-bootstrap or permutation inference. No causal claim.'}
    if a.input: out.update(input_sha256=hashlib.sha256(Path(a.input).read_bytes()).hexdigest(),manifest=json.loads(Path(a.manifest).read_text()))
    Path(a.out).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps(out,indent=2,allow_nan=False))
if __name__=='__main__':main()
