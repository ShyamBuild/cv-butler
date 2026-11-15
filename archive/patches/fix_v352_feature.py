import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
RD = os.path.join(os.getcwd(), 'README.md')
if not os.path.exists(RD):
    open(RD, 'w').write("# CV Butler v85.0\n*The co-pilot that remembers, confirms, and sends.*\n\nSee ARCHITECTURE.md for the nine domains, the seven doors, the skip tray (RETRAY-ONE), the composers and the contract; run ./install.sh on a fresh Mac, then chat, up, and the digits 1-7 with y/t/n at the cue.\n")
    done.append('readme')
IN = os.path.join(os.getcwd(), 'install.sh')
if not os.path.exists(IN):
    open(IN, 'w').write('#!/bin/bash\n# CV Butler v85.0 Installer\nset -e\necho "🤵 CV Butler v85.0 - installing on $(hostname)..."\npip3 install -r requirements.txt 2>/dev/null || pip3 install pyobjc-framework-Quartz\nmkdir -p drafts templates\necho "✅ stores seeded - run: chat"\n')
    os.chmod(IN, 0o755)
    done.append('install')
for FN in ('butler.py', 'briefing.py'):
    P = os.path.join(os.getcwd(), FN)
    L = open(P).read().split('\n')
    hits = [k for k, l in enumerate(L) if l.startswith('VERSION =')]
    if not hits:
        L.insert(0, "VERSION = '85.0'  # THE FREEZE v85.0: the standing price of every future change")
        done.append(FN.split('.')[0] + '-version-new')
    else:
        for j, k in enumerate(hits):
            L[k] = ("VERSION = '85.0'  # THE FREEZE v85.0: the standing price of every future change" if j == 0 else "VERSION = '85.0'  # THE FREEZE v85.0: harmonized - one truth wherever the book keeps one")
        done.append(FN.split('.')[0] + '-version-harmonized-x%d' % len(hits))
    src = '\n'.join(L)
    if src != open(P).read():
        ast.parse(src); open(P, 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S329 the freeze holds - v85.0 is the standing price of every future change", "'S328 the tray offers one skipped soul per empty seed, oldest first", "ck('S329 the freeze holds - v85.0 is the standing price of every future change', (chr(35)+' THE FREEZE v85.0') in _src and os.path.exists(os.path.join(BASE_DIR, 'README.md')) and os.path.exists(os.path.join(BASE_DIR, 'install.sh')))  # S329 repinned v85.0: a version is a fact about the source, so the guard reads the source, not a variable the book may reassign")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
