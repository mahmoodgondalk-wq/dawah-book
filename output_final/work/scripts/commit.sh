#!/bin/bash
# Commit output_final and try to push (retries with backoff). Usage: commit.sh "message"
cd "$(dirname "$0")/../../.." || exit 1
STATUS=$(python3 output_final/work/scripts/batches.py status 2>/dev/null | tail -1)
python3 - "$STATUS" <<'PY'
import sys,re,datetime
p="output_final/PROGRESS.md"; s=open(p).read()
line="- Labeling status: "+sys.argv[1]+" (as of "+datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")+")"
s=re.sub(r"^- Labeling status:.*$", line, s, flags=re.M)
open(p,"w").write(s)
PY
git add -A output_final
git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01VEj6L3KXMj66AtFpD6YoGD" || echo "nothing to commit"
for d in 2 4 8 16; do
  if git push -q -u origin claude/upbeat-ptolemy-ph4o7a 2>/tmp/push_err.txt; then echo "pushed"; exit 0; fi
  if grep -q "403" /tmp/push_err.txt; then echo "push refused (403: no GitHub access) - committed locally"; exit 0; fi
  sleep $d
done
echo "push failed (network) - committed locally"
