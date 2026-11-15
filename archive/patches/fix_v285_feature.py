import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'MENU v84.10a' not in src:
    for k, l in enumerate(B):
        if l.strip().startswith("if len(sys.argv) > 1 and sys.argv[1] in ('pending'"):
            d = ind(l)
            B[k:k] = [d*' ' + "if len(sys.argv) > 1 and sys.argv[1] in ('?', 'help'):  # MENU v84.10a: the clerk offers his menu when the master forgets",
                      (d+4)*' ' + "print('🤵 The 4-Word Life:')",
                      (d+4)*' ' + "print('  📆 briefing     · what is due today')",
                      (d+4)*' ' + "print('  🏷️ tag <n> <s>  · update a human (e.g. tag lalan feedback pending)')",
                      (d+4)*' ' + "print('  🧹 tidy         · carry misplaced papers home')",
                      (d+4)*' ' + "print('  👀 dash         · see the desk\\'s census')",
                      (d+4)*' ' + "print('  (Right-click a folder in Finder -> Butler Here to start)')",
                      (d+4)*' ' + "sys.exit(0)"]
            done.append('cli-menu'); break
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'MENU v84.10a' not in srcg:
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('pending'): do_pending("):
            d = ind(l)
            g[k:k] = [d*' ' + "if q.strip() in ('?', 'help', 'menu'):  # MENU v84.10a",
                      (d+4)*' ' + "say('🤵 The 4-Word Life:')",
                      (d+4)*' ' + "say('  📆 briefing     · what is due today')",
                      (d+4)*' ' + "say('  🏷️ tag <n> <s>  · update a human (e.g. tag lalan feedback pending)')",
                      (d+4)*' ' + "say('  🧹 tidy         · carry misplaced papers home')",
                      (d+4)*' ' + "say('  👀 dash         · see the desk\\'s census')",
                      (d+4)*' ' + "continue"]
            done.append('chat-menu'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S250 the clerk offers his menu when the master forgets", "'S249 a paper away from its stage's folder is named by audit and moved only by tidy's keystroke", "ck('S250 the clerk offers his menu when the master forgets', (chr(35)+' MENU v84.10a') in _src and (chr(35)+' MENU v84.10a') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
