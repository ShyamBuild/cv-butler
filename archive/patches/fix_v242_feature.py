import ast, os, re as _re
done = []
def ind(l): return len(l) - len(l.lstrip())
BARE = '(?<!footer )div\\[contenteditable="true"\\]'
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if not any(x.strip().startswith('return _lv') for x in B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith("print('🔢 ' + str(len(digits))"))
    B.insert(i+1, '    ' + "return _lv  # CANDIDATE-FIRST v81.93: provenance speaks AND hands back its list, so callers can act on it")
    done.append('provenance-returns')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if '# CANDIDATE-FIRST v81.93' not in srcg:
    i = next(k for k, l in enumerate(g) if 'PROVENANCE-AT-PICK v81.92: a pick-list without addresses' in l)
    d = ind(g[i])
    g[i:i+3] = [d*' ' + "if path is not None and len(ps) > 1:  # PROVENANCE-AT-PICK v81.92 # CANDIDATE-FIRST v81.93: when the paper distinguishes the human from a referee, the machine picks the human and says so; the list returns only for true ambiguity (markers separated by space-hash, never by plus: each witness keeps its own hash)",
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
W = os.path.join(os.getcwd(), 'wa.py')
srcw = open(W).read()
if _re.search(BARE, srcw):
    srcw = _re.sub(BARE, 'footer div[contenteditable="true"]', srcw)
    done.append('composer-scope-bare-only')
if '# NO-FIELD-EXIT v81.94' not in srcw:
    w = srcw.split('\n')
    k = next(i for i, l in enumerate(w) if 'there is no message field to paste into' in l)
    d = ind(w[k])
    w[k+1:k+1] = [d*' ' + "_r = input('   [x] discard this round · [q] close the window · [Enter] keep it open, then teach or re-pick: ').strip().lower()  # NO-FIELD-EXIT v81.94: a dead number ends the round with ONE menu; the paste-advice never speaks after a no-field confession",
                  d*' ' + "if _r == 'q':",
                  (d+4)*' ' + "try: page.close()",
                  (d+4)*' ' + "except Exception: pass",
                  d*' ' + "return False"]
    done.append('no-field-exit')
    srcw = '\n'.join(w)
if srcw != open(W).read():
    ast.parse(srcw); open(W, 'w').write(srcw)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S199 the paper's own witness picks the candidate's number", "'S198 every pick-list speaks its numbers", "ck('S199 the paper'+chr(39)+'s own witness picks the candidate'+chr(39)+'s number', (chr(35)+' CANDIDATE-FIRST v81.93') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and any(x.strip().startswith('return _lv') for x in _src.split(chr(10))))"),
      ("'S200 a dead number ends the round with one menu", "'S199 the paper's own witness picks the candidate's number", "ck('S200 a dead number ends the round with one menu', (chr(35)+' NO-FIELD-EXIT v81.94') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S201 the field detector sees the composer, not the search box", "'S200 a dead number ends the round with one menu", "ck('S201 the field detector sees the composer, not the search box', ((_w := open(os.path.join(BASE_DIR, 'wa.py')).read()) and re.search('(?<!footer )div' + chr(92) + '[contenteditable=' + chr(34) + 'true' + chr(34) + chr(92) + ']', _w) is None and ('footer div[contenteditable=' + chr(34) + 'true' + chr(34) + ']') in _w))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S197 the WhatsApp door is asked within the first beats", "'S195 identity speaks once, not twice")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('DIAG return_lv:', any(x.strip().startswith('return _lv') for x in open('butler.py')))
print('DIAG cand_first:', '# CANDIDATE-FIRST v81.93' in open('briefing.py').read())
print('DIAG bare_selector_left:', _re.search(BARE, open('wa.py').read()) is not None)
print('✅', done)
