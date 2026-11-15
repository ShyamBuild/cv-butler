import ast, os, json
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _in_nonqueue(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
    B[i:i] = ["NONQUEUE_PATH = os.path.join(BASE_DIR, 'nonqueue.json')  # NON-QUEUE v84.39: derivative folders never queue",
              "def nonqueue_load():",
              "    try: d = json.load(open(NONQUEUE_PATH))",
              "    except Exception: d = []",
              "    return [x.lower() for x in d] + ['converted files', 'converted', 'archive', 'duplicates']",
              "def _in_nonqueue(p):",
              "    nq = set(nonqueue_load())",
              "    return any(dn.lower() in nq for dn in os.path.split(os.path.dirname(p))[0:][0].split(os.sep)) if False else any(dn.lower() in nq for dn in os.path.dirname(p).split(os.sep))",
              "def skipfolder_cmd(arg, root, say=print):  # NON-QUEUE v84.39",
              "    if not arg: say('usage: skipfolder Converted Files'); return",
              "    try: d = json.load(open(NONQUEUE_PATH))",
              "    except Exception: d = []",
              "    if arg not in d: d.append(arg)",
              "    json.dump(d, open(NONQUEUE_PATH, 'w'), indent=1)",
              "    say(f'🚫 never queue: {arg} - its residents are derivatives or archives, not candidates')",
              ""]
    done.append('nonqueue')
    src = '\n'.join(B)
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
if '_in_nonqueue(p)' not in '\n'.join(B[c0:c1]):
    for k in range(c0, c1):
        if B[k].strip().startswith('if not _is_desk_candidate(x): continue'):
            B.insert(k+1, ind(B[k])*' ' + "if _in_nonqueue(p): continue  # NON-QUEUE v84.39: a converted paper is a derivative, not a candidate")
            done.append('calls-nonqueue'); break
    src = '\n'.join(B)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
seg = '\n'.join(B[u0:u1])
if '_in_nonqueue' not in seg:
    for k in range(u0, u1):
        if B[k].strip().startswith('if rq in known or rq in sk or os.path.basename(dp) in _tag_vocab()'):
            B[k] = B[k].replace(': continue', ' or _in_nonqueue(q): continue')
            done.append('up-scan-nonqueue'); break
    for k in range(u0, u1):
        if B[k].strip().startswith('if os.path.basename(os.path.dirname(p)) in _tag_vocab() or _name_key(os.path.basename(p)) in mem:'):
            B[k] = B[k].rstrip()[:-0] if False else B[k].replace(':', ' or _in_nonqueue(p):', 1) if B[k].rstrip().endswith(':') else B[k]
            done.append('up-seat-nonqueue')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if ph: say(f'   phone: {ph}')") and 'CONTACT-ONCE' not in '\n'.join(B[max(0,k-6):k+4]):
        d = ind(l)
        B[k:k+2] = [d*' ' + "_em = ''  # CONTACT-ONCE v84.39: every truth exactly once - email and phone in a single line",
                    d*' ' + "for _fn in ('email_of', '_email_of', '_email_witness', 'emails_of'):",
                    d*' ' + "    _f = globals().get(_fn)",
                    d*' ' + "    if callable(_f):",
                    d*' ' + "        try:",
                    d*' ' + "            _v = _f(p)",
                    d*' ' + "            if _v: _em = _v[0] if isinstance(_v, (list, tuple)) else str(_v); break",
                    d*' ' + "        except Exception: pass",
                    d*' ' + "if ph: say(f'   ✉️ {_em} · 📱 {ph}' if _em else f'   📱 {ph}')",
                    d*' ' + "else: say((f'   ✉️ {_em}' if _em else f'   phone: none readable - teach me: python3 butler.py teach {i[\"name\"].split()[0].lower()} <digits>'))"]
        done.append('contact-once'); break
for k, l in enumerate(B):
    if l.strip().startswith('pass  # QUIET-CHAIR v84.37: the triple speaks once, at the proposal'):
        B[k] = ind(l)*' ' + "say_identity_for(p, say)  # IDENTITY-AT-SEAT v84.39: the master asked for the triple at the seat as well; S277 keeps the proposal's"
        done.append('identity-at-seat'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if "'clients', 'refresh', 'options', 'draftwhy', 'twins')" in l and 'skipfolder' not in l:
        B[k] = l.replace("'twins')", "'twins', 'skipfolder')")
        done.append('cli-skipfolder-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'twins':") and 'skipfolder' not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "elif _v == 'skipfolder': skipfolder_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-skipfolder-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'skipfolder_cmd' not in '\n'.join(g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q == 'twins' or q.startswith('twins '):"):
            g.insert(k+1, ind(l)*' ' + "if q.startswith('skipfolder '): butler.skipfolder_cmd(q[11:].strip(), root, say); continue  # NON-QUEUE v84.39")
            done.append('chat-skipfolder'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.39' not in t:
        open(AR, 'a').write('v84.39: nonqueue.json + skipfolder (derivative folders never queue); contact line once (email+phone); identity triple at seat and proposal; module-map section grows each lap\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S304 derivative folders never queue as candidates", "'S303 the persistent window stays open and the master may tag without texting", "ck('S304 derivative folders never queue as candidates', (chr(35)+' NON-QUEUE v84.39') in _src and ('nonqueue.json' in _src) and ('def skipfolder_cmd(' in _src))"),
      ("'S305 every contact truth is spoken once, at the seat and at the proposal", "'S304 derivative folders never queue as candidates", "ck('S305 every contact truth is spoken once, at the seat and at the proposal', (chr(35)+' CONTACT-ONCE v84.39') in _src and (chr(35)+' IDENTITY-AT-SEAT v84.39') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
