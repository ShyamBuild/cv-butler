import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
W0 = open('wa.py').read()
M0 = set(markers(B0.split('\n'))) | set(markers(W0.split('\n')))
B = B0.split('\n')
snap = list(B)
n = 0
for k, l in enumerate(B):
    if "menu_key('   y = 🏷️ tag + 📦 move + 📱 WhatsApp draft" in l:
        B[k] = l.replace("menu_key('   y = 🏷️", "menu_key('y = 🏷️"); n += 1
    if "menu_key('   y = 🏷️ tag + 📦 move · t = same" in l:
        B[k] = l.replace("menu_key('   y = 🏷️", "menu_key('y = 🏷️"); n += 1
    if "menu_key('· proposal waiting - one key: ')" in l:
        B[k] = l.replace("menu_key('· proposal waiting - one key: ')", "menu_key('proposal waiting - one key: ')  # FLUSH-CUE v85.14: prompts stand at column zero; no intentional indent may be mistaken for a ghost"); n += 1
if n: done.append('flush-cue-x%d' % n)
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
w = W0.split('\n')
snapw = list(w)
for k, l in enumerate(w):
    if l.strip().startswith("_pm = '   [s] I clicked send myself"):
        d = ind(l)
        w[k] = d*' ' + "_pm = '[s] I clicked send myself · [x] discard & clear · [q] leave in field & close · [Enter] keep waiting: '  # FLUSH-CUE v85.14"
        done.append('wa-flush'); break
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open('wa.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.14' not in t:
        open(AR, 'a').write('v85.14: FLUSH-CUE - every interactive prompt stands at column zero; intentional indents retired so no written space can be mistaken for the ghost space the master sees; cat -A diagnostic requested to name the newline thief in bytes\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S347 every interactive prompt stands at column zero", "'S346 the seat check delegates the deed to the developed renamer", "ck('S347 every interactive prompt stands at column zero', (chr(35)+' FLUSH-CUE v85.14') in _src and ((chr(39) + '   y = ' + chr(127991) + chr(65039)) not in _src) and ((chr(39) + '   [s] I clicked') not in open(os.path.join(BASE_DIR, 'wa.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
