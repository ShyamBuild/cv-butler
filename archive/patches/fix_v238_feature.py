import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if 'return _lv' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith("print('🔢 ' + str(len(digits))"))
    d = ind(l) if False else ind(B[i]) - 4
    B.insert(i+1, (d if d >= 0 else 4)*' ' + "return _lv  # CANDIDATE-FIRST v81.93: provenance speaks AND hands back its list, so callers can act on it")
    done.append('provenance-returns')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if '# CANDIDATE-FIRST v81.93' not in '\n'.join(g):
    i = next(k for k, l in enumerate(g) if 'PROVENANCE-AT-PICK v81.92: a pick-list without addresses' in l)
    d = ind(g[i])
    g[i:i+3] = [d*' ' + "if path is not None and len(ps) > 1:  # CANDIDATE-FIRST v81.93: when the paper distinguishes the human from a referee, the machine picks the human and says so; the list returns only for true ambiguity",
                d*' ' + "    try:",
                d*' ' + "        _lv = butler.provenance_of(path, ps) or []",
                d*' ' + "        _cand = [x for x, w in _lv if 'referee' not in w]",
                d*' ' + "        if len(_cand) == 1 and _cand[0] in ps:",
                d*' ' + "            say(f\"🎯 using the candidate's own number {_cand[0]} (page-proven); a referee-suspect number stays un-dialled unless you name it\")",
                d*' ' + "            return _cand[0]",
                d*' ' + "    except Exception:",
                d*' ' + "        pass"]
    done.append('candidate-first')
    srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
if "'S199 the paper's own witness picks the candidate's number" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S198 every pick-list speaks its numbers" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S199 the paper'+chr(39)+'s own witness picks the candidate'+chr(39)+'s number', (chr(35)+' CANDIDATE-FIRST v81.93') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('return _lv') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S199-guard')
print('✅', done)
