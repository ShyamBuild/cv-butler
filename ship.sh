#!/bin/zsh
cd ~/CV_Tool || exit 1
HOLD=0; [ "$1" = "--hold" ] && { HOLD=1; shift; }
MSG="$1"; PATCH="$2"
ROOT="$(cat ~/.cvtool_last_butler_root 2>/dev/null)"
[ -z "$ROOT" ] && ROOT="/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
if [ -n "$PATCH" ]; then
  echo "── patch: $PATCH"
  /usr/bin/python3 "$PATCH" || { echo "❌ patch crashed - rolling back to last proven commit"; git checkout -- butler.py briefing.py 2>/dev/null; exit 1; }
fi
echo "── selftest gate"
OUT="$(cv_env/bin/python3 butler.py --selftest "$ROOT" 2>&1)"
echo "$OUT" | tail -12
TWINS="$(cv_env/bin/python3 - "$ROOT" << 'PY'
import os, sys
def _n(s): return (s or '').lower().replace('\u2013','-').replace(' ','_')
bad = []
for dp, dn, fn in os.walk(sys.argv[1]):
    dn[:] = [d for d in dn if not d.startswith('.')]
    g = {}
    for d in dn: g.setdefault(_n(d), []).append(d)
    bad += [f"{os.path.basename(dp)}: {v}" for v in g.values() if len(v) > 1]
print('; '.join(bad))
PY
)"
if echo "$OUT" | grep -q "ALL GREEN" && [ -z "$TWINS" ]; then
  git add -A
  git -c user.email=butler@local -c user.name=butler commit -qm "$MSG (selftest ALL GREEN)" 2>/dev/null || echo "(nothing new to commit)"
  H="$(git rev-parse --short HEAD)"
  echo "✅ committed $H: $MSG"
  if [ "$HOLD" = "1" ]; then
    echo "🕐 --hold given: restart is yours"
  else
    pkill -f butler.py || true
    sleep 1
    nohup cv_env/bin/python3 butler.py "$ROOT" >> butler_live.log 2>&1 &
    disown
    sleep 2
    if pgrep -f butler.py > /dev/null; then
      echo "🤵 butler live on $H (background) · watch: tail -f butler_live.log · commands: cv_env/bin/python3 briefing.py chat · stop: pkill -f butler.py"
    else
      echo "⚠️ butler did not stay up - paste: tail -20 butler_live.log"
    fi
  fi
else
  echo "❌ NOT GREEN (twins: $TWINS) - auto-rollback to last proven commit"
  git checkout -- butler.py briefing.py 2>/dev/null
  echo "   proven state restored. Paste the FAIL lines; next patch starts clean."
  exit 1
fi
