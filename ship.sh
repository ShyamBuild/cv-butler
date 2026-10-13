#!/bin/zsh
cd ~/CV_Tool || exit 1
HOLD=0; [ "$1" = "--hold" ] && { HOLD=1; shift; }
MSG="$1"; PATCH="$2"
ROOT="$(cat ~/.cvtool_last_butler_root 2>/dev/null)"
[ -z "$ROOT" ] && ROOT="/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
export GIT_TERMINAL_PROMPT=0
sync_mirror() {
  [ -d "$HOME/CV_Tool_pub/.git" ] || return 0
  cp "$HOME/CV_Tool/butler.py" "$HOME/CV_Tool/briefing.py" "$HOME/CV_Tool/wa.py" "$HOME/CV_Tool/cleaner.py" "$HOME/CV_Tool/ship.sh" "$HOME/CV_Tool/PROTOCOL.md" "$HOME/CV_Tool/butler_check.py" "$HOME/CV_Tool_pub/" 2>/dev/null || return 0
  git -C "$HOME/CV_Tool_pub" add -A 2>/dev/null || return 0
  git -C "$HOME/CV_Tool_pub" diff --cached --quiet && return 0
  git -C "$HOME/CV_Tool_pub" commit -qm "sync $H: $MSG" 2>/dev/null || return 0
  if git -C "$HOME/CV_Tool_pub" push --quiet 2>/dev/null; then
    echo "☁️ mirror pushed: github.com/ShyamBuild/cv-butler"
  else
    echo "☁️ mirror committed locally (offline - pushes with next green commit)"
  fi
}
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
  sync_mirror
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
