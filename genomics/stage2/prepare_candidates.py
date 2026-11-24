"""Create provisional pilot cohort from supplied ABC and annotated Perturb-seq files.
Selection is independent of conservation; no H2 outcome is computed here.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
p=argparse.ArgumentParser();p.add_argument('--abc',required=True);p.add_argument('--perturb',required=True);p.add_argument('--out',required=True);args=p.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
a=pd.read_csv(args.abc,sep='\t',low_memory=False);a=a[a.CellType.eq('K562-Roadmap')].copy();b=pd.read_csv(args.perturb)
# Exclude ambiguous identifiers rather than choosing a transcript with an extreme response.
b=b.dropna(subset=['gene','gene_id']);b=b[~b.gene.duplicated(False)&~b.gene_id.duplicated(False)].copy()
b=b.rename(columns={'gene':'TargetGene','anderson-darling de genes':'B_reach_reported','num_cells':'perturbed_cells','fold_expr':'residual_expression_reported'})
key=['chr','start','end']; a['enhancer_id']=a.chr+':'+a.start.astype(str)+'-'+a.end.astype(str)
# Use all thresholded distal candidate links for proxy, before joining perturbation data.
a=a[a['class'].isin(['genic','intergenic']) & ~a.isSelfPromoter & (a.distance>=2000)].copy()
a=a[a.chr.isin(['chr'+str(i) for i in range(1,23)]) & (a.end>a.start)]
a['direct_targets_thresholded']=a.groupby(key).TargetGene.transform('nunique')
a['other_distal_raw_activity_contact_thresholded']=(a.groupby('TargetGene')['ABC.Score.Numerator'].transform('sum')-a['ABC.Score.Numerator']).clip(lower=0)
a['R_buffering_thresholded']=np.log1p(a.other_distal_raw_activity_contact_thresholded)
# For first pilot choose one primary target per interval, independent of reach and conservation.
# Discard exact score ties. Restrict to ABC-labelled intergenic intervals, not confirmed exon-free.
a=a.sort_values(key+['ABC.Score','TargetGene'],ascending=[True,True,True,False,True]);ties=a[a['ABC.Score'].eq(a.groupby(key)['ABC.Score'].transform('max'))].groupby(key).size(); tie_ids=set(ties[ties>1].index)
primary=a.drop_duplicates(key).copy();primary=primary[~primary.set_index(key).index.isin(tie_ids)];primary=primary[primary['class'].eq('intergenic')]
joined=primary.merge(b[['TargetGene','gene_id','B_reach_reported','perturbed_cells','residual_expression_reported','UMI_count']],on='TargetGene',how='inner',validate='many_to_one').sort_values(key)
joined['elem_length']=joined.end-joined.start
joined.to_csv(out/'candidate_enhancers_hg19.csv.gz',index=False)
joined[key+['enhancer_id']].to_csv(out/'candidate_enhancers_hg19.bed',sep='\t',header=False,index=False)
summary={'abc_k562_rows':61981,'distal_autosomal_links':len(a),'primary_intergenic_candidates':len(primary),'joined_intervals':len(joined),'joined_genes':joined.TargetGene.nunique(),'chromosomes':joined.chr.nunique(),'reach_range':[int(joined.B_reach_reported.min()),int(joined.B_reach_reported.max())],'median_gene_reach':float(joined.drop_duplicates('TargetGene').B_reach_reported.median()),'missing_residual_expression':int(joined.residual_expression_reported.isna().sum()),'missing_abc_target_expression':int(joined.TargetGeneExpression.isna().sum()),'exact_top_score_tied_intervals':len(tie_ids),'assembly':'hg19 (GRCh37)','status':'provisional, selected annotated profiles; no conservation outcome; no H2 test'}
(out/'cohort_summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
