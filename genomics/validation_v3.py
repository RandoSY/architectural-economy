"""Leakage-aware cross-validation for global prediction and held-out within-gene contrasts.
Synthetic fixtures are implementation checks, not genomic evidence. Uses v2 fixture generator.
"""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import section6_2_pilot as v2
BASE=v2.Z_ELEM_COLS+['T_breadth']; GENE=v2.Z_GENE_COLS; ARCH=['B_reach','R_buffering','B_x_R']; RAW=BASE+GENE+ARCH[:2]
Y='constraint_phyloP'
def prep(train,test):
    train=train.copy();test=test.copy()
    for c in RAW:
        if c=='gene_is_tf':continue
        mu=train[c].mean();sd=train[c].std(ddof=0)
        if sd<1e-12:sd=1.
        train[c]=(train[c]-mu)/sd;test[c]=(test[c]-mu)/sd
    for f in (train,test):f['B_x_R']=f['B_reach']*f['R_buffering']
    return train,test
def centered(f,cols):
    f=f.loc[f.groupby('target_gene')['enhancer_id'].transform('count')>=2].copy()
    x=f[cols]-f.groupby('target_gene')[cols].transform('mean')
    y=f[Y]-f.groupby('target_gene')[Y].transform('mean')
    return x.to_numpy(),y.to_numpy()
def score(y,p):
    y=np.concatenate(y);p=np.concatenate(p)
    return {'n':len(y),'mse':float(np.mean((y-p)**2)),'r2':float(1-np.sum((y-p)**2)/np.sum((y-y.mean())**2))}
def validate(df):
    if df.groupby('target_gene')['chrom'].nunique().max()>1:raise ValueError('Target gene spans chromosomes; resolve mapping before split')
    models={'global_baseline':(BASE+GENE,False),'global_architecture':(BASE+GENE+ARCH,False),'contrast_baseline':(BASE,True),'contrast_architecture':(BASE+ARCH,True)}
    res={k:([],[]) for k in models}
    for chrom in sorted(df.chrom.unique()):
        tr,te=prep(df[df.chrom!=chrom],df[df.chrom==chrom])
        for k,(cols,within) in models.items():
            if within:
                x,y=centered(tr,cols);xx,yy=centered(te,cols)
            else:x,y=tr[cols].to_numpy(),tr[Y].to_numpy();xx,yy=te[cols].to_numpy(),te[Y].to_numpy()
            if not len(yy):continue
            beta=v2.fit_ols(x,y,add_intercept=not within)
            pred=v2.predict_ols(xx,beta,add_intercept=not within)
            res[k][0].append(yy);res[k][1].append(pred)
    return {k:score(*v) for k,v in res.items()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input-csv');args=parser.parse_args()
    if args.input_csv: out={'status':'user supplied data; provenance not validated','scores':validate(pd.read_csv(args.input_csv))}
    else: out={'status':'synthetic implementation checks only','confounded_null':validate(v2.generate_synthetic_verification_data('confounded_null')),'true_effect':validate(v2.generate_synthetic_verification_data('true_coordination'))}
    path=Path(__file__).resolve().parents[1]/'results'/'validation_v3.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
