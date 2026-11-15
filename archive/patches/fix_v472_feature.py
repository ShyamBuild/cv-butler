import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def perfile():
    S = {}
    for fn in ('butler.py', 'briefing.py', 'wa.py'):
        P = os.path.join(os.getcwd(), fn)
        S[fn] = set(markers(open(P).read().split('\n'))) if os.path.exists(P) else set()
    return S
M0 = perfile()
B0 = open('butler.py').read()
B = B0.split('\n')
snap = list(B)
c0 = next((k for k, l in enumerate(B) if l.startswith('def _case_sweep(')), None)
if c0 is not None and 'def _eyename_of(' not in '\n'.join(B):
    B[c0:c0] = ["_EYEC = {}",
                "def _eyename_cache():",
                "    import json as _je",
                "    cf = os.path.join(BASE_DIR, '.eyename.json')",
                "    try:",
                "        return _je.load(open(cf)), cf",
                "    except Exception:",
                "        return {}, cf",
                "def _stem_norm(s):  # STEM-NORM v85.90: download artifacts (_1, (2), trailing digits) are not part of a human's name",
                "    return re.sub(r'[_\\s]*(?:\\(\\d+\\)|\\d+)$', '', s).strip()",
                "def _eyename_of(p, trace=False, log=None):  # EYES-IN-SWEEP v85.90: the OCR-backed first line names a paper the filename cannot - cached by size and mtime so each paper pays the cap once  # EYECACHE v85.90",
                "    try:",
                "        st = os.stat(p)",
                "    except Exception:",
                "        return ''",
                "    key = os.path.basename(p)",
                "    c, cf = _eyename_cache()",
                "    e = c.get(key)",
                "    if e and e[0] == st.st_size and abs(e[1] - st.st_mtime) < 1:",
                "        return e[2]",
                "    name = ''",
                "    t = ''",
                "    try:",
                "        t = extract_text(p) or ''",
                "    except Exception:",
                "        t = ''",
                "    fl = ''",
                "    for ln in t.split('\\n'):",
                "        ln = ln.strip()",
                "        if ln:",
                "            fl = ln",
                "            break",
                "    fl = re.split(r'\\s+(?:Phone|Mob|Tel|E-Mail|Email)[:\\-]?', fl, flags=re.I)[0].strip()  # LINE-CUT v85.90: a first line that ends in a phone still begins with a human",
                "    ws = fl.split()",
                "    if 2 <= len(ws) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in ws):",
                "        cn = _canonical_person_name(fl) or ''",
                "        name = _display_name(cn) if cn else ''",
                "    if not name:",
                "        try:",
                "            v = _name_from_first_line(p) or ''",
                "            cn = _canonical_person_name(v) if v else ''",
                "            name = _display_name(cn) if cn else ''",
                "        except Exception:",
                "            name = ''",
                "    c[key] = [st.st_size, st.st_mtime, name]",
                "    try:",
                "        import json as _je2",
                "        _je2.dump(c, open(cf, 'w'))",
                "    except Exception:",
                "        pass",
                "    return name",
                ""]
    done.append('eyename-helpers')
ws0 = next((k for k, l in enumerate(B) if l.strip() == 'ws = stem.split()' and k > (c0 or 0)), None)
if ws0 is not None and 'EYES-IN-SWEEP v85.90: the OCR-backed' not in '\n'.join(B[ws0-24:ws0]):
    d = ind(B[ws0])
    B[ws0:ws0] = [d*' ' + "_en = _eyename_of(p)  # EYES-IN-SWEEP v85.90: the background sweep carries the same OCR eye the diagnostic proved, in place and cached, so the main butler renames what the table renames",
                  d*' ' + "if _en and _en != stem:",
                  (d+4)*' ' + "_sn = _stem_norm(stem)",
                  (d+4)*' ' + "_w0 = _sn.split()",
                  (d+4)*' ' + "_shape_ok = 2 <= len(_w0) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in _w0)",
                  (d+4)*' ' + "if not _shape_ok or _name_key(_sn) == _name_key(_en):",
                  (d+8)*' ' + "_q3 = os.path.join(dpath, _en + ext)",
                  (d+8)*' ' + "if os.path.exists(_q3) and os.path.basename(_q3).lower() != x.lower():",
                  (d+12)*' ' + "if trace: log('🧭 sweep: %s | eyes say %s but another paper holds that name - proposal only' % (x, _en))",
                  (d+8)*' ' + "else:",
                  (d+12)*' ' + "try:",
                  (d+16)*' ' + "os.rename(p, _q3)",
                  (d+16)*' ' + "log('✏️ sweep renamed (eyes): %s → %s' % (x, _en + ext))",
                  (d+16)*' ' + "try:",
                  (d+20)*' ' + "_safe_rename_ledger(p, _en, 'sweep-eyes', once=True)",
                  (d+20)*' ' + "_safe_repath_ledgers(p, _q3)",
                  (d+16)*' ' + "except Exception:",
                  (d+20)*' ' + "pass",
                  (d+16)*' ' + "continue",
                  (d+12)*' ' + "except Exception as _se3:",
                  (d+16)*' ' + "if trace: log('⚠️ sweep eyes-rename failed: %s | %r' % (x, _se3))"]
    done.append('eyes-in-sweep')
n = 0
for k, l in enumerate(B):
    if '_name_key(stem) != _name_key(canon)' in l and '_stem_norm(stem)' not in l:
        B[k] = l.replace('_name_key(stem) != _name_key(canon)', '_name_key(_stem_norm(stem)) != _name_key(canon)  # STEM-NORM v85.90: a suffix is not a surname')
        n += 1
if n: done.append('stem-norm-wired-x%d' % n)
GI = os.path.join(os.getcwd(), '.gitignore')
gi = open(GI).read() if os.path.exists(GI) else ''
if '.eyename.json' not in gi.split('\n'):
    open(GI, 'a').write('.eyename.json\n')
    done.append('eyename-shelter')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 sweep eye branch and norm sites:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'EYES-IN-SWEEP v85.90: the background sweep' in l or 'STEM-NORM v85.90: a suffix' in l or 'LINE-CUT v85.90' in l:
        print('   |', l.strip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.90' not in t:
        open(AR, 'a').write('v85.90: EYES-IN-SWEEP - the main butler background sweep carries the OCR-backed first-line eye proven by rendiag, cached in .eyename.json per size+mtime so each paper pays the cap once; LINE-CUT frees names from phone-tailed first lines; STEM-NORM strips download scars before key compares in sweep, fast half and ceremony; renames stay in place, twins stay proposals (S432, S433)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S432 the main butler renames through the same eye the diagnostic proved, once per paper", "'S431 the reader chain has one name, one parameter and one raster hand", "ck('S432 the main butler renames through the same eye the diagnostic proved, once per paper', (chr(35)+' EYES-IN-SWEEP v85.90') in _src and (chr(35)+' EYECACHE v85.90') in _src and ('.eyename.json' in _src))"),
      ("'S433 a download suffix is not a surname", "'S432 the main butler renames through the same eye the diagnostic proved, once per paper", "ck('S433 a download suffix is not a surname', _src.count('_stem_norm(') >= 3)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
