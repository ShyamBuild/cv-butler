import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
G = open('ledger.py').read().split('\n')
if 'LEDGER-PRUNE' not in '\n'.join(G):
    i = next(k for k, l in enumerate(G) if l.strip().startswith('_save(POS, pos_d); _save(CASES, case_d)'))
    d = ind(G[i])
    G[i:i] = [d*' ' + '# LEDGER-PRUNE v43.1',
              d*' ' + 'for _kk in list(pos_d):',
              d*' ' + '    _bl = os.path.basename(_kk).lower()',
              d*' ' + "    if not os.path.isdir(_kk) or _bl.startswith(('jd', 'fw')) or _bl.startswith('untitled') or _bl in ('converted doc files', 'converted files', 'duplicates', 'previous versions', 'nvites', 'ta_output'):",
              d*' ' + '        del pos_d[_kk]']
    done.append('ledger-prune')
if 'pos_pipe' not in '\n'.join(G):
    i = next(k for k, l in enumerate(G) if "say(f'📈 pipeline-weighted expected:" in l)
    d = ind(G[i])
    G[i:i] = [d*' ' + 'pos_pipe = 0.0',
              d*' ' + 'for _pp, _e in _load(POS).items():',
              d*' ' + "    if _e.get('status') != 'open': continue",
              d*' ' + '    _c = _ctc_for(_pp)',
              d*' ' + "    if _c: pos_pipe += sum(_e.get('pipeline', {}).values()) * 0.15 * incentive_rupees(_c)",
              d*' ' + 'pipe = max(pipe, pos_pipe)']
    done.append('money-position-pipeline')
if 'source candidates for' not in '\n'.join(G):
    i = next(k for k, l in enumerate(G) if 'no high-value pushes right now' in l)
    d = ind(G[i])
    G[i:i] = [d*' ' + 'for _pp, _e in _load(POS).items():',
              d*' ' + "    if _e.get('status') == 'open' and _e.get('idle_days', 0) >= 14 and sum(_e.get('pipeline', {}).values()) == 0:",
              d*' ' + "        acts.append((50, f\"source candidates for {_e['client']} / {_e['title']} - open {_e.get('idle_days')}d with an empty pipeline\"))"]
    done.append('push-sourcing-actions')
new = '\n'.join(G); ast.parse(new); open('ledger.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S44 ledger prunes stale positions" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S43 incentive formula constant" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "_led3 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''")
    B.insert(i+2, d*' ' + "ck('S44 ledger prunes stale positions', (chr(35) + ' LEDGER-PRUNE') in _led3)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S44-guard')
print('✅', done)
