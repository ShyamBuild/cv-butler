import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
W = open('wa.py').read().split('\n')
if 'def _arm(' not in '\n'.join(W):
    i = next(k for k, l in enumerate(W) if l.strip().startswith('def send_review('))
    W[i:i] = ['def _arm(phone, text):',
              '    try:',
              '        import cadence',
              '        m = re.match(r"\\s*Hi\\s+([A-Za-z][A-Za-z .\\-]+?),", text or "")',
              '        cadence.arm(phone, (m.group(1).strip() if m else None))',
              '    except Exception:',
              '        pass',
              '']
    done.append('wa-arm-helper')
for k, l in enumerate(W):
    if l.strip() == "say('✅ sent (you clicked in WhatsApp)')":
        W.insert(k+1, ind(l)*' ' + '_arm(digits, text)'); done.append('wa-arm-manual')
idxs = [k for k, l in enumerate(W) if l.strip() == 'return bool(sent)']
for k in reversed(idxs):
    W.insert(k, ind(W[k])*' ' + 'if sent: _arm(digits, text)')
if idxs: done.append(f'wa-arm-autosend-x{len(idxs)}')
new = '\n'.join(W); ast.parse(new); open('wa.py', 'w').write(new)
print('stage1 wa', done, flush=True)
C = open('cadence.py').read()
old = "if i['kind'] == 'ack_check' and not i['done'] and k and k in (i.get('name') or '').lower():"
if old in C:
    C = C.replace(old, "if i['kind'] == 'ack_check' and not i['done'] and k and (k in (i.get('name') or '').lower() or (k.isdigit() and k in re.sub(r'\\D', '', str(i.get('phone') or '')))):")
    C = C.replace('import os, json, time, datetime', 'import os, re, json, time, datetime', 1)
    open('cadence.py', 'w').write(C); done.append('cadence-ack-phone')
B = open('butler.py').read().split('\n')
if 'cadence.process(B' not in '\n'.join(B):
    i = max(k for k, l in enumerate(B) if 'import ledger; ledger.tick(B)' in l)
    B.insert(i+1, ind(B[i])*' ' + 'import cadence; cadence.process(B, hsay)')
    done.append('heartbeat-cadence')
if "'S37 cadence armed" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S36 StageLog not self-recursive" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S37 cadence armed + processed', 'cadence.arm(' in _wa and ('cadence.' + 'process(B') in _src)")
    B.insert(i+2, d*' ' + "ck('S38 outbox/due/ack routed', \"cmd == 'outbox'\" in _br)")
    B.insert(i+3, d*' ' + "_led = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''")
    B.insert(i+4, d*' ' + "ck('S39 ledger hygiene: no utility positions + phone precedence', 'untitled' in _led and 'phone_fixes.json' in _led)")
    B.insert(i+5, d*' ' + "ck('S40 learned beats extraction at learn-back', '_lb = _phones_by_basename(path)' in _br)")
    done.append('S37-S40-guards')
new = '\n'.join(B); ast.parse(new); open('butler.py', 'w').write(new)
print('stage2 butler', done, flush=True)
F = open('briefing.py').read().split('\n')
if '_lb = _phones_by_basename(path)' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith("store[os.path.abspath(path)] = {'k': k, 'phones': ph}"))
    d0 = ind(F[i])
    F.insert(i, d0*' ' + '_lb = _phones_by_basename(path)')
    F.insert(i+1, d0*' ' + 'if _lb: ph = _lb')
    done.append('poison-guard-learn-back')
for k, l in enumerate(F):
    if "'note','interview','offer')" in l and "'due'" not in l:
        F[k] = l.replace("'offer')", "'offer','due','outbox','ack')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'offer'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'due': import cadence; cadence.show_due(print)")
        F.insert(k+2, ind(l)*' ' + "elif cmd == 'outbox': import cadence; cadence.show_outbox(print)")
        F.insert(k+3, ind(l)*' ' + "elif cmd == 'ack': import cadence; cadence.ack(arg, print)")
        done.append('cli-cadence-routes'); break
for k, l in enumerate(F):
    if "startswith('positions')" in l and 'cadence' not in l:
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('due'): import cadence; cadence.show_due(); continue")
        F.insert(k+2, ind(l)*' ' + "if q.lower().startswith('outbox'): import cadence; cadence.show_outbox(); continue")
        F.insert(k+3, ind(l)*' ' + "if q.lower().startswith('ack '): import cadence; cadence.ack(q[4:].strip()); continue")
        done.append('chat-cadence-routes'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
print('stage3 briefing', done, flush=True)
G = open('ledger.py').read().split('\n')
if 'pl = pname.lower()' not in '\n'.join(G):
    for k, l in enumerate(G):
        if l.strip() == "if not os.path.isdir(pp) or pname.startswith('.'): continue":
            G.insert(k+1, ind(l)*' ' + 'pl = pname.lower()')
            G.insert(k+2, ind(l)*' ' + "if pl.startswith(('jd', 'fw')) or pl.startswith('untitled') or pl in ('converted doc files', 'converted files', 'duplicates', 'previous versions', 'nvites', 'ta_output'): continue")
            done.append('ledger-positions-filter'); break
if 'byb = {}' not in '\n'.join(G):
    i = next(k for k, l in enumerate(G) if "for k, v in _load(os.path.join(BASE, 'phones.json')).items():" in l)
    j = i
    while j < len(G) and 'except Exception: pass' not in G[j]: j += 1
    G[i:j+1] = ["        pj = _load(os.path.join(BASE, 'phones.json'))",
                "        byb = {}",
                "        for k, v in pj.items():",
                "            ph = v.get('phones') or []",
                "            if not ph: continue",
                "            byb.setdefault(os.path.basename(k).lower(), []).append((os.path.exists(k), ph))",
                "        for nm, opts in byb.items():",
                "            cd = _case(case_d, os.path.splitext(nm)[0])",
                "            cd['phones'] = next((ph for ex, ph in opts if ex), None) or opts[0][1]",
                "        for kk, vv in _load(os.path.join(BASE, 'phone_fixes.json')).items():",
                "            tg = next((k2 for k2 in case_d if re.sub(r'[^a-z]', '', k2) == kk), None)",
                "            if tg and isinstance(vv, list) and vv: case_d[tg]['phones'] = vv",
                "    except Exception: pass"]
    done.append('ledger-phone-precedence')
new = '\n'.join(G); ast.parse(new); open('ledger.py', 'w').write(new)
print('✅', done)
