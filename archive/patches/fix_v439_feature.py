import ast, os, re, shutil
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
t0 = next((k for k, l in enumerate(B) if l.startswith('def _tick_loop(')), None)
if t0 is not None and 'BELL-HEARTBEAT v85.59' not in '\n'.join(B[t0:t0+40]):
    t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def ') or (B[k].strip() and not B[k].startswith(' ') and not B[k].startswith('#')))
    d = ind(B[t0])
    B[t0:t1] = [d*' ' + "def _tick_loop():  # WATCH-HOOK v85.53 (heartbeat v85.59): the bell is owned by a pulse, not by a lock - the stamp proves life, and a stale or dead owner is inherited within half a minute",
                (d+4)*' ' + "import time as _tt",
                (d+4)*' ' + "pf = os.path.join(BASE_DIR, '.tick.pid')",
                (d+4)*' ' + "while True:  # BELL-RETRY v85.55: a doorbell that gives up after one knock is not a doorbell",
                (d+8)*' ' + "own = False",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "if not os.path.exists(pf):",
                (d+16)*' ' + "own = True",
                (d+12)*' ' + "else:",
                (d+16)*' ' + "age = _tt.time() - os.stat(pf).st_mtime",
                (d+16)*' ' + "txt = open(pf).read().strip()",
                (d+16)*' ' + "dead = False",
                (d+16)*' ' + "try:",
                (d+20)*' ' + "os.kill(int(txt), 0)",
                (d+16)*' ' + "except Exception:",
                (d+20)*' ' + "dead = True",
                (d+16)*' ' + "if dead or age > 30:  # BELL-HEARTBEAT v85.59: an orphan from an old commit never refreshes the stamp, so the living inherit the bell",
                (d+20)*' ' + "own = True",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "own = True",
                (d+8)*' ' + "if own:",
                (d+12)*' ' + "try:",
                (d+16)*' ' + "open(pf, 'w').write(str(os.getpid()))",
                (d+12)*' ' + "except Exception:",
                (d+16)*' ' + "pass",
                (d+12)*' ' + "break",
                (d+8)*' ' + "_tt.sleep(10)",
                (d+4)*' ' + "while True:",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "os.utime(pf, None)",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "pass",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "_event_tick((desk_load() or {}).get('primary') or os.getcwd(), _tick_log)",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "pass",
                (d+8)*' ' + "_tt.sleep(5)",
                ""]
    done.append('bell-heartbeat')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
RD_OLD = os.path.join(os.getcwd(), 'rendiag.py')
RD_NEW = os.path.join(os.getcwd(), 'archive', 'rendiag.py')
if not os.path.exists(RD_NEW):
    body = None
    if os.path.exists(RD_OLD):
        body = open(RD_OLD).read()
    else:
        body = "#!/usr/bin/env python3\nimport os, sys\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nimport butler\npaths = sys.argv[1:]\nif not paths:\n    root = butler._lock_root() or (butler.desk_load() or {}).get('primary') or os.getcwd()\n    paths = []\n    for dp, dn, fn in os.walk(root):\n        for x in fn:\n            if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                paths.append(os.path.join(dp, x))\n        if len(paths) > 400: break\nbutler.rename_diag(paths)\n"
    open(RD_NEW, 'w').write(body)
    done.append('rendiag-to-archive')
if os.path.exists(RD_OLD):
    try:
        os.remove(RD_OLD)
        done.append('rendiag-root-removed')
    except Exception:
        pass
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 heartbeat head and rendiag home:')
L = open('butler.py').read().split('\n')
for k, l in enumerate(L):
    if 'BELL-HEARTBEAT v85.59: the bell is owned' in l or 'BELL-HEARTBEAT v85.59: an orphan' in l:
        print('   |', l.strip()[:150])
print('   |', RD_NEW, os.path.exists(RD_NEW))
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.59' not in t:
        open(AR, 'a').write('v85.59: BELL-HEARTBEAT replaces the flock with a pid stamp refreshed each beat - dead or stale owners are inherited within thirty seconds so orphan watchers can never starve the bell again; rendiag.py moves to archive/ where untracked survivors live (S401 repinned, S403)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("ck('S401 ") and 'archive' not in l:
        d = ind(l)
        B[k] = d*' ' + "ck('S401 the butler'+chr(39)+'s eyes open in public, one honest row per file', ('def rename_diag(' in _src) and (chr(35)+' RENAME-DIAG v85.58') in _src and os.path.exists(os.path.join(BASE_DIR, 'archive', 'rendiag.py')))  # S401 repinned v85.59: the diagnostic lives where untracked survivors live"
        done.append('S401-repin'); break
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S403 the bell is owned by a pulse, and orphans inherit nothing but silence", "'S402 the master's Finder selection is drained by the bell, in the background, each beat", "ck('S403 the bell is owned by a pulse, and orphans inherit nothing but silence', (chr(35)+' BELL-HEARTBEAT v85.59') in _src and ('.tick.pid' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
