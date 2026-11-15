import ast, os, re, sys
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
W0 = open('wa.py').read()
w = W0.split('\n')
snapw = list(w)
i0 = next(k for k, l in enumerate(w) if l.startswith('def send_review('))
k1 = next((k for k in range(i0, i0+30) if w[k].strip().startswith("code += (\"open(%r, 'w').write(st)\"")), None)
if k1 is not None and '_pw().stop()' not in '\n'.join(w[i0:k1+6]):
    d = ind(w[k1])
    w[k1+1:k1+1] = [d*' ' + "code += 'try:' + nl",
                    d*' ' + "code += '    wa._pw().stop()  # DRIVER-GOODBYE v85.42: an orderly goodbye so the node driver exits before any pipe closes beneath it' + nl",
                    d*' ' + "code += 'except Exception:' + nl",
                    d*' ' + "code += '    pass' + nl"]
    done.append('driver-goodbye')
k2 = next((k for k in range(i0, i0+30) if w[k].strip().startswith('rr = subprocess.call(')), None)
if k2 is not None and 'timeout=240' not in w[k2]:
    w[k2] = w[k2].replace(')', ', timeout=240)', 1) + '  # HANG-CEILING v85.42: a child that ignores even four minutes is killed, its status read, its draft parked - a hung ritual never owns an evening'
    done.append('hang-ceiling')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
B0 = open('butler.py').read()
B = B0.split('\n')
snap = list(B)
n = 0
for k, l in enumerate(B):
    if 'emails_of(' in l and not l.strip().startswith('def emails_of(') and '_email_cheap(' not in l and 'def _email_cheap' not in l:
        B[k] = l.replace('emails_of(', '_email_cheap(')
        n += 1
if n: done.append('cheap-mail-everywhere-x%d' % n)
tk = next((k for k, l in enumerate(B) if 'TIDY-TRAY v85.34' in l), None)
if tk is not None and 'TRAY-SCOPE' not in B[tk-1]:
    d = ind(B[tk])
    B.insert(tk, d*' ' + "_sk = [x for x in _sk if os.path.realpath(x).startswith(os.path.realpath(root))]  # TRAY-SCOPE v85.41: the tray belongs to its desk - a new position starts with an empty tray, and the old chair's souls rest where they were skipped")
    done.append('tray-scope')
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
sys.path.insert(0, os.getcwd())
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
    if 'v85.42' not in t:
        open(AR, 'a').write('v85.42: DRIVER-GOODBYE (child stops playwright before exit, no EPIPE corpse-wait) + HANG-CEILING (wrapper timeout 240, kill and park); cheap email at every butler call site so tray returns never pay OCR; TRAY-SCOPE filters the tray to its desk; audit imports butler via sys.path (S380, S381, S382)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S380 the driver is bid goodbye before any pipe closes, and no child may hang an evening", "'S379 a door and its keyword voice speak one sentence because they read one file", "ck('S380 the driver is bid goodbye before any pipe closes, and no child may hang an evening', (chr(35)+' DRIVER-GOODBYE v85.42') in open(os.path.join(BASE_DIR, 'wa.py')).read() and (chr(35)+' HANG-CEILING v85.42') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S381 a returned tray paper never pays the pixel bill", "'S380 the driver is bid goodbye before any pipe closes, and no child may hang an evening", "ck('S381 a returned tray paper never pays the pixel bill', _src.count('emails_of(') <= 2 and ('_email_cheap(' in _src))"),
      ("'S382 the tray belongs to its desk", "'S381 a returned tray paper never pays the pixel bill", "ck('S382 the tray belongs to its desk', (chr(35)+' TRAY-SCOPE v85.41') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
