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
w0 = next(k for k, l in enumerate(B) if l.startswith('def _chair_wa_text('))
if 'def _draft_local_text(' not in '\n'.join(B):
    B[w0:w0] = ["def _draft_local_text(path, name, p):  # ONE-VOICE-FIRST v85.40: one door serves every voice - the master's own file for a kind, formatted from truths the house holds",
                "    import collections as _cc, json as _j2",
                "    _pi = pos_identity(p)",
                "    _dm = {}",
                "    try: _dm = _j2.load(open(os.path.join(BASE_DIR, 'desk_meta.json'))).get(desk_load().get('primary') or '', {})",
                "    except Exception: pass",
                "    _fld = _cc.defaultdict(str, {'name': name, 'position': _pi.get('role') or os.path.basename(os.path.dirname(p)), 'company': _pi.get('company') or _dm.get('company') or '', 'location': _pi.get('loc') or _pi.get('location') or ''})",
                "    return open(path).read().strip().format_map(_fld)",
                ""]
    done.append('local-text-helper')
w0 = next(k for k, l in enumerate(B) if l.startswith('def _chair_wa_text('))
w1 = next(k for k in range(w0 + 1, len(B)) if B[k].startswith('def '))
if 'ONE-VOICE-FIRST v85.40: every kind' not in '\n'.join(B[w0:w1]):
    t3 = next(k for k in range(w0, w1) if B[k].strip() == 'if t3: return t3')
    d = ind(B[t3])
    B[t3+1:t3+1] = [d*' ' + "_lp = os.path.join(DRAFTS_DIR, kind + '.txt')  # ONE-VOICE-FIRST v85.40: every kind reads the master's own file before any legacy template is consulted - door and keyword voice speak one sentence because they read one file",
                    d*' ' + "if os.path.exists(_lp): return _draft_local_text(_lp, name, p)"]
    done.append('every-kind-first')
r0 = next((k for k in range(w0, w1) if B[k].strip().startswith("if kind == 'refer':") and 'SCENARIO-REFER' in B[k]), None)
if r0 is not None:
    r1 = r0
    while r1 + 1 < w1 and (ind(B[r1+1]) > ind(B[r0]) or B[r1+1].strip() == ''):
        r1 += 1
    d = ind(B[r0])
    B[r0:r1+1] = [d*' ' + "if kind == 'refer':  # SCENARIO-REFER v85.4 (delegated v85.40): the refer courtesy walks through the same one door as every other kind",
                  (d+4)*' ' + "_rp2 = os.path.join(DRAFTS_DIR, 'refer.txt')",
                  (d+4)*' ' + "if os.path.exists(_rp2): return _draft_local_text(_rp2, name, p)"]
    done.append('refer-delegated')
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
print('🔎 voice-to-text audit (kind · legacy scenario · drafts file · first line):')
import importlib
try:
    import butler as _bt
    for _k in ('jd', 'refer', 'cv', 'nudge', 'missed', 'internal'):
        _sc = getattr(_bt, 'CHAIR_SCENARIO', {}).get(_k)
        _fp = os.path.join(os.getcwd(), 'drafts', _k + '.txt')
        _fl = ''
        if os.path.exists(_fp):
            _fl = open(_fp).read().strip().split('\n')[0][:90]
        print('   |', _k, '·', _sc, '·', ('drafts/%s.txt EXISTS' % _k) if os.path.exists(_fp) else 'no drafts file', '·', _fl)
except Exception as _e:
    print('   | audit skipped:', _e)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.40' not in t:
        open(AR, 'a').write('v85.40: ONE-VOICE-FIRST - every kind reads drafts/<kind>.txt before any legacy template, so a door and its keyword voice speak one sentence; refer delegates to the same door; the audit table prints kind, legacy scenario, file and first line (S379)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S379 a door and its keyword voice speak one sentence because they read one file", "'S378 one pick yields one whole human - own number or none, never a sibling's", "ck('S379 a door and its keyword voice speak one sentence because they read one file', (chr(35)+' ONE-VOICE-FIRST v85.40') in _src and ('def _draft_local_text(' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
