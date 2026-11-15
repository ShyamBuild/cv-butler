import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
W = open('wa.py').read().split('\n')
if 'left in field & window closed' not in '\n'.join(W):
    i = next(k for k, l in enumerate(W) if l.strip() == "say('✅ sent (you clicked in WhatsApp)')")
    W[i:i] = [ind(W[i])*' ' + "if c == 'q':",
              ind(W[i])*' ' + "    say('📝 left in field & window closed - NOT counted as sent')",
              ind(W[i])*' ' + "    return False"]
    done.append('q-not-sent')
open('wa.py', 'w').write('\n'.join(W))
F = open('briefing.py').read().split('\n')
for k, l in enumerate(F):
    if l.strip() == 'low = (pos or \'\').lower(); locs = []':
        F[k:k+1] = [ind(l)*' ' + "low = (pos or '').lower().replace('|', ' ')  # SPLIT-HARD v56",
                    ind(l)*' ' + "low = re.sub(r'\\blocation\\b', ' ', low)",
                    ind(l)*' ' + "locs = []"]
        done.append('split-hard'); break
i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_send('))
j = next(k for k in range(i, i+60) if F[k].strip() == 'nm = _full_name(hit)')
F.insert(j+1, ind(F[j])*' ' + "say(f'   🗣 voice: {_tpl_name(tpl_words)}')")
done.append('send-voice-label')
for k, l in enumerate(F):
    if l.strip() == 'if not st: return None':
        F[k:k+1] = [ind(l)*' ' + 'if not st:',
                    ind(l)*' ' + '    try:',
                    ind(l)*' ' + "        conv = json.load(open(os.path.join(BASE_DIR, 'conversations.json')))",
                    ind(l)*' ' + "        for p in (cs.get('phones') or []):",
                    ind(l)*' ' + "            e = conv.get(re.sub(r'\\D', '', str(p)))",
                    ind(l)*' ' + '            if not e: continue',
                    ind(l)*' ' + "            outs = [m['text'].lower() for m in e.get('messages', []) if m['dir'] == 'out']",
                    ind(l)*' ' + "            if outs and any('not relevant' in t for t in outs[-3:]): return ['rejected']",
                    ind(l)*' ' + '    except Exception:',
                    ind(l)*' ' + '        pass',
                    ind(l)*' ' + '    return None']
        done.append('follow-conversation-fallback'); break
if 'def do_tpltest(' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_help('))
    F[i:i] = ["def do_tpltest(arg, root, say=print):",
              "    hits = _hits_for((arg or '').strip(), root)",
              "    if not hits: say(f'🤷 no CV matches {arg!r}'); return",
              "    hit = hits[0]",
              "    pos, cli = _pos_client_for(hit, None)",
              "    title, loc = _split_pos(pos)",
              "    at = cli + (f', {loc}' if loc else '')",
              "    say(f'🧪 path: {os.path.relpath(hit, root)}')",
              "    say(f'   position raw : {pos}')",
              "    say(f'   client       : {cli}')",
              "    say(f'   title        : {title}')",
              "    say(f'   location     : {loc or \"(none found)\"}')",
              "    say(f'   where        : {at}')",
              "    say('   rendered (awaiting voice):')",
              "    for ln in _fmt_tpl(_tpl_for(['awaiting']), hit, None, _full_name(hit)).split('\\n'):",
              "        say(f'     {ln}')",
              ""]
    done.append('tpltest-command')
for k, l in enumerate(F):
    if "'clientname','follow')" in l and "'tpltest'" not in l:
        F[k] = l.replace("'follow')", "'follow','tpltest')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'follow'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'tpltest': do_tpltest(arg, root, print)")
        done.append('cli-tpltest'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('follow ')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('tpltest '): do_tpltest(q[8:].strip(), root); continue")
        done.append('chat-tpltest'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
print('stage briefing', done, flush=True)
B = open('butler.py').read().split('\n')
if "'S61 q never counts as sent" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S60 stage-aware follow" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S61 q never counts as sent', 'left in field & window closed' in _wa)")
    B.insert(i+2, d*' ' + "ck('S62 tpltest + split hardening', 'def do_tpltest(' in _br and (chr(35) + ' SPLIT-HARD') in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S61-S62-guards')
print('✅', done)
