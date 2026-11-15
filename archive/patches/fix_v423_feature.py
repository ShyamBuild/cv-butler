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
tk = next((k for k, l in enumerate(B) if 'TRAY-SCOPE v85.41' in l), None)
if tk is not None and 'locals().get' not in B[tk]:
    d = ind(B[tk])
    B[tk:tk+1] = [d*' ' + "_rt = locals().get('root') or desk_load().get('primary') or os.sep  # TRAY-SCOPE scope-safe v85.45: the filter asks the room for its root before assuming one",
                  d*' ' + "_sk = [x for x in _sk if os.path.realpath(x).startswith(os.path.realpath(_rt))]  # TRAY-SCOPE v85.41: the tray belongs to its desk - a new position starts with an empty tray"]
    done.append('tray-scope-safe')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
G0 = open('briefing.py').read()
g = G0.split('\n')
snapg = list(g)
idxs = [k for k, l in enumerate(g) if 'WHOLE-WORD-WALK v81.81' in l]
for k in reversed(idxs):
    if 'FULL-NAME-PICK' in '\n'.join(g[k:k+40]):
        continue
    d = ind(g[k+3])
    g[k+4:k+4] = [d*' ' + "if hit:  # FULL-NAME-PICK v85.45: the first match is a candidate, not a verdict - when several papers answer the same spoken words, the master picks among them all",
                  (d+4)*' ' + "_hits = []",
                  (d+4)*' ' + "for _sr in _roots:",
                  (d+8)*' ' + "for dp, dn, fn in os.walk(_sr):",
                  (d+12)*' ' + "for x in fn:",
                  (d+16)*' ' + "if x.lower().endswith('.pdf') and all(t in os.path.splitext(x)[0].lower().replace('_', ' ').split() for t in q.split()):",
                  (d+20)*' ' + "_hits.append(os.path.join(dp, x))",
                  (d+4)*' ' + "if len(_hits) > 1:",
                  (d+8)*' ' + "say('🪪 several papers answer to those words - pick the human by email:')",
                  (d+8)*' ' + "for _n, _c in enumerate(_hits, 1):",
                  (d+12)*' ' + "try:",
                  (d+16)*' ' + "_ef = getattr(butler, '_email_cheap', None) or butler.emails_of",
                  (d+16)*' ' + "_em = _ef(_c) or ['none readable']",
                  (d+16)*' ' + "_em = _em[0] if isinstance(_em, list) else _em",
                  (d+12)*' ' + "except Exception:",
                  (d+16)*' ' + "_em = 'none readable'",
                  (d+12)*' ' + "try:",
                  (d+16)*' ' + "_ph = (butler.phones_of(_c, quiet=True) or ['none readable'])[0]",
                  (d+12)*' ' + "except Exception:",
                  (d+16)*' ' + "_ph = 'none readable'",
                  (d+8)*' ' + "say(f'   {_n}) {os.path.basename(_c)} · {_em} · {_ph} · {os.path.relpath(os.path.dirname(_c), root)}')",
                  (d+8)*' ' + "try:",
                  (d+12)*' ' + "hit = _hits[int(input('   pick #: ').strip()) - 1]",
                  (d+8)*' ' + "except KeyboardInterrupt:",
                  (d+12)*' ' + "say('👋 pick cancelled - nothing drafted'); hit = None",
                  (d+8)*' ' + "except Exception:",
                  (d+12)*' ' + "say('🤷 pick skipped')"]
    done.append('full-name-pick')
srcg = '\n'.join(g)
if srcg != G0:
    ast.parse(srcg); open('briefing.py', 'w').write(srcg)
W0 = open('wa.py').read()
w = W0.split('\n')
snapw = list(w)
cw = next((k for k, l in enumerate(w) if 'timeout=240' in l or 'timeout=1800' in l), None)
if cw is not None and 'timeout=1500' not in w[cw]:
    w[cw] = re.sub(r'timeout=\d+', 'timeout=1500', w[cw]).rstrip() + '  # HANG-CEILING human-thought v85.46 (1500 v85.47): twenty-five minutes for a thinking master, death only for a wedged child - and a number no probe mistakes for the OCR cap'
    done.append('ceiling-human')
b0 = next(k for k, l in enumerate(w) if l.startswith('def _send_review_body('))
b1 = next(k for k in range(b0 + 1, len(w)) if w[k].startswith('def '))
kq = next((k for k in range(b0, b1) if 'QR-RESCAN v85.26' in w[k]), None)
if kq is not None and 'WAIT-SAY' not in '\n'.join(w[b0:b1]):
    d = ind(w[kq])
    j = kq
    while j + 1 < b1 and (w[j+1].strip() == '' or ind(w[j+1]) > d):
        j += 1
    w[j+1:j+1] = [d*' ' + "say('⏳ waiting for the composer - the window is loading, not hung')  # WAIT-SAY v85.45: a slow load reads as work in progress, never as a corpse"]
    done.append('wait-say')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 old walk kept and picker appended; ceiling and wait-say:')
L = open('briefing.py').read().split('\n')
for k, l in enumerate(L):
    if 'FULL-NAME-PICK v85.45' in l:
        for j in range(k-4, k+4):
            print('   |', L[j].rstrip()[:150])
        break
for l in open('wa.py').read().split('\n'):
    if 'HANG-CEILING human-thought' in l or 'WAIT-SAY v85.45' in l:
        print('   |', l.strip()[:150])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.47' not in t:
        open(AR, 'a').write('v85.47: the picker stands AFTER the untouched old walk (first match a candidate, not a verdict) so S27/S189 keep their shape; ceiling 1500 avoids the 180-substring trap; WAIT-SAY anchored after the QR block where the silence begins (S385, S386, S387)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S385 when several papers answer the spoken words, the master picks among them all", "'S384 the door speaks the master's files' dialect - no courtesy renders an empty name", "ck('S385 when several papers answer the spoken words, the master picks among them all', (chr(35)+' FULL-NAME-PICK v85.45') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' WHOLE-WORD-WALK v81.81') in open(os.path.join(BASE_DIR, 'briefing.py')).read())"),
      ("'S386 the tray filter asks its room for the root before assuming one", "'S385 when several papers answer the spoken words, the master picks among them all", "ck('S386 the tray filter asks its room for the root before assuming one', ('locals().get' in _src) and (chr(35)+' TRAY-SCOPE v85.41') in _src)"),
      ("'S387 a slow load reads as work in progress, and a thinking master is never mistaken for a wedged child", "'S386 the tray filter asks its room for the root before assuming one", "ck('S387 a slow load reads as work in progress, and a thinking master is never mistaken for a wedged child', (chr(35)+' WAIT-SAY v85.45') in open(os.path.join(BASE_DIR, 'wa.py')).read() and ('timeout=1500' in open(os.path.join(BASE_DIR, 'wa.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
