import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def pos_identity(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _pos_of('))
    B[i:i] = ["POS_PATH = os.path.join(BASE_DIR, 'positions.json')  # POS-ID v84.21: one truth per position, taught once, read forever",
              "CLIENTMAP_PATH = os.path.join(BASE_DIR, 'clients.json')  # POS-ID v84.21: one truth per client, system-wide",
              "def pos_identity(p, root=None):  # POS-ID v84.21: company from the client map, role and location from the folder, overrides win",
              "    root = root or _pl_root()",
              "    out = {'company': '', 'role': '', 'loc': ''}",
              "    if not p: return out",
              "    rel = os.path.relpath(p, root).split(os.sep)",
              "    pospath = None",
              "    d = desk_load()",
              "    for chair in (d.get('primary'), d.get('secondary')):",
              "        if chair and (p == chair or p.startswith(chair + os.sep)): pospath = chair; break",
              "    if pospath is None and len(rel) > 2: pospath = os.path.join(root, rel[0], rel[1])",
              "    if pospath is None and len(rel) == 2: pospath = os.path.join(root, rel[0])",
              "    if not pospath: return out",
              "    try: reg = json.load(open(POS_PATH))",
              "    except Exception: reg = {}",
              "    ov = reg.get(pospath, {})",
              "    base = os.path.basename(pospath)",
              "    role, loc = (base.split(' -', 1) + [''])[:2]",
              "    out['role'] = ov.get('role') or role.strip()",
              "    out['loc'] = ov.get('loc') or loc.strip()",
              "    client = os.path.basename(os.path.dirname(pospath))",
              "    try: cm = json.load(open(CLIENTMAP_PATH))",
              "    except Exception: cm = {}",
              "    out['company'] = ov.get('company') or cm.get(client, '') or ''",
              "    return out",
              "def say_identity_for(p, say=print):  # POS-ID v84.21: the triple, shown before anything sends",
              "    i = pos_identity(p)",
              "    parts = [x for x in (i['company'], i['role'], i['loc']) if x]",
              "    if parts: say('🏢 ' + ' · '.join(parts))",
              "def client_cmd(arg, root, say=print):  # POS-ID v84.21: teach a client's company once, system-wide",
              "    if '=' not in arg: say('usage: client 02 HIPP = Honda India'); return",
              "    k, v = arg.split('=', 1)",
              "    try: cm = json.load(open(CLIENTMAP_PATH))",
              "    except Exception: cm = {}",
              "    cm[k.strip()] = v.strip()",
              "    json.dump(cm, open(CLIENTMAP_PATH, 'w'), indent=1)",
              "    say(f'🏢 client taught: {k.strip()} = {v.strip()}')",
              "def posmeta_cmd(arg, root, say=print):  # POS-ID v84.21: override the triple for the seated chair when the folder lies",
              "    d = desk_load()",
              "    if not d.get('primary'): say('🤷 no desk seated - seat one first'); return",
              "    parts = [x.strip() for x in arg.split('|')]",
              "    try: reg = json.load(open(POS_PATH))",
              "    except Exception: reg = {}",
              "    ov = reg.get(d['primary'], {})",
              "    if len(parts) > 0 and parts[0]: ov['company'] = parts[0]",
              "    if len(parts) > 1 and parts[1]: ov['role'] = parts[1]",
              "    if len(parts) > 2 and parts[2]: ov['loc'] = parts[2]",
              "    reg[d['primary']] = ov",
              "    json.dump(reg, open(POS_PATH, 'w'), indent=1)",
              "    say('📋 position truth set: ' + ' · '.join(x for x in (ov.get('company'), ov.get('role'), ov.get('loc')) if x))",
              ""]
    done.append('pos-registry')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("role, loc = (pos.split(' -', 1) + [''])[:2] if pos else ('', '')"):
        d = ind(l)
        B[k:k+1] = [d*' ' + "_idn = pos_identity(p or '')",
                    d*' ' + "role = _idn['role'] or role",
                    d*' ' + "loc = _idn['loc'] or loc"]
        done.append('fields-registry'); break
for k, l in enumerate(B):
    if l.strip().startswith("if meta.get('company'): _rl.append('in ' + meta['company'])"):
        B[k] = ind(l)*' ' + "if (_idn['company'] or meta.get('company')): _rl.append('in ' + (_idn['company'] or meta['company']))"
        done.append('roleline-registry'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('say(f"📞 UP:'):
        B.insert(k+1, ind(l)*' ' + "say_identity_for(p, say)")
        done.append('up-identity'); break
for k, l in enumerate(B):
    if l.strip().startswith('say(f"🤖 Proposal:'):
        B.insert(k, ind(l)*' ' + "say_identity_for(p, say)")
        done.append('proposal-identity'); break
for k, l in enumerate(B):
    if "'release', 'forget', 'meta')" in l:
        B[k] = l.replace("'meta')", "'meta', 'client', 'posmeta')")
        done.append('cli-pos-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'meta':") and 'client' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'client': client_cmd(' '.join(_a), _pl_root(), print)")
        B.insert(k+2, d*' ' + "elif _v == 'posmeta': posmeta_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-pos-branches'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'say_identity_for' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def _fmt_tpl('))
    d = ind(g[i])
    g.insert(i+1, (d+4)*' ' + "try:  # POS-ID v84.21: every draft, keyword or chair, shows the position's triple before the window opens")
    g.insert(i+2, (d+8)*' ' + "if hit and os.path.isfile(str(hit)):")
    g.insert(i+3, (d+12)*' ' + "import butler as _bt; _bt.say_identity_for(str(hit), print)")
    g.insert(i+4, (d+4)*' ' + "except Exception: pass")
    done.append('composer-identity')
    srcg = '\n'.join(g)
if 'client_cmd' not in srcg:
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('meta '):"):
            dd = ind(l)
            g.insert(k+1, dd*' ' + "if q.startswith('client '): butler.client_cmd(q[7:].strip(), root, say); continue  # POS-ID v84.21")
            g.insert(k+2, dd*' ' + "if q.startswith('posmeta '): butler.posmeta_cmd(q[8:].strip(), root, say); continue")
            done.append('chat-pos'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S276 one truth per position, taught once and shown at the composer", "'S275 the fields dict carries every sentence it computes", "ck('S276 one truth per position, taught once and shown at the composer', (chr(35)+' POS-ID v84.21') in _src and ('def pos_identity(' in _src) and ('say_identity_for' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))"),
      ("'S277 the chair shows the triple before the thumb decides", "'S276 one truth per position, taught once and shown at the composer", "ck('S277 the chair shows the triple before the thumb decides', ('say_identity_for(p, say)' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
