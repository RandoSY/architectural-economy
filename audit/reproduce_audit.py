"""Audit unmodified v2 simulation implementations; run from any directory."""
from pathlib import Path
import sys, json, itertools, platform
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'simulations'))
import pdp8_benchmark as p
import synthetic_networks as s
ARCH=['inlined','shared','dual_modular','buffered_tmr']
NET=['dedicated','shared','modular_shared','modular_buffered']
pairs=[((i*11+5)%61+2,(i*17+9)%59+3) for i in range(64)]
def run(arch, pairs):
    asm,pc=p.build_program(arch,pairs); cpu=p.PDP8(); cpu.load(asm.mem); st=cpu.run(pc)
    errors=sum(cpu.mem[p.DATA_OUT_BASE+i]!=a*b for i,(a,b) in enumerate(pairs))
    return asm,pc,st,errors
out={'scope':'Implementation-level audit; not physical PDP-8 or empirical genomics validation','python':platform.python_version(),'numpy':np.__version__,'pdp8':{},'networks':{}}
all_pairs=list(itertools.product(range(64),repeat=2))
for a in ARCH:
    err=0
    for i in range(0,4096,64):
        _,_,st,e=run(a,all_pairs[i:i+64]); assert st.halted; err+=e
    cap=0; first_failure=None
    for n in range(1,130):
        pp=[((i*7+3)%61+2,(i*13+5)%59+3) for i in range(n)]
        try:
            _,_,st,e=run(a,pp)
            if not st.halted or e: first_failure={'tasks':n,'errors':e,'halted':st.halted};break
            cap=n
        except (ValueError,MemoryError) as exc: first_failure={'tasks':n,'error':str(exc)};break
    asm,pc,st,e=run(a,pairs); assert e==0 and st.halted
    rows={}
    for label,addrs in [('routine',asm.routine_addrs),('other_tracked',sorted(set(asm.code_addrs)-set(asm.routine_addrs)))]:
        vals=[]; hangs=0
        for addr in addrs:
            cpu=p.PDP8();cpu.load(asm.mem);cpu.mem[addr]=p.NOP
            r=cpu.run(pc,max_instructions=max(20000,st.instructions*3))
            blast=sum(cpu.mem[p.DATA_OUT_BASE+i]!=x*y for i,(x,y) in enumerate(pairs))
            if not r.halted: hangs+=1;blast=max(1,blast)
            vals.append(blast)
        rows[label]={'fault_sites':len(vals),'timeouts':hangs,'mean_blast':float(np.mean(vals)),'max_blast':max(vals),'raw_blast':vals}
    out['pdp8'][a]={'operand_pairs':4096,'errors':err,'consecutive_capacity':cap,'first_failure':first_failure,'faults':rows}
    print(a,err,cap,rows['other_tracked']['mean_blast'],flush=True)
X=((np.arange(4096)[:,None]>>np.arange(12))&1).astype(np.int8)
comparisons=0; mismatches=0
for k in [4,8,12,16,24,32]:
    for seed in range(30):
        specs,ops=s.sample_task_portfolio(np.random.default_rng(10000*k+seed),12,k)
        ref,_=s.build_network('dedicated',12,specs,ops).eval_all(X)
        for a in NET[1:]:
            y,_=s.build_network(a,12,specs,ops).eval_all(X); comparisons+=1;mismatches+=int(np.count_nonzero(y!=ref))
out['networks']={'states_per_portfolio':4096,'comparisons':comparisons,'output_bit_mismatches':mismatches}
assert mismatches==0 and all(v['errors']==0 for v in out['pdp8'].values())
(ROOT/'results'/'independent_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['networks'])
