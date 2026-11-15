import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
i0 = next((k for k, l in enumerate(B) if '# NAME-BY-PHONE v79' in l), None)
if i0 is not None and '# LEARN-BACK v80.1' not in '\n'.join(B):
    i1 = next(k for k in range(i0, i0+16) if B[k].strip() == 'if _nb: name = _nb')
    d = ind(B[i0])
    B[i0:i1+1] = [d*' ' + "_nbm = _names_by_phone()  # NAME-BY-PHONE v79",
                  d*' ' + "_st0 = os.path.splitext(base)[0]",
                  d*' ' + "_phs = []",
                  d*' ' + "if name and (_nbm or _st0 != name):",
                  d*' ' + "    try:",
                  d*' ' + "        import fitrank as _fr",
                  d*' ' + "        _phs = phones_of(_fr._text(p)) or []",
                  d*' ' + "    except Exception:",
                  d*' ' + "        _phs = []",
                  d*' ' + "if _nbm:",
                  d*' ' + "    for _d in _phs:",
                  d*' ' + "        if _d in _nbm: name = _nbm[_d]; break",
                  d*' ' + "if name and _phs and _st0 != name and len(_st0.split()) >= 2 and all(w[:1].isupper() for w in _st0.split() if w):  # LEARN-BACK v80.1",
                  d*' ' + "    for _d in _phs: _nbm[_d] = _st0",
                  d*' ' + "    try:",
                  d*' ' + "        import json as _j2",
                  d*' ' + "        _j2.dump(_nbm, open(os.path.join(BASE_DIR, 'names_by_phone.json'), 'w'), indent=1)",
                  d*' ' + "    except Exception: pass",
                  d*' ' + "    name = _st0"]
    done.append('name-block-v80.1')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
F = open('briefing.py').read().split('\n')
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('name '): do_name("):
        F[k] = ind(l)*' ' + "if q.lower().startswith('name '): print('📖 chat is read-only - run: briefing.py name <phone-or-word> <Name>'); continue  # CHAT-READONLY v80"
        done.append('chat-readonly-restored'); break
for k, l in enumerate(F):
    if l.strip() == 'hits = _hits_for((arg or '').strip(), root)':
        F[k] = ind(l)*' ' + "hits = _hits_for((arg or '').strip().strip('\"\\''), root)"
        done.append('renwhy-quote-strip'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S103 chat stays read-only" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S102 name command learns and renames on demand" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S103 chat stays read-only', (chr(35)+' CHAT-READONLY') in _br and 'do_name(q[' not in _br)")
    B.insert(i+2, d*' ' + "ck('S104 butler learns manual renames', (chr(35)+' LEARN-BACK v80.1') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S103-S104-guards')
print('✅', done)
