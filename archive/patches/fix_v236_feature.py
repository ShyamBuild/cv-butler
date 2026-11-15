import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
def idx(B, cond, what):
    hit = [k for k, l in enumerate(B) if cond(l)]
    if not hit: raise SystemExit('anchor missing: ' + what)
    return hit[0]
B = open('butler.py').read().split('\n')
if 'def _provenance_lines(' not in '\n'.join(B):
    i = idx(B, lambda l: l.startswith('def phones_of('), 'def phones_of( at module level')
    B[i:i] = ["def _provenance_lines(ap, ph):  # PROVENANCE v81.90 (refactored v81.92): one source of truth for where each number lives in the paper (module level: briefing calls it too)",
              "    out = []",
              "    try:",
              "        with pdfplumber.open(ap) as _pf:",
              "            for _pi, _pg in enumerate(_pf.pages, 1):",
              "                _pt = _pg.extract_text() or ''",
              "                _ref = 'references' in _pt.lower()",
              "                for _dd in phones_in_text(_pt):",
              "                    if _dd in ph and _dd not in [x[0] for x in out]:",
              "                        out.append((_dd, f'page {_pi}' + (' , after a References heading - likely a referee, not the candidate' if _ref else ' , header/body - likely the candidate')))",
              "    except Exception:",
              "        pass",
              "    return out",
              "",
              "def provenance_of(p, digits):  # PROVENANCE-AT-PICK v81.92: the pick-list speaks each number's address, cached or fresh",
              "    _lv = _provenance_lines(os.path.abspath(p), digits)",
              "    if _lv:",
              "        print('🔢 ' + str(len(digits)) + ' numbers in ' + os.path.basename(p) + ': ' + ' · '.join(f'{i}) {dd} ({w})' for i, (dd, w) in enumerate(_lv, 1)), flush=True)",
              ""]
    done.append('provenance-fn')
    i = idx(B, lambda l: l.strip() == 'if ph and not quiet and len(ph) > 1:', 'the old provenance block head')
    j = next(k for k in range(i, len(B)) if '# PROVENANCE v81.90' in B[k])
    d = ind(B[i])
    B[i:j+2] = [d*' ' + "if ph and not quiet and len(ph) > 1: _provenance_print = provenance_of(ap, ph)  # PROVENANCE v81.90: every number carries its page and its section"]
    done.append('provenance-refactor')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'path=None' not in '\n'.join(g):
    i = idx(g, lambda l: l.strip() == 'def _pick_phone(ps, say=print, ask=None):', 'def _pick_phone signature')
    d = ind(g[i])
    g[i] = d*' ' + "def _pick_phone(ps, say=print, ask=None, path=None):"
    g[i+1:i+1] = [d*' ' + "    if path is not None and len(ps) > 1:  # PROVENANCE-AT-PICK v81.92: a pick-list without addresses is a guess with numbering",
                  d*' ' + "        try: butler.provenance_of(path, ps)",
                  d*' ' + "        except Exception: pass"]
    done.append('pick-path-kwarg')
    n = 0
    for k, l in enumerate(g):
        if l.strip() == 'phone = _pick_phone(_phones_by_basename(hit) or phones_of(hit), say)':
            g[k] = ind(l)*' ' + "phone = _pick_phone(_phones_by_basename(hit) or phones_of(hit), say, path=hit)"
            n += 1
    if n: done.append(f'call-sites-{n}')
    srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
W = os.path.join(os.getcwd(), 'wa.py')
w = open(W).read().split('\n')
if '# EARLY-DOOR v81.92' not in '\n'.join(w):
    k = idx(w, lambda l: 'Correct it with: fixphone' in l, 'the fixphone advice line in wa.py')
    d = ind(w[k])
    w[k-2:k+4] = [d*' ' + "try:  # EARLY-DOOR v81.92: ask WhatsApp within the first beats, not after the placement wait - poll four seconds for the modal or the field, whichever speaks first",
                  d*' ' + "    for _i in range(8):",
                  d*' ' + "        _html = page.content() or ''",
                  d*' ' + "        if \"isn't on WhatsApp\" in _html:",
                  d*' ' + "            say('⚠️ WhatsApp says this number isn\\'t on WhatsApp - nothing drafted; teach or re-pick a number that is registered, or close the window whenever you like')",
                  d*' ' + "            return False",
                  d*' ' + "        try:",
                  d*' ' + "            if page.locator('div[contenteditable=\"true\"]').count() > 0: break",
                  d*' ' + "        except Exception: break",
                  d*' ' + "        page.wait_for_timeout(500)",
                  d*' ' + "except Exception:",
                  d*' ' + "    pass"]
    done.append('early-door')
    srcw = '\n'.join(w); ast.parse(srcw); open(W, 'w').write(srcw)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S197 the WhatsApp door is asked within the first beats", "'S196 no paste advice when WhatsApp says no field", "ck('S197 the WhatsApp door is asked within the first beats', (chr(35)+' EARLY-DOOR v81.92') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S198 every pick-list speaks its numbers' addresses", "'S197 the WhatsApp door is asked within the first beats", "ck('S198 every pick-list speaks its numbers'+chr(39)+' addresses', (chr(35)+' PROVENANCE-AT-PICK v81.92') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and _src.count('def provenance_'+'of(') == 1 and _src.find('def provenance_'+'of(') < _src.find('def phones_'+'of('))  # needles split: a count-guard must not count its own needle")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S195 identity speaks once, not twice")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
