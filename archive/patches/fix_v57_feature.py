import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if 'cadence.process(B' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if 'import ledger; ledger.tick(B)' in l)
    B.insert(i+1, ind(B[i])*' ' + 'import cadence; cadence.process(B, hsay)')
    done.append('heartbeat-cadence')
if "'S37 cadence armed" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S36 StageLog not self-recursive" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S37 cadence armed + processed', 'cadence.arm(' in _br and 'cadence.process(B' in _src)")
    B.insert(i+2, d*' ' + "ck('S38 outbox/due/ack routed', \"cmd == 'outbox'\" in _br)")
    B.insert(i+3, d*' ' + "_led = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''")
    B.insert(i+4, d*' ' + "ck('S39 ledger hygiene: no utility positions + phone precedence', 'untitled' in _led and 'phone_fixes.json' in _led)")
    done.append('S37-S39-guards')
new = '\n'.join(B); ast.parse(new); open('butler.py', 'w').write(new)
print('stage1 butler', done, flush=True)
F = open('briefing.py').read().split('\n')
idxs = [k for k, l in enumerate(F) if 'fitrank.mark_called(hit)' in l or 'fitrank.mark_called(os.path.join(folder, x))' in l]
for k in reversed(idxs):
    expr = 'os.path.join(folder, x)' if 'folder, x' in F[k] else 'hit'
    F.insert(k+1, ind(F[k])*' ' + 'try: import cadence; cadence.arm(phone, os.path.splitext(os.path.basename(' + expr + '))[0])')
    F.insert(k+2, ind(F[k])*' ' + 'except Exception: pass')
done.append(f'cadence-arm-x{len(idxs)}')
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
print('stage2 briefing', done, flush=True)
G = open('ledger.py').read().split('\n')
for k, l in enumerate(G):
    if l.strip() == "if not os.path.isdir(pp) or pname.startswith('.'): continue":
        G.insert(k+1, ind(l)*' ' + 'pl = pname.lower()')
        G.insert(k+2, ind(l)*' ' + "if pl.startswith(('jd', 'fw')) or pl.startswith('untitled') or pl in ('converted doc files', 'converted files', 'duplicates', 'previous versions', 'nvites', 'ta_output'): continue")
        done.append('ledger-positions-filter'); break
i = next(k for k, l in enumerate(G) if 'for k, v in _load(os.path.join(BASE, \'phones.json\')).items():' in l)
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
