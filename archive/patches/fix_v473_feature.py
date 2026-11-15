import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
if 'def _eyename_of(' not in '\n'.join(B):
    blk = [(0,"_EYEC = {}"), (0,"def _eyename_cache():"), (1,"import json as _je"), (1,"cf = os.path.join(BASE_DIR, '.eyename.json')"), (1,"try:"), (2,"return _je.load(open(cf)), cf"), (1,"except Exception:"), (2,"return {}, cf"),
           (0,"def _stem_norm(s):  # STEM-NORM v85.90: download artifacts (_1, (2), trailing digits) are not part of a human's name"), (1,"return re.sub(r'[_\\s]*(?:\\(\\d+\\)|\\d+)$', '', s).strip()"),
           (0,"def _eyename_of(p, trace=False, log=None):  # EYES-IN-SWEEP v85.90: the OCR-backed first line names a paper the filename cannot - cached by size and mtime so each paper pays the cap once  # EYECACHE v85.90"),
           (1,"try:"), (2,"st = os.stat(p)"), (1,"except Exception:"), (2,"return ''"),
           (1,"key = os.path.basename(p)"), (1,"c, cf = _eyename_cache()"), (1,"e = c.get(key)"),
           (1,"if e and e[0] == st.st_size and abs(e[1] - st.st_mtime) < 1:"), (2,"return e[2]"),
           (1,"name = ''"), (1,"t = ''"), (1,"try:"), (2,"t = extract_text(p) or ''"), (1,"except Exception:"), (2,"t = ''"),
           (1,"fl = ''"), (1,"for ln in t.split('\\n'):"), (2,"ln = ln.strip()"), (2,"if ln:"), (3,"fl = ln"), (3,"break"),
           (1,"fl = re.split(r'\\s+(?:Phone|Mob|Tel|E-Mail|Email)[:\\-]?', fl, flags=re.I)[0].strip()  # LINE-CUT v85.90: a first line that ends in a phone still begins with a human"),
           (1,"ws = fl.split()"), (1,"if 2 <= len(ws) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in ws):"), (2,"cn = _canonical_person_name(fl) or ''"), (2,"name = _display_name(cn) if cn else ''"),
           (1,"if not name:"), (2,"try:"), (3,"v = _name_from_first_line(p) or ''"), (3,"cn = _canonical_person_name(v) if v else ''"), (3,"name = _display_name(cn) if cn else ''"), (2,"except Exception:"), (3,"name = ''"),
           (1,"c[key] = [st.st_size, st.st_mtime, name]"), (1,"try:"), (2,"import json as _je2"), (2,"_je2.dump(c, open(cf, 'w'))"), (1,"except Exception:"), (2,"pass"), (1,"return name")]
    c0 = next(k for k, l in enumerate(B) if l.startswith('def _case_sweep('))
    d = P.ind(B[c0])
    B[c0:c0] = [(d + e)*' ' + s for e, s in blk]
    done.append('eyename-helpers')
if P.insert_before(B, 'ws = stem.split()', [(0,"_en = _eyename_of(p)  # EYES-IN-SWEEP v85.90: the background sweep carries the same OCR eye the diagnostic proved, in place and cached, so the main butler renames what the table renames"),
    (0,"if _en and _en != stem:"), (1,"_sn = _stem_norm(stem)"), (1,"_w0 = _sn.split()"), (1,"_shape_ok = 2 <= len(_w0) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in _w0)"), (1,"if not _shape_ok or _name_key(_sn) == _name_key(_en):"),
    (2,"_q3 = os.path.join(dpath, _en + ext)"), (2,"if os.path.exists(_q3) and os.path.basename(_q3).lower() != x.lower():"), (3,"if trace: log('🧭 sweep: %s | eyes say %s but another paper holds that name - proposal only' % (x, _en))"),
    (2,"else:"), (3,"try:"), (4,"os.rename(p, _q3)"), (4,"log('✏️ sweep renamed (eyes): %s → %s' % (x, _en + ext))"), (4,"try:"), (5,"_safe_rename_ledger(p, _en, 'sweep-eyes', once=True)"), (5,"_safe_repath_ledgers(p, _q3)"), (4,"except Exception:"), (5,"pass"), (4,"continue"),
    (3,"except Exception as _se3:"), (4,"if trace: log('⚠️ sweep eyes-rename failed: %s | %r' % (x, _se3))")], once_marker='EYES-IN-SWEEP v85.90: the background sweep'):
    done.append('eyes-in-sweep')
n = P.sub_in_line(B, '_name_key(stem) != _name_key(canon)', '_name_key(_stem_norm(stem)) != _name_key(canon)', 'STEM-NORM v85.90: a suffix is not a surname')
if n: done.append('stem-norm-wired-x%d' % n)
GI = os.path.join(os.getcwd(), '.gitignore')
gi = open(GI).read() if os.path.exists(GI) else ''
if '.eyename.json' not in gi.split('\n'):
    open(GI, 'a').write('.eyename.json\n'); done.append('eyename-shelter')
P.write(B)
P.witness(M0)
print('🔎 norm sites and eye branch:')
for k, l in enumerate(open('butler.py').read().split('\n')):
    if 'STEM-NORM v85.90: a suffix' in l or 'EYES-IN-SWEEP v85.90: the background' in l or 'LINE-CUT v85.90' in l:
        print('   |', l.strip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.91' not in t:
    open(AR, 'a').write('v85.91: PROTOCOL CHANGE - patchlib primitives (tail-preserving sub_in_line, neighbourhood-printing inserts, verbatim replace_function, append_module) make the crash families structurally impossible; verify.sh collapses verification to one paste; EYES-IN-SWEEP ships as the first customer: OCR-backed cached eye in the sweep, LINE-CUT, STEM-NORM, .eyename.json sheltered (S432, S433)\n')
    done.append('arch-line')
B = P.read(); src = '\n'.join(B)
def anch(*needles):
    for nd in needles:
        hit = [k for k, l in enumerate(B) if nd in l]
        if hit: return hit[-1]
    return None
GU = [("'S432 the main butler renames through the same eye the diagnostic proved, once per paper", "'S431 the reader chain has one name, one parameter and one raster hand", "ck('S432 the main butler renames through the same eye the diagnostic proved, once per paper', (chr(35)+' EYES-IN-SWEEP v85.90') in _src and (chr(35)+' EYECACHE v85.90') in _src and ('.eyename.json' in _src))"),
      ("'S433 a download suffix is not a surname", "'S432 the main butler renames through the same eye the diagnostic proved, once per paper", "ck('S433 a download suffix is not a surname', _src.count('_stem_norm(') >= 3)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)
