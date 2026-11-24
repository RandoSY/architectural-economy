import gzip,sys,collections,csv
from pathlib import Path
p=Path(sys.argv[1]); out=Path(sys.argv[2]); counts=collections.Counter()
with gzip.open(p,'rt') as f,gzip.open(out/'k562_abc_links.tsv.gz','wt') as g:
 g.write(next(f))
 for line in f:
  t=line.rsplit('\t',1)[-1].strip(); counts[t]+=1
  if 'k562' in t.lower(): g.write(line)
with open(out/'celltype_counts.csv','w') as f:
 w=csv.writer(f);w.writerow(['celltype','rows']);w.writerows(counts.most_common())
print(sum(counts.values()),[(k,v) for k,v in counts.items() if 'k562' in k.lower()])
