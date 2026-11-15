import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
F = open('briefing.py').read().split('\n')
if 'def _pos_client_for(' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def _pos_for('))
    F[i:i] = ["CLIENTS_FILE = os.path.join(BASE_DIR, 'clients.json')",
              "def _clients():",
              "    try: return json.load(open(CLIENTS_FILE))",
              "    except Exception: return {}",
              "def _jd_text_for(pos_path):",
              "    try:",
              "        import fitrank",
              "        sp = fitrank._store(pos_path)",
              "        if os.path.exists(sp):",
              "            t = json.load(open(sp)).get('jdtext')",
              "            if t: return t",
              "    except Exception: pass",
              "    return ''",
              "def _auto_client_full(short, pos_path):",
              "    head = (_jd_text_for(pos_path) or '')[:600]",
              "    low = short.lower()",
              "    for m in re.finditer(r'[A-Z][A-Za-z0-9&.\\-]{2,24}(?:\\s+[A-Z][A-Za-z0-9&.\\-]{2,24}){0,3}', head):",
              "        run = m.group(0)",
              "        if low in run.lower():",
              "            w = run.split()",
              "            if len(w[0]) > 3: w[0] = w[0].title()",
              "            return ' '.join(w)",
              "    return ''",
              "def _client_full(short_dirname, pos_path):",
              "    short = re.sub(r'^\\d+[\\s_-]*', '', short_dirname).strip()",
              "    m = _clients(); key = re.sub(r'[^a-z]', '', short.lower())",
              "    if key in m: return m[key]",
              "    full = _auto_client_full(short, pos_path)",
              "    if full:",
              "        m[key] = full",
              "        try: json.dump(m, open(CLIENTS_FILE, 'w'), indent=2)",
              "        except Exception: pass",
              "        return full",
              "    return short.title()",
              "def _pos_client_for(hit, f=None):",
              "    for base in ([os.path.dirname(os.path.abspath(hit))] if hit else []) + ([f['path']] if f and f.get('path') else []):",
              "        comp = _company_root(base)",
              "        rel = os.path.relpath(base, comp)",
              "        parts = [] if rel == '.' else rel.split(os.sep)",
              "        if len(parts) >= 2:",
              "            pos_path = os.path.join(comp, parts[0], parts[1])",
              "            return clean_pos(parts[1]), _client_full(parts[0], pos_path)",
              "        if len(parts) == 1:",
              "            pos_path = os.path.join(comp, parts[0])",
              "            return clean_pos(parts[0]), _client_full(parts[0], pos_path)",
              "    return 'the discussed role', 'our client'",
              "def do_clientname(arg, root, say=print):",
              "    if '=' not in arg: say('usage: clientname <short> = <Full Client Name>'); return",
              "    q, full = [x.strip() for x in arg.split('=', 1)]",
              "    m = _clients(); m[re.sub(r'[^a-z]', '', q.lower())] = full",
              "    json.dump(m, open(CLIENTS_FILE, 'w'), indent=2)",
              "    say(f'🏢 client alias saved: {q} -> {full}')",
              ""]
    done.append('pos-client-resolver')
idxs = [k for k, l in enumerate(F) if l.strip().startswith("pos = f['display'] if f else clean_pos(")]
for k in reversed(idxs):
    F[k] = ind(F[k])*' ' + "pos, cli = _pos_client_for(None, f)"
if idxs: done.append(f'phone-first-truth-x{len(idxs)}')
for k, l in enumerate(F):
    if l.strip().startswith("pos = f['display'] if f else clean_pos(os.path.basename(os.path.dirname(os.path.dirname(hit))))"):
        F[k] = ind(l)*' ' + "pos, cli = _pos_client_for(hit, f)"
        if k+1 < len(F) and l and F[k+1].strip().startswith("cli = f['client'] if f else re.sub"):
            del F[k+1]
        done.append('send-name-truth'); break
for k, l in enumerate(F):
    if "format(name=name, position=f['display'], company=f['client'])" in l:
        F[k] = l.replace("position=f['display'], company=f['client']", "position=_pos_client_for(hit, f)[0], company=_pos_client_for(hit, f)[1]")
        done.append('missed-name-truth')
for k, l in enumerate(F):
    if l.strip().startswith("text = tpl.format(name=name, position=f['display'], company=f['client'])"):
        F[k] = ind(l)*' ' + "text = tpl.format(name=name, position=_pos_client_for(hit, f)[0], company=_pos_client_for(hit, f)[1])"
        done.append('reject-truth'); break
for k, l in enumerate(F):
    if l.strip().startswith("client = re.sub(r'^\\d+[\\s_-]*', '', os.path.basename(os.path.dirname(os.path.dirname(folder))))"):
        F[k] = ind(l)*' ' + "client = _client_full(os.path.basename(os.path.dirname(os.path.dirname(folder))), os.path.dirname(os.path.dirname(folder)))"
        done.append('text-client-full'); break
for k, l in enumerate(F):
    if "'digest','summarize')" in l and "'clientname'" not in l:
        F[k] = l.replace("'summarize')", "'summarize','clientname')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'summarize'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'clientname': do_clientname(arg, root, print)")
        done.append('cli-clientname'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('summarize ')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('clientname '): do_clientname(q[11:].strip(), root); continue")
        done.append('chat-clientname'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
print('stage briefing', done, flush=True)
B = open('butler.py').read().split('\n')
if "'S51 drafts use position/client truth" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S50 summarize routed" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S51 drafts use position/client truth', 'def _pos_client_for(' in _br and 'position=_pos_client_for(hit, f)[0]' in _br)")
    B.insert(i+2, d*' ' + "ck('S52 client alias command routed', 'def do_clientname(' in _br and \"cmd == 'clientname'\" in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S51-S52-guards')
print('✅', done)
