#!/bin/bash
# install_services.sh - SUMMARY-RESOLVE v85.142: repo-tracked installer for the Summary Maker workflow (law 25: the master runs me, never a note)
set -e
W="$HOME/Library/Services/Summary Maker.workflow/Contents/document.wflow"
grep -q "summary_template" "$W" && { echo "already installed - idempotent skip"; exit 0; }
cp "$W" "$W.bak-$(date +%Y%m%d-%H%M%S)"
cv_env/bin/python3 - <<'PEOF'
import io, os
w = os.path.expanduser('~/Library/Services/Summary Maker.workflow/Contents/document.wflow')
L = io.open(w, encoding='utf-8').read().split('\n')
k = next(i for i, l in enumerate(L) if l.strip().startswith('template=$(osascript'))
ind = L[k][:len(L[k]) - len(L[k].lstrip())]
L[k:k+1] = [
    ind + 'template=$(cd ~/CV_Tool && cv_env/bin/python3 -c "import summary_builder,sys; print(summary_builder._summary_template_for(sys.argv[1:]))" "$@" 2>/dev/null | tail -1)',
    ind + 'if [ -z "$template" ]; then',
    L[k],
    ind + 'fi',
]
io.open(w, 'w', encoding='utf-8').write('\n'.join(L))
print('installed: verb-first template with chooser fallback')
PEOF
grep -n "summary_template" "$W" | head -3
