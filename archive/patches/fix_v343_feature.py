import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
snap = list(B)
for k, l in enumerate(B):
    if 'y = do + WhatsApp draft · t = do only · n = cancel' in l and 'PLAIN-CUE' not in l:
        B[k] = l.replace('y = do + WhatsApp draft · t = do only · n = cancel', 'y = tag + move + WhatsApp draft · t = tag + move, no WhatsApp · n = cancel').rstrip() + '  # PLAIN-CUE v84.50: the cue names the deeds in the master\'s words - tag, move, text'
        done.append('plain-cue-outcome'); break
for k, l in enumerate(B):
    if 't = yes, no draft' in l and 'PLAIN-CUE' not in l:
        B[k] = l.replace('y = yes · t = yes, no draft · n = cancel', 'y = tag + move · t = tag + move, no WhatsApp · n = cancel').rstrip() + ('' if 'PLAIN-CUE' in l else '  # PLAIN-CUE v84.50')
        done.append('plain-cue-tagvoice'); break
if parse_ok := True:
    pass
try:
    ast.parse('\n'.join(B))
    open('butler.py', 'w').write('\n'.join(B))
except Exception:
    B = snap; done.append('revert:plain-cue')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.50' not in t:
        open(AR, 'a').write('v84.50: PLAIN-CUE - cue lines name the deeds in the master\'s words (tag + move + WhatsApp draft / tag + move, no WhatsApp / cancel) in chair and tag-voice; every negative guard probe is built from concatenated parts so no witness carries the crime in its own body\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S321 the cue line names the deeds in the master's words", "'S320 no question may listen in silence - the cue line waits visibly and Ctrl+C cancels", "ck('S321 the cue line names the deeds in the master'+chr(39)+'s words', (chr(35)+' PLAIN-CUE v84.50') in _src and ('tag + move + WhatsApp draft' in _src) and (('t = do ' + 'only') not in _src) and (('t = yes, no ' + 'draft') not in _src))  # S321 repinned v84.50: negative probes are built from parts - a witness may not carry the crime in its own body")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
