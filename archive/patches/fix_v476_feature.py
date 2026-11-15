import sys, os, subprocess
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
S = P.read('ship.sh')
if P.insert_after(S, 'cp "$HOME/CV_Tool/wa_template.txt" "$HOME/CV_Tool_pub/" 2>/dev/null', [
    (0, 'mkdir -p "$HOME/CV_Tool_pub/archive"'),
    (0, 'for _af in dump.txt patchlib.py rendiag.py verify.sh; do cp "$HOME/CV_Tool/archive/$_af" "$HOME/CV_Tool_pub/archive/$_af" 2>/dev/null; done  # MIRROR-TOOLS v85.93: publish the dump and the primitives with every commit, so every future lap is written against read code fetched from the mirror')]):
    done.append('mirror-tools')
P.write(S, 'ship.sh')
open('archive/verify.sh', 'w').write("""#!/bin/zsh
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
echo "== dump lines: $(wc -l < archive/dump.txt)"
echo "== health"; butler health 2>/dev/null | tail -4
echo "== tick tail"; tail -6 ~/CV_Tool/tick.log 2>/dev/null
echo "== rendiag head"; ~/CV_Tool/cv_env/bin/python3 ~/CV_Tool/archive/rendiag.py 2>/dev/null | head -4
echo "== sources"; sed -n '1,40p' archive/dump.txt
""")
done.append('verify-regenerates-dump')
subprocess.run(['/bin/zsh', '-c', 'cd ~/CV_Tool && ~/CV_Tool/cv_env/bin/python3 - > archive/dump.txt 2>&1 <<\'EOF\'\nimport butler, inspect\nfor f in (\'_service_act\',\'_case_sweep\',\'_event_tick\',\'_tick_loop\',\'extract_text_ocr\',\'_name_from_first_line\',\'heuristic_name\',\'_canonical_person_name\',\'_display_name\',\'_fast_rename\',\'rename_diag\',\'_eyename_of\',\'_stem_norm\',\'_convert_to_pdf\',\'_jd_like_name\',\'_portal_name\',\'_rename_ledger\',\'_repath_ledgers\',\'_lock_root\',\'desk_load\',\'seat_rename_check\'):\n    o = getattr(butler, f, None)\n    print(\'==== %s ====\' % f); print(inspect.getsource(o) if o else \'MISSING\')\nsrc = open(butler.__file__).read().split(\'\\n\')\nk = next(i for i,l in enumerate(src) if \'SERVICE-QUEUE v85.58\' in l)\nprint(\'==== drain region ====\'); print(\'\\n\'.join(src[k-3:k+22]))\nprint(\'==== module constants ====\')\nfor i,l in enumerate(src):\n    if l.startswith(\'OCRBIN\') or l.startswith(\'OCR_SEM\') or l.startswith(\'extract_text =\') or l.startswith(\'BASE_DIR\'):\n        print(i+1, l)\nEOF'], check=False)
print('🔎 dump regenerated:', os.path.getsize('archive/dump.txt'), 'bytes')
B = P.read()
src = '\n'.join(B)
def anch(*nd):
    for n in nd:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S435 the mirror carries the dump and the primitives, so reading precedes every edit", "'S434 no right-click dies without a line in the tower", "ck('S435 the mirror carries the dump and the primitives, so reading precedes every edit', ('MIRROR-TOOLS v85.93' in open(os.path.join(BASE_DIR, 'ship.sh')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append('S435-guard')
P.write(B)
P.witness(M0)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.93' not in t:
    open(AR, 'a').write('v85.93: MIRROR-TOOLS - sync_mirror publishes archive/dump.txt, patchlib.py, rendiag.py and verify.sh with every commit and verify.sh regenerates the dump first, so the assistant reads exact current sources from the public mirror before writing any patch; raw fetch of the 328KB butler.py 404s through the fetcher, the dump route carries the needed truth in small bytes (S435)\n')
    done.append('arch-line')
print('✅', done)
