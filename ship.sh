#!/bin/zsh
CT="${CV_TOOL:-$HOME/CV_Tool}"; cd "$CT" || exit 1  # HOUSE-GUARDS v85.386
export GIT_TERMINAL_PROMPT=0
HOLD=0; [ "$1" = "--hold" ] && { HOLD=1; shift; }
CHECK=0; [ "$1" = "--check" ] && { CHECK=1; shift; }
MSG="$1"; PATCH="$2"
PRIMARY="/Users/apple/Downloads/Sunsoft Technology"
ROOT="${CV_ROOT:-$PRIMARY}"
LIVE_ROOTS=()
for lf in "$CT"/butler_*.lock(N); do  # HOUSE-GUARDS v85.386
  pid="$(cut -d'|' -f1 "$lf" 2>/dev/null)"
  rt="$(cut -d'|' -f2 "$lf" 2>/dev/null)"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && [ -d "$rt" ]; then LIVE_ROOTS+=("$rt"); fi
done
ROLLBACK_LIST=(butler.py stampkeeper.py briefing.py wa.py wa_warm.py cleaner.py notes/stamp_now.py ship.sh)  # HOUSE-GUARDS v85.386: the code files a red gate restores - declared ONCE, read by both rollback paths
PURITY_LIST=(butler.py summary_builder.py 'archive/*.py')  # PAPERWORK-PURITY v85.386: law 31 - what a no-patch ship may never carry dirty
do_rollback() {  # HOUSE-GUARDS v85.386: one rollback, used by the crash path and the red-gate path
  git checkout -- "${ROLLBACK_LIST[@]}" 2>/dev/null
  return 0
}
purity_dirt() {  # PAPERWORK-PURITY v85.386: the law-31 census of a no-patch tree
  git status --porcelain -- "${PURITY_LIST[@]}"
}
plan_roots() {  # HOUSE-GUARDS v85.386: exactly ONE watcher per root - the plan is deduped before anything launches
  keep=()
  for rt in "${LIVE_ROOTS[@]}"; do
    case "$rt" in
      "$ROOT"/*|"$ROOT") ;;
      *) keep+=("$rt") ;;
    esac
  done
  LIVE_ROOTS=("$ROOT" "${keep[@]}")
  LIVE_ROOTS=(${(u)LIVE_ROOTS})
}
case "$1" in  # HOUSE-GUARDS v85.386: three read-only doors, so the gate can prove these laws without shipping anything
  --roots) plan_roots; for rt in "${LIVE_ROOTS[@]}"; do echo "$rt"; done; exit 0 ;;
  --rollback) do_rollback; exit 0 ;;
  --purity)
    _pd="$(purity_dirt)"
    if [ -n "$_pd" ]; then echo '❌ PAPERWORK-PURITY (law 31): a no-patch ship may not carry code dirt'; echo "$_pd" | head -5; exit 1; fi
    echo '✅ PAPERWORK-PURITY: butler.py, summary_builder.py and archive/*.py are at HEAD'
    exit 0 ;;
esac
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
  if [ -n "$(git status --porcelain -- butler.py stampkeeper.py summary_builder.py wa_warm.py briefing.py wa.py cleaner.py notes/stamp_now.py recruit.py ship.sh PROTOCOL.md butler_check.py requirements.txt)" ]; then echo '⚠️ uncommitted CODE edits - gate them with ./ship.sh'; else echo '📚 code clean & in sync (runtime/data ignored)'; fi  # HOUSE-GUARDS v85.386
  echo "☁️ mirror head: $(git -C "$HOME/CV_Tool_pub" rev-parse --short HEAD 2>/dev/null) · local head: $LH"
  TA=$(( $(date +%s) - $(stat -f %m tick.log 2>/dev/null || echo 0) )); if [ "$TA" -gt 30 ]; then echo "🔔 BELL-DEAD: tick.log ${TA}s old (a live pid proves nothing)"; else echo "🔔 bell alive: last tick ${TA}s ago"; fi  # BELL-ALIVE v85.159: health judges the bell by the tick.log age, not by a pid
  echo '-- last log lines'; tail -2 butler_live.log 2>/dev/null
}
[ "$CHECK" = "1" ] && { health; exit 0; }
sync_mirror() {
  [ -d "$HOME/CV_Tool_pub/.git" ] || return 0
  cp "$HOME/CV_Tool/butler.py" "$HOME/CV_Tool/stampkeeper.py" "$HOME/CV_Tool/summary_builder.py" "$HOME/CV_Tool/wa_warm.py" "$HOME/CV_Tool/briefing.py" "$HOME/CV_Tool/wa.py" "$HOME/CV_Tool/cleaner.py" "$HOME/CV_Tool/ship.sh" "$HOME/CV_Tool/PROTOCOL.md" "$HOME/CV_Tool/butler_check.py" "$HOME/CV_Tool/requirements.txt" "$HOME/CV_Tool/fitrank.py" "$HOME/CV_Tool/recruit.py" "$HOME/CV_Tool/ledger.py" "$HOME/CV_Tool/cadence.py" "$HOME/CV_Tool/sem.py" "$HOME/CV_Tool/waread.py" "$HOME/CV_Tool_pub/" || return 0  # HOUSE-GUARDS v85.386
  cp "$HOME/CV_Tool/wa_template.txt" "$HOME/CV_Tool_pub/" 2>/dev/null
  mkdir -p "$HOME/CV_Tool_pub/archive"
  for _af in dump.txt patchlib.py rendiag.py verify.sh mkdump.sh; do cp "$HOME/CV_Tool/archive/$_af" "$HOME/CV_Tool_pub/archive/$_af" 2>/dev/null; done  # MIRROR-TOOLS v85.93: publish the dump and the primitives with every commit, so every future lap is written against read code fetched from the mirror
  mkdir -p "$HOME/CV_Tool_pub/templates"
  cp "$HOME/CV_Tool/templates/"*.txt "$HOME/CV_Tool_pub/templates/" 2>/dev/null
  git -C "$HOME/CV_Tool_pub" add -A || return 0
  git -C "$HOME/CV_Tool_pub" diff --cached --quiet && return 0
  git -C "$HOME/CV_Tool_pub" commit -qm "sync $H: $MSG" || return 0
  if git -C "$HOME/CV_Tool_pub" push --quiet; then
    echo '☁️ mirror pushed: github.com/ShyamBuild/cv-butler'
  else
    echo '☁️ mirror committed locally (offline - pushes with next green commit)'
  fi
}
resume_all() {
  plan_roots  # HOUSE-GUARDS v85.386: the plan is deduped first - one watcher per root, never two
  for rt in "${LIVE_ROOTS[@]}"; do
    nohup cv_env/bin/python3 butler.py "$rt" >> butler_live.log 2>&1 &
    disown
  done
  sleep 3
  echo "🤵 butler(s) live on $H: $(for rt in "${LIVE_ROOTS[@]}"; do printf '%s ' "$(basename "$rt")"; done)"
}
if [ -n "$PATCH" ]; then
  echo "-- patch: $PATCH"
  /usr/bin/python3 "$PATCH" || { echo '❌ patch crashed - rolling back to last proven commit'; do_rollback; exit 1; }  # HOUSE-GUARDS v85.386
fi
pkill -f butler.py || true
sleep 1
echo '-- selftest gate (butler paused - no races)'
OUT="$(cv_env/bin/python3 butler.py --selftest "$ROOT" 2>&1)"
echo "$OUT" | grep "FAIL\|SKILLS MISSING" | head -10  # GATE-LOUD v81.69: every red line before the window
echo "$OUT" | tail -40
TWINS="$(twins_check "$ROOT")"
if echo "$OUT" | grep -q "ALL GREEN" && [ -z "$TWINS" ]; then
  if [ -z "$PATCH" ] && [ -n "$(purity_dirt)" ]; then  # PAPERWORK-PURITY v85.386: law 31 - a no-patch ship carries no code dirt
      echo '❌ PAPERWORK-PURITY (law 31) - a no-patch ship may not commit code dirt:'
      purity_dirt | head -5
      resume_all
      exit 1
  fi
  git add -A
  git -c user.email=butler@local -c user.name=butler commit -qm "$MSG (selftest ALL GREEN)" || echo '(nothing new to commit)'
  H="$(git rev-parse --short HEAD)"
  echo "✅ committed $H: $MSG"
  sync_mirror
  if [ "$HOLD" = "1" ]; then
    echo '🕐 --hold given: restart is yours'
  else
    resume_all
  fi
  health
else
  echo "❌ NOT GREEN (twins: $TWINS) - rollback if dirty, then relaunch proven butler(s)"
  if [ -n "$(git status --porcelain -- "${ROLLBACK_LIST[@]}")" ]; then  # HOUSE-GUARDS v85.386
    do_rollback  # HOUSE-GUARDS v85.386
    echo '   proven state restored.'
  else
    echo '   working tree already clean - nothing to roll back.'
  fi
  H="$(git rev-parse --short HEAD)"
  resume_all
  echo '   paste the FAIL lines above; next patch starts clean.'
  exit 1
fi
