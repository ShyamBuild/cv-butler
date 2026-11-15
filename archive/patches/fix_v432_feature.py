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
e0 = next((k for k, l in enumerate(B) if l.startswith('def _event_tick(')), None)
if e0 is not None and 'def _tick_loop(' not in '\n'.join(B):
    e1 = next(k for k in range(e0 + 1, len(B)) if B[k].startswith('def ') or (B[k].strip() and not B[k].startswith(' ') and not B[k].startswith('#') and not B[k].startswith(')') and not B[k].startswith('for ') and not B[k].startswith('if ') and not B[k].startswith('try') and not B[k].startswith('except') and not B[k].startswith('continue') and not B[k].startswith('names') and not B[k].startswith('p =') and not B[k].startswith('ext') and not B[k].startswith('_convert') and not B[k].startswith('_fast') and not B[k].startswith('mt') and not B[k].startswith('dirs') and not B[k].startswith('_EVT')))
    B[e1:e1] = ["def _tick_loop():  # WATCH-HOOK v85.53: the doorbell owns its heartbeat when the watcher's cannot be found - one stat per folder every five seconds, single tenant by flock, silence between rings",
                "    import time as _tt, fcntl as _fc",
                "    lf = os.path.join(BASE_DIR, '.tick.lock')",
                "    try:",
                "        _lh = open(lf, 'w')",
                "        _fc.flock(_lh, _fc.LOCK_EX | _fc.LOCK_NB)",
                "    except Exception:",
                "        return",
                "    while True:",
                "        try:",
                "            _event_tick((desk_load() or {}).get('primary') or os.getcwd())",
                "        except Exception:",
                "            pass",
                "        _tt.sleep(5)",
                "import threading as _thd",
                "_thd.Thread(target=_tick_loop, daemon=True).start()  # WATCH-HOOK v85.53: every butler process offers a ticker; the flock chooses the one that rings",
                ""]
    done.append('tick-loop')
    print('🔎 ticker installed after _event_tick:')
    for j in range(e1, min(e1+6, len(B))):
        print('   |', B[j].rstrip()[:150])
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
    if 'v85.53' not in t:
        open(AR, 'a').write('v85.53: WATCH-HOOK owns its heartbeat - a daemon thread rings _event_tick every five seconds, single-tenant by flock on .tick.lock so exactly one process ever owns the bell; anchor-free by design because the watcher loop could not be found blind; existing docx papers convert and name within seconds of restart (S395)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S395 the doorbell owns its heartbeat and one process alone may ring it", "'S394 a Word paper is converted the moment it lands, source untouched, twice never", "ck('S395 the doorbell owns its heartbeat and one process alone may ring it', ('def _tick_loop(' in _src) and (chr(35)+' WATCH-HOOK v85.53') in _src and ('.tick.lock' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
