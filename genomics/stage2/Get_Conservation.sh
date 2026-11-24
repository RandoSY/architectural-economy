#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[[ $(uname -m) == x86_64 ]] || { echo 'This downloader expects x86-64 Linux/WSL.' >&2; exit 1; }
if [ ! -x ./bigWigAverageOverBed ]; then
  curl -fL --retry 3 'https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bigWigAverageOverBed' -o bigWigAverageOverBed.download
  mv bigWigAverageOverBed.download bigWigAverageOverBed
  chmod +x bigWigAverageOverBed
fi
# Match the ABC hg19 reference. Never use an hg38 BigWig with these BED coordinates.
source_url='https://hgdownload.soe.ucsc.edu/goldenPath/hg19/phyloP100way/hg19.100way.phyloP100way.bw'
./bigWigAverageOverBed "${1:-$source_url}" candidate_enhancers_hg19.bed conservation_hg19.tmp.tsv
awk 'BEGIN{FS="\t"} NF!=6{exit 1}' conservation_hg19.tmp.tsv
[ "$(wc -l < conservation_hg19.tmp.tsv)" -eq "$(wc -l < candidate_enhancers_hg19.bed)" ]
mv conservation_hg19.tmp.tsv conservation_hg19.tsv
printf 'Finished. Upload conservation_hg19.tsv to ChatGPT.\n'
