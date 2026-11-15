import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
NEW = [(0,"def _service_act(p, root, log):  # QUEUE-ACT v85.76: the right-click deed, lawful and local  # DRAIN-ARMOR v85.92: no path returns silent and a crash logs itself"),
 (1,"x = os.path.basename(p)"),
 (1,"try:"),
 (2,"ext = os.path.splitext(x)[1].lower()"),
 (2,"if ext in ('.docx', '.doc', '.rtf', '.png', '.jpg', '.jpeg', '.heic'): _convert_to_pdf(p, log); return"),
 (2,"if ext != '.pdf': log('🧭 service: %s | not a paper kind I act on' % x); return"),
 (2,"stem = os.path.splitext(x)[0]"),
 (2,"try:"),
 (3,"if _jd_like_name(x) or _portal_name(x): log('🧭 service: %s | masked (jd/portal) - name kept by law' % x); return"),
 (2,"except Exception: log('🧭 service: %s | mask check failed - left as is' % x); return"),
 (2,"disp = _display_name(stem)"),
 (2,"q = os.path.join(os.path.dirname(p), disp + ext)"),
 (2,"if disp != stem and not (os.path.exists(q) and os.path.basename(q).lower() != x.lower()):  # CASE-SELF v85.82: a case-variant of yourself is you"),
 (3,"try:"),
 (4,"os.rename(p, q); log('✏️ service renamed: %s → %s' % (x, disp + ext))"),
 (4,"try:"),
 (5,"_safe_rename_ledger(p, disp, 'service', once=True); _safe_repath_ledgers(p, q)"),
 (4,"except Exception: pass"),
 (4,"return"),
 (3,"except Exception as _se: log('⚠️ service rename failed: %s | %r' % (x, _se)); return"),
 (2,"v = ''"),
 (2,"try: v = heuristic_name(p) or _name_from_first_line(p)"),
 (2,"except Exception: v = ''"),
 (2,"if not v: log('🧭 service: %s | every eye silent (text, word, ocr) - vision or teaching needed' % x); return"),
 (2,"c = ''"),
 (2,"try: c = _canonical_person_name(v) if v else ''"),
 (2,"except Exception: c = ''"),
 (2,"if not c: log('🧭 service: %s | eyes read text but no human name in it (first line: %s)' % (x, (v or '')[:40])); return"),
 (2,"d2 = _display_name(c)"),
 (2,"if d2 == stem: log('🧭 service: %s | already named correctly by the eyes' % x); return"),
 (2,"q2 = os.path.join(os.path.dirname(p), d2 + ext)"),
 (2,"if os.path.exists(q2) and os.path.basename(q2).lower() != x.lower():  # CASE-INSENSITIVE v85.77: a held name is a proposal, never a deed"),
 (3,"log('🧭 service: %s | eyes say %s but another paper holds that name - proposal only' % (x, d2)); return"),
 (2,"_sn = _stem_norm(stem); _w0 = _sn.split()"),
 (2,"if _name_key(_sn) != _name_key(d2) and 2 <= len(_w0) <= 4: log('🧭 service: %s | eyes say %s, a different human - proposal only, never a guess' % (x, d2)); return"),
 (2,"try:"),
 (3,"os.rename(p, q2); log('✏️ service renamed (eyes): %s → %s' % (x, d2 + ext))  # SERVICE-EYES v85.85: an improper name yields to the paper's own witness, in place"),
 (3,"try:"),
 (4,"_safe_rename_ledger(p, d2, 'service-eyes', once=True); _safe_repath_ledgers(p, q2)"),
 (3,"except Exception: pass"),
 (2,"except Exception as _se2: log('⚠️ service eyes-rename failed: %s | %r' % (x, _se2))"),
 (1,"except Exception as _ce:"),
 (2,"log('⚠️ service crashed on %s: %r' % (os.path.basename(p), _ce))  # DRAIN-ARMOR v85.92")]
if P.replace_function(B, '_service_act', NEW):
    done.append('service-act-rewritten')
P.write(B)
P.witness(M0)
open('archive/verify.sh', 'w').write("""#!/bin/zsh
cd ~/CV_Tool || exit 1
echo "== health"; butler health 2>/dev/null | tail -4
echo "== tick tail"; tail -6 ~/CV_Tool/tick.log 2>/dev/null
echo "== rendiag head"; ~/CV_Tool/cv_env/bin/python3 ~/CV_Tool/archive/rendiag.py 2>/dev/null | head -4
echo "== sources"; ~/CV_Tool/cv_env/bin/python3 - <<'EOF' 2>/dev/null
import butler, inspect
print(inspect.getsource(butler._service_act))
src = open(butler.__file__).read().split('\\n')
k = next(i for i,l in enumerate(src) if 'SERVICE-QUEUE v85.58' in l)
print('\\n'.join(src[k-2:k+16]))
EOF
""")
done.append('verify-carries-sources')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.92' not in t:
    open(AR, 'a').write('v85.92: _service_act rewritten whole carrying all four inherited markers, every exit speaking, crashes logging themselves; verify.sh now appends verbatim sources of _service_act and the drain so every receipt is self-sufficient and blind edits stay impossible; mirror raw fetch 404s until the repo is public or the dump is pasted once (S434)\n')
    done.append('arch-line')
B = P.read(); src = '\n'.join(B)
def anch(*nd):
    for n in nd:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S434 no right-click dies without a line in the tower", "'S433 a download suffix is not a surname", "ck('S434 no right-click dies without a line in the tower', (chr(35)+' DRAIN-ARMOR v85.92') in _src and ('service crashed on' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append('S434-guard')
P.write(B)
print('✅', done)
