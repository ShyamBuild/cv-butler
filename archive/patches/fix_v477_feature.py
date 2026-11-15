import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
PL = os.path.join(os.getcwd(), 'archive', 'patchlib.py')
pl = open(PL).read()
if 'def write_raw(' not in pl:
    old = "def write(B, fn='butler.py'):\n    src = '\\n'.join(B); ast.parse(src); open(fn, 'w').write(src); return src"
    new = ("def write(B, fn='butler.py'):\n"
           "    src = '\\n'.join(B)\n"
           "    if fn.endswith('.py'): ast.parse(src)\n"
           "    open(fn, 'w').write(src); return src\n"
           "def write_raw(B, fn):  # PATCHLIB v85.94: shells and texts write without a python parser judging them\n"
           "    open(fn, 'w').write('\\n'.join(B)); return True\n"
           "def preflight(B, M0, fn='butler.py'):  # PATCHLIB v85.94: parse, witness and marker-carry checked BEFORE any write, so a bad lap dies childless\n"
           "    src = '\\n'.join(B)\n"
           "    if fn.endswith('.py'): ast.parse(src)\n"
           "    cur = set(markers(src.split('\\n')))\n"
           "    return M0.get(fn, set()) - cur")
    assert old in pl
    pl = pl.replace(old, new)
    open(PL, 'w').write(pl)
    done.append('patchlib-v2')
import importlib
importlib.reload(P)
S = P.read('ship.sh')
if P.insert_after(S, 'cp "$HOME/CV_Tool/wa_template.txt" "$HOME/CV_Tool_pub/" 2>/dev/null', [
    (0, 'mkdir -p "$HOME/CV_Tool_pub/archive"'),
    (0, 'for _af in dump.txt patchlib.py rendiag.py verify.sh mkdump.sh; do cp "$HOME/CV_Tool/archive/$_af" "$HOME/CV_Tool_pub/archive/$_af" 2>/dev/null; done  # MIRROR-TOOLS v85.93: publish the dump and the primitives with every commit, so every future lap is written against read code fetched from the mirror')]):
    done.append('mirror-tools')
lost = P.preflight(S, {}, 'ship.sh') if hasattr(P, 'preflight') else set()
P.write_raw(S, 'ship.sh')
open('archive/mkdump.sh', 'w').write("""#!/bin/zsh
cd ~/CV_Tool || exit 1
~/CV_Tool/cv_env/bin/python3 - <<'EOF' > archive/dump.txt 2>&1
import butler, inspect
for f in ('_service_act','_case_sweep','_event_tick','_tick_loop','_tick_log','extract_text_ocr','_name_from_first_line','heuristic_name','_canonical_person_name','_display_name','_fast_rename','rename_diag','_eyename_of','_stem_norm','_convert_to_pdf','_pages_pdf','_jd_like_name','_portal_name','_rename_ledger','_repath_ledgers','_lock_root','desk_load','seat_rename_check'):
    o = getattr(butler, f, None)
    print('==== %s ====' % f); print(inspect.getsource(o) if o else 'MISSING')
src = open(butler.__file__).read().split('\\n')
k = next(i for i,l in enumerate(src) if 'SERVICE-QUEUE v85.58' in l)
print('==== drain region ===='); print('\\n'.join(src[k-3:k+22]))
print('==== module constants ====')
for i,l in enumerate(src):
    if l.startswith('OCRBIN') or l.startswith('OCR_SEM') or l.startswith('extract_text =') or l.startswith('BASE_DIR'):
        print(i+1, l)
EOF
""")
os.chmod('archive/mkdump.sh', 0o755)
open('archive/verify.sh', 'w').write("""#!/bin/zsh
~/CV_Tool/archive/mkdump.sh
echo "== dump lines: $(wc -l < ~/CV_Tool/archive/dump.txt)"
echo "== health"; butler health 2>/dev/null | tail -4
echo "== tick tail"; tail -6 ~/CV_Tool/tick.log 2>/dev/null
echo "== rendiag head"; ~/CV_Tool/cv_env/bin/python3 ~/CV_Tool/archive/rendiag.py 2>/dev/null | head -4
echo "== sources head"; sed -n '1,30p' ~/CV_Tool/archive/dump.txt
""")
os.chmod('archive/verify.sh', 0o755)
done.append('verify-regenerates-dump')
os.system('/bin/zsh ~/CV_Tool/archive/mkdump.sh')
print('🔎 dump bytes:', os.path.getsize('archive/dump.txt'))
B = P.read()
lost = P.preflight(B, M0) if hasattr(P, 'preflight') else set()
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B)
P.witness(M0)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.94' not in t:
    open(AR, 'a').write('v85.94: PATCHLIB v2 - write parses only python, write_raw frees shells (the ast.parse-on-ship.sh crash family dies), preflight checks parse+witness+markers before any write so bad laps die childless; MIRROR-TOOLS publishes dump/patchlib/rendiag/verify/mkdump with every commit (S435, S436)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for n in nd:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S435 the mirror carries the dump and the primitives, so reading precedes every edit", "'S434 no right-click dies without a line in the tower", "ck('S435 the mirror carries the dump and the primitives, so reading precedes every edit', ('MIRROR-TOOLS v85.93' in open(os.path.join(BASE_DIR, 'ship.sh')).read()))"),
      ("'S436 a bad lap dies childless, before any file is written", "'S435 the mirror carries the dump and the primitives, so reading precedes every edit", "ck('S436 a bad lap dies childless, before any file is written', ('def preflight(' in open(os.path.join(BASE_DIR, 'archive', 'patchlib.py')).read()) and ('def write_raw(' in open(os.path.join(BASE_DIR, 'archive', 'patchlib.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)
