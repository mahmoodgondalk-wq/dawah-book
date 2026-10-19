#!/bin/bash
# prints the number of edited batches that pass check_edit.py and, with -v, their names
cd /home/user/dawah-book
n=0; ok=""
for f in output_final/work/edit/out/*.txt; do b=$(basename $f .txt); if python3 output_final/work/scripts/check_edit.py $b 2>/dev/null | tail -1 | grep -q " OK$"; then n=$((n+1)); ok="$ok $b"; fi; done
[ "$1" = "-v" ] && echo "$ok"
echo $n
