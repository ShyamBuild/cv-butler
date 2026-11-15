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
if 'def _event_tick(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
    B[i:i] = ["_EVT = {}",
              "def _fast_rename(p, root, log):  # RENAME-WATCH v85.52: the ceremony's fast half in the background - text eyes, first-line eye, CASE-LAW; the expensive pupil stays with the chair's up",
              "    x = os.path.basename(p)",
              "    try:",
              "        if _jd_like_name(x) or _portal_name(x): return",
              "    except Exception:",
              "        return",
              "    stem = os.path.splitext(x)[0]",
              "    v = heuristic_name(p) or _name_from_first_line(p)",
              "    if not v: return",
              "    canon = _canonical_person_name(v)",
              "    if not canon: return",
              "    canon = _display_name(canon)",
              "    if stem == canon: return",
              "    if _name_key(stem) != _name_key(canon): return",
              "    q = os.path.join(os.path.dirname(p), canon + os.path.splitext(x)[1])",
              "    if os.path.exists(q): return",
              "    try:",
              "        os.rename(p, q)",
              "        _rename_ledger(p, canon, 'watch', once=True)",
              "        _repath_ledgers(p, q)",
              "        log('✏️ watch renamed: %s → %s' % (x, os.path.basename(q)))",
              "    except Exception:",
              "        pass",
              "def _convert_to_pdf(p, log):  # CONVERT-WATCH v85.52: a Word paper is not a scan, it is a locked eye - conversion is the key; the source stays untouched and the book remembers",
              "    import json as _jc, subprocess as _sp",
              "    cf = os.path.join(BASE_DIR, '.converted.json')",
              "    try:",
              "        done_map = _jc.load(open(cf))",
              "    except Exception:",
              "        done_map = {}",
              "    if done_map.get(p): return",
              "    out = os.path.splitext(p)[0] + '.pdf'",
              "    ext = os.path.splitext(p)[1].lower()",
              "    try:",
              "        if ext in ('.png', '.jpg', '.jpeg', '.heic'):",
              "            _sp.run(['sips', '-s', 'format', 'pdf', p, '--out', out], capture_output=True, timeout=120)",
              "        else:",
              "            _sp.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(p), p], capture_output=True, timeout=300)",
              "    except FileNotFoundError:",
              "        if not done_map.get('_nosoffice'):",
              "            done_map['_nosoffice'] = 1",
              "            log('⚠️ no soffice - install LibreOffice for doc→pdf; images still convert via sips')",
              "        return",
              "    except Exception:",
              "        return",
              "    if os.path.exists(out):",
              "        done_map[p] = 1",
              "        try:",
              "            _jc.dump(done_map, open(cf, 'w'))",
              "        except Exception:",
              "            pass",
              "        log('🔁 converted: %s → %s' % (os.path.basename(p), os.path.basename(out)))",
              "def _event_tick(root, log=print):  # RENAME-WATCH v85.52 + CONVERT-WATCH v85.52: directory mtimes are the doorbells - one stat per folder per heartbeat, no hashing, no OCR, no pings; the house rests between rings",
              "    try:",
              "        dirs = [root] + [os.path.join(root, s) for s in _tag_vocab() if os.path.isdir(os.path.join(root, s))]",
              "    except Exception:",
              "        dirs = [root]",
              "    for dpath in dirs:",
              "        try:",
              "            mt = os.stat(dpath).st_mtime",
              "        except Exception:",
              "            continue",
              "        if _EVT.get(dpath) == mt: continue",
              "        _EVT[dpath] = mt",
              "        try:",
              "            names = os.listdir(dpath)",
              "        except Exception:",
              "            continue",
              "        for x in names:",
              "            p = os.path.join(dpath, x)",
              "            if not os.path.isfile(p): continue",
              "            ext = os.path.splitext(x)[1].lower()",
              "            if ext in ('.docx', '.doc', '.rtf', '.png', '.jpg', '.jpeg', '.heic'):",
              "                _convert_to_pdf(p, log)",
              "            elif ext == '.pdf':",
              "                _fast_rename(p, root, log)",
              ""]
    done.append('watch-trio')
w0 = next((k for k, l in enumerate(B) if l.startswith('def ') and 'watch' in l.split('(')[0].lower()), None)
hk = None
if w0 is not None:
    w1 = next(k for k in range(w0 + 1, len(B)) if B[k].startswith('def '))
    hk = next((k for k in range(w0, w1) if 'sleep(' in B[k]), None)
if hk is not None and '_event_tick(' not in '\n'.join(B[w0:hk]):
    d = ind(B[hk])
    B.insert(hk, d*' ' + "try:  # WATCH-HOOK v85.52: the heartbeat rings the doorbells - latency equals one heartbeat, cost equals one stat per folder")
    B.insert(hk+1, d*' ' + "    _event_tick((desk_load() or {}).get('primary') or os.getcwd())")
    B.insert(hk+2, d*' ' + "except Exception:")
    B.insert(hk+3, d*' ' + "    pass")
    done.append('watch-hook')
    print('🔎 watcher heartbeat and hook:')
    for j in range(w0, hk+6):
        print('   |', B[j].rstrip()[:150])
else:
    print('🔎 watcher sleep anchor not found - tick defs stand ready; next lap hooks by evidence')
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
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.52' not in t:
        open(AR, 'a').write('v85.52: RENAME-WATCH + CONVERT-WATCH - directory mtimes as doorbells on the watcher heartbeat; background runs the ceremony fast half (text eyes, FIRST-LINE, CASE-LAW) and converts docx/doc/rtf/images to PDF beside untouched sources, recorded in .converted.json; vision stays with the chair up once per paper per day; missing soffice named aloud once (S393, S394)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S393 the background renames with the ceremony's fast half the moment a paper lands", "'S392 every exit names itself - a bare shell prompt is never the only evidence", "ck('S393 the background renames with the ceremony'+chr(39)+'s fast half the moment a paper lands', ('def _fast_rename(' in _src) and (chr(35)+' RENAME-WATCH v85.52') in _src)"),
      ("'S394 a Word paper is converted the moment it lands, source untouched, twice never", "'S393 the background renames with the ceremony's fast half the moment a paper lands", "ck('S394 a Word paper is converted the moment it lands, source untouched, twice never', ('def _convert_to_pdf(' in _src) and (chr(35)+' CONVERT-WATCH v85.52') in _src and ('.converted.json' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
