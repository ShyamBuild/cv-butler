import ast, os, subprocess
done = []
r0 = subprocess.run(['zsh', '-n', 'ship.sh'], capture_output=True, text=True)
print('current ship.sh zsh -n:', 'CLEAN' if r0.returncode == 0 else r0.stderr.strip()[:200])
p = 'butler.py'; L = open(p).read().split('\n')
i = next((k for k, l in enumerate(L) if 'zz_garbage_test.pdf' in l and 'tmp =' in l), None)
if i is not None:
    a = i - 1
    j = next(k for k in range(i, len(L)) if 'os.remove(os.path.join(root, f))' in L[k])
    d = len(L[a]) - len(L[a].lstrip())
    L[a:j+1] = [d*' ' + 'src = None',
                d*' ' + 'for _f in sorted(os.listdir(root)):',
                d*' ' + "    if _f.lower().endswith('.pdf') and not _f.startswith('zz_'): src = os.path.join(root, _f); break",
                d*' ' + "tmp = os.path.join(root, 'zz_garbage_test.pdf')",
                d*' ' + 'if src:',
                d*' ' + "    b0 = os.path.splitext(os.path.basename(src))[0]",
                d*' ' + "    pre = {f for f in os.listdir(root) if f.startswith(b0 + '_') or f.startswith('zz_garbage_test')}",
                d*' ' + '    shutil.copy(src, tmp)',
                d*' ' + '    B.route(tmp, print)',
                d*' ' + "    ck('S4 wrong-name repair', not os.path.exists(tmp))",
                d*' ' + "    post = {f for f in os.listdir(root) if f.startswith(b0 + '_') or f.startswith('zz_garbage_test')}",
                d*' ' + '    for f in post - pre:',
                d*' ' + '        try: os.remove(os.path.join(root, f))',
                d*' ' + '        except Exception: pass',
                d*' ' + 'else:',
                d*' ' + "    ck('S4 wrong-name repair', False, 'no root pdf to test with')"]
    done.append('S4-anchor-robust')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
SHIP = r'''#!/bin/zsh
cd ~/CV_Tool || exit 1
export GIT_TERMINAL_PROMPT=0
HOLD=0; [ "$1" = "--hold" ] && { HOLD=1; shift; }
CHECK=0; [ "$1" = "--check" ] && { CHECK=1; shift; }
MSG="$1"; PATCH="$2"
ROOT="$(cat ~/.cvtool_last_butler_root 2>/dev/null)"
[ -z "$ROOT" ] && ROOT="/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
twins_check() {
  cv_env/bin/python3 - "$1" << 'PY'
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
}
health() {
  echo '-- health'
  if pgrep -f butler.py > /dev/null; then echo '🤵 process: running'; else echo '⚠️ process: NOT running'; fi
  LH="$(git rev-parse --short HEAD)"
  LB="$(grep -o 'git [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]' butler_live.log 2>/dev/null | tail -1 | awk '{print $2}')"
  if [ "$LH" = "$LB" ]; then echo "🔁 version: live = committed ($LH)"; else echo "⚠️ version drift: live=${LB:-?} vs committed=$LH"; fi
  if [ -n "$(git status --porcelain -- butler.py briefing.py wa.py cleaner.py ship.sh PROTOCOL.md butler_check.py requirements.txt)" ]; then echo '⚠️ uncommitted CODE edits - gate them with ./ship.sh'; else echo '📚 code clean & in sync (runtime/data ignored)'; fi
  echo "☁️ mirror head: $(git -C "$HOME/CV_Tool_pub" rev-parse --short HEAD 2>/dev/null) · local head: $LH"
  echo '-- last log lines'; tail -2 butler_live.log 2>/dev/null
}
[ "$CHECK" = "1" ] && { health; exit 0; }
sync_mirror() {
  [ -d "$HOME/CV_Tool_pub/.git" ] || return 0
  cp "$HOME/CV_Tool/butler.py" "$HOME/CV_Tool/briefing.py" "$HOME/CV_Tool/wa.py" "$HOME/CV_Tool/cleaner.py" "$HOME/CV_Tool/ship.sh" "$HOME/CV_Tool/PROTOCOL.md" "$HOME/CV_Tool/butler_check.py" "$HOME/CV_Tool/requirements.txt" "$HOME/CV_Tool_pub/" || return 0
  git -C "$HOME/CV_Tool_pub" add -A || return 0
  git -C "$HOME/CV_Tool_pub" diff --cached --quiet && return 0
  git -C "$HOME/CV_Tool_pub" commit -qm "sync $H: $MSG" || return 0
  if git -C "$HOME/CV_Tool_pub" push --quiet; then
    echo '☁️ mirror pushed: github.com/ShyamBuild/cv-butler'
  else
    echo '☁️ mirror committed locally (offline - pushes with next green commit)'
  fi
}
if [ -n "$PATCH" ]; then
  echo "-- patch: $PATCH"
  /usr/bin/python3 "$PATCH" || { echo '❌ patch crashed - rolling back to last proven commit'; git checkout -- butler.py briefing.py wa.py cleaner.py; exit 1; }
fi
pkill -f butler.py || true
sleep 1
echo '-- selftest gate (butler paused - no races)'
OUT="$(cv_env/bin/python3 butler.py --selftest "$ROOT" 2>&1)"
echo "$OUT" | tail -20
TWINS="$(twins_check "$ROOT")"
if echo "$OUT" | grep -q "ALL GREEN" && [ -z "$TWINS" ]; then
  git add -A
  git -c user.email=butler@local -c user.name=butler commit -qm "$MSG (selftest ALL GREEN)" || echo '(nothing new to commit)'
  H="$(git rev-parse --short HEAD)"
  echo "✅ committed $H: $MSG"
  sync_mirror
  if [ "$HOLD" = "1" ]; then
    echo '🕐 --hold given: restart is yours'
  else
    nohup cv_env/bin/python3 butler.py "$ROOT" >> butler_live.log 2>&1 &
    disown
    sleep 3
    if pgrep -f butler.py > /dev/null; then echo "🤵 butler live on $H (background)"; else echo '⚠️ butler did not stay up - paste: tail -20 butler_live.log'; fi
  fi
  health
else
  echo "❌ NOT GREEN (twins: $TWINS) - rollback if dirty, then relaunch proven butler"
  if [ -n "$(git status --porcelain -- butler.py briefing.py wa.py cleaner.py)" ]; then
    git checkout -- butler.py briefing.py wa.py cleaner.py
    echo '   proven state restored.'
  else
    echo '   working tree already clean - nothing to roll back.'
  fi
  nohup cv_env/bin/python3 butler.py "$ROOT" >> butler_live.log 2>&1 &
  disown
  sleep 2
  echo "🤕 proven butler relaunched on $(git rev-parse --short HEAD)"
  echo '   paste the FAIL lines above; next patch starts clean.'
  exit 1
fi
'''
open('ship.sh.new', 'w').write(SHIP)
os.chmod('ship.sh.new', 0o755)
r1 = subprocess.run(['zsh', '-n', 'ship.sh.new'], capture_output=True, text=True)
if r1.returncode != 0:
    os.remove('ship.sh.new')
    raise SystemExit('ship.sh.new failed zsh -n: ' + r1.stderr.strip()[:300])
done.append('ship-v6-staged-zsh-clean')
P = open('PROTOCOL.md').read()
if 'zsh -n' not in P:
    P = P.rstrip() + '\n11. Shell scripts are validated with `zsh -n` (syntax check, never executes) before staging; per-line quote-parity is NOT a valid test (heredocs span lines). Never rewrite ship.sh from inside a running ship.sh.\n'
    open('PROTOCOL.md', 'w').write(P)
    done.append('protocol-rule-11')
print('✅', done or 'nothing missing')
