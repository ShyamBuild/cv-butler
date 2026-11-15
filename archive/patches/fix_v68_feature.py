import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
F = open('briefing.py').read().split('\n')
if 'def do_summarize(' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_help('))
    F[i:i] = ['def _llm_prose(s):',
              '    try:',
              '        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:',
              "            names = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]",
              '        if not names: return None',
              '        payload = json.dumps({"model": names[0], "messages": [{"role": "user", "content": f"Rewrite these recruiter facts as exactly two client-facing sentences, plain text, no preamble: {s}"}], "stream": False}).encode()',
              '        req = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})',
              '        with urllib.request.urlopen(req, timeout=60) as r:',
              "            t = (json.loads(r.read().decode())['message']['content'] or '').strip()",
              '        return t if 20 < len(t) < 400 else None',
              '    except Exception:',
              '        return None',
              'def do_summarize(arg, root, say=print):',
              "    q = (arg or '').strip()",
              "    if not q: say('usage: summarize <candidate name>'); return",
              '    hits = _hits_for(q, root)',
              "    if not hits: say(f\"🤷 no CV matches '{q}'\"); return",
              '    hit = hits[0]',
              '    import fitrank, ledger, time as _tm',
              '    txt = fitrank._text(hit)',
              '    yrs, des, loc = fitrank._years(txt), fitrank._desig(txt), fitrank._loc(txt)',
              '    nt, ctc = fitrank._notice(txt), fitrank._ctc(txt)',
              "    cs = ledger._load(ledger.CASES).get(os.path.splitext(os.path.basename(hit))[0].lower(), {})",
              "    sts = cs.get('stages') or []",
              "    stage = sts[0]['stage'] if sts else 'untracked'",
              "    days = (int(_tm.time()) - sts[0]['at']) // 86400 if sts else 0",
              '    conv = {}',
              "    try: conv = json.load(open(os.path.join(BASE_DIR, 'conversations.json')))",
              '    except Exception: conv = {}',
              "    phs = cs.get('phones') or phones_of(hit) or ['']",
              "    din = re.sub(r'\\D', '', str(phs[0])) if phs else ''",
              "    e = conv.get(din) if din else None",
              "    li = next((m for m in reversed((e or {}).get('messages', [])) if m['dir'] == 'in'), None) if e else None",
              "    liq = (li['text'][:70] if li else None)",
              "    desig = ' / '.join(sorted(set(des))[:3]) or 'professional'",
              '    facts = []',
              "    if yrs: facts.append(f'{yrs}+ years')",
              "    if loc: facts.append(', '.join(loc[:2]))",
              "    if nt: facts.append(f'{nt}-day notice')",
              "    if ctc: facts.append(f'~{ctc}L')",
              "    line1 = f\"{_full_name(hit)} - {desig} ({', '.join(facts) or 'experience on file'})\"",
              "    line2 = f\"Currently {stage} ({days}d) · tier {cs.get('tier') or '?'} · last inbound: \" + (f'\"{liq}\"' if liq else 'none captured')",
              "    say('📝 client-ready:')",
              "    say(f'   {line1}.')",
              "    say(f'   {line2}.')",
              "    p = _llm_prose(line1 + '. ' + line2)",
              "    if p: say(f'   polished: {p}')",
              '']
    done.append('summarize-command')
for k, l in enumerate(F):
    if "'client','digest')" in l and "'summarize'" not in l:
        F[k] = l.replace("'digest')", "'digest','summarize')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'digest'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'summarize': do_summarize(arg, root, print)")
        done.append('cli-summarize'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('digest')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('summarize '): do_summarize(q[10:].strip(), root); continue")
        done.append('chat-summarize'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
print('stage briefing', done, flush=True)
B = open('butler.py').read().split('\n')
if "'S50 summarize routed" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S49 cadence queue accepts due" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S50 summarize routed', 'def do_summarize(' in _br and \"cmd == 'summarize'\" in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S50-guard')
print('✅', done)
