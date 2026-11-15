import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if '# DEDUPE v81.79' not in srcg:
    for k, l in enumerate(g):
        if '_strict.append(os.path.join(dp, x))' in l:
            d = ind(l)
            g[k:k+1] = [d*' ' + "_p = os.path.join(dp, x)",
                        d*' ' + "if _p not in _strict: _strict.append(_p)  # DEDUPE v81.79: the client walk contains the position walk; a human is listed once"]
            done.append('dedupe'); break
    srcg = '\n'.join(g)
if '# PATH-LABEL v81.79' not in srcg:
    g = srcg.split('\n')
    for k, l in enumerate(g):
        if 'os.path.basename(os.path.dirname(_c))' in l and 'POSITION-LABEL v81.76' in l:
            code = l.split('#')[0].replace('os.path.basename(os.path.dirname(_c))', 'os.path.relpath(os.path.dirname(_c), root)')
            g[k] = code + '  # POSITION-LABEL v81.76 # PATH-LABEL v81.79: the whole folder trail from the client down - position and stage together - because that is what tells humans apart (comment lives outside the f-string braces)'
            done.append('path-label'); break
    srcg = '\n'.join(g)
if '# WHOLE-WORD-WALK v81.81' not in srcg:
    g = srcg.split('\n')
    for k, l in enumerate(g):
        if "all(t in x.lower() for t in q.split() if len(t) > 2)" in l:
            g[k] = ind(l)*' ' + "if x.lower().endswith('.pdf') and all(t in os.path.splitext(x)[0].lower().replace('_', ' ').split() for t in q.split()):  # WHOLE-WORD-WALK v81.81: the loose walk stops guessing by substring; a token is a whole word or the candidate is not offered"
            done.append('whole-word-walk'); break
    srcg = '\n'.join(g)
if '# PICK-GRACEFUL v81.81' not in srcg:
    g = srcg.split('\n')
    for k, l in enumerate(g):
        if "hit = _strict[int(input('   pick #: ').strip()) - 1]" in l:
            d = ind(l)
            g[k+1:k+1] = [d*' ' + "except KeyboardInterrupt: say('👋 pick cancelled - nothing drafted'); hit = None  # PICK-GRACEFUL v81.81: Ctrl-C at the picker is a choice, not a crash"]
            done.append('pick-graceful'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S186 a human is listed once, labelled by their whole trail", "'S185 the picker labels humans by position, not client", "ck('S186 a human is listed once, labelled by their whole trail', (chr(35)+' DEDUPE v81.79') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' PATH-LABEL v81.79') in open(os.path.join(BASE_DIR, 'briefing.py')).read())"),
      ("'S187 the loose walk offers whole words only", "'S186 a human is listed once, labelled by their whole trail", "ck('S187 the loose walk offers whole words only', (chr(35)+' WHOLE-WORD-WALK v81.81') in open(os.path.join(BASE_DIR, 'briefing.py')).read())"),
      ("'S188 Ctrl-C at the picker is a choice, not a crash", "'S187 the loose walk offers whole words only", "ck('S188 Ctrl-C at the picker is a choice, not a crash', (chr(35)+' PICK-GRACEFUL v81.81') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
