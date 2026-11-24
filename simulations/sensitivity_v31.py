"""Exact K=32 sensitivity sweep for the v3 synthetic benchmark.
Run from repository root: python simulations/sensitivity_v31.py
Tests all 4096 states. The original architecture builders are unchanged.
"""
from pathlib import Path
import json
from collections import Counter
import numpy as np
from synthetic_networks import MotifSpec, build_network

ARCH = ["dedicated", "shared", "modular_shared", "modular_buffered"]
POOLS = [8, 16, 32, 64]
EXPONENTS = [0.0, 0.8, 1.2, 2.0]
K, M, SEEDS = 32, 12, 30

def portfolio(rng, pool_size, exponent):
    pool, seen = [], set()
    while len(pool) < pool_size:
        abc = tuple(map(int, rng.choice(M, size=3, replace=False)))
        kind = "and_not" if rng.random() < .6 else "and_or"
        m = MotifSpec(abc, kind)
        if m not in seen:
            pool.append(m)
            seen.add(m)
    w = np.arange(1, pool_size+1, dtype=float)**(-exponent)
    w /= w.sum()
    specs, ops = [], []
    for _ in range(K):
        specs.append([pool[int(i)] for i in rng.choice(pool_size, 2, replace=False, p=w)])
        ops.append("or" if rng.random() < .7 else "and")
    return specs, ops

def metrics(net, X, Yref):
    Y, active = net.eval_all(X)
    assert np.array_equal(Y,Yref)
    # Exact knockout blast computed locally: a redundant group cannot change
    # under a single motif loss; an unbuffered group may alter its output.
    vals = [m.eval_vec(X) for m in net.motif_nodes]
    blast = np.zeros(len(vals), dtype=int)
    fanout = np.zeros(len(vals), dtype=int)
    # Extra explicit OR-gate cost: one gate per distinct redundant pair.
    pairs = set()
    for k, groups in enumerate(net.output_groups):
        for j, grp in enumerate(groups):
            for mid in grp:
                fanout[mid] += 1
            if len(grp) > 1:
                pairs.add(tuple(sorted(grp)))
                continue
            other = groups[1-j]
            oth = np.bitwise_or.reduce([vals[i] for i in other],axis=0)
            if net.output_ops[k]=="or":
                changed = np.any(vals[grp[0]] & (1-oth))
            else:
                changed = np.any(vals[grp[0]] & oth)
            blast[grp[0]] += int(changed)
    output_blast = np.any(Y,axis=0).astype(int)
    # Distinct-pair shared OR gates are extra modeled fault sites.
    # Their loss removes the entire group (unlike a single motif loss).
    pair_blast = Counter()
    for k,groups in enumerate(net.output_groups):
        for j,grp in enumerate(groups):
            if len(grp)==1: continue
            oth = np.bitwise_or.reduce([vals[i] for i in groups[1-j]],axis=0)
            v = vals[grp[0]]
            changed = np.any(v & (1-oth)) if net.output_ops[k]=="or" else np.any(v & oth)
            pair_blast[tuple(sorted(grp))] += int(changed)
    all_sites = np.concatenate([blast,output_blast])
    explicit_sites = np.concatenate([all_sites,np.array([pair_blast[q] for q in sorted(pairs)], dtype=int)])
    return dict(nodes=net.n_internal_nodes, edges=net.n_edges, active_nodes=active,
        mean_motif_blast=float(blast.mean()), max_motif_blast=int(blast.max()),
        mean_all_blast=float(all_sites.mean()), max_all_blast=int(all_sites.max()),
        mean_motif_fanout=float(fanout.mean()), explicit_or_nodes=net.n_internal_nodes+len(pairs),
        explicit_or_mean_blast=float(explicit_sites.mean()),
        explicit_or_max_blast=int(explicit_sites.max()))

def run():
    X = ((np.arange(2**M)[:,None] >> np.arange(M))&1).astype(np.int8)
    result = []
    for pool in POOLS:
        for exponent in EXPONENTS:
            rows = {a:[] for a in ARCH}
            for seed in range(SEEDS):
                specs,ops = portfolio(np.random.default_rng(10000*K+seed),pool,exponent)
                ref = build_network("dedicated",M,specs,ops)
                Yref,_ = ref.eval_all(X)
                for a in ARCH:
                    net=ref if a=="dedicated" else build_network(a,M,specs,ops)
                    rows[a].append(metrics(net,X,Yref))
            for a in ARCH:
                summary={key:float(np.mean([r[key] for r in rows[a]])) for key in rows[a][0]}
                result.append(dict(pool_size=pool,zipf_exponent=exponent,architecture=a,n_seeds=SEEDS,**summary))
    return dict(status="synthetic sensitivity experiment, not genomic evidence",config=dict(K=K,M=M,seeds=SEEDS,states=2**M,pools=POOLS,exponents=EXPONENTS),summary=result)
if __name__=="__main__":
    result=run()
    out=Path(__file__).resolve().parents[1]/"results"/"sensitivity_v31.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(out)
