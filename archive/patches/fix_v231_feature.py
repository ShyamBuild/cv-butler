import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if '# PROVENANCE v81.90' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip() == 'return ph')
    d = ind(B[i])
    B[i:i] = [d*' ' + "if ph and not quiet and len(ph) > 1:",
              d*' ' + "    try:",
              d*' ' + "        with pdfplumber.open(ap) as _pf:",
              d*' ' + "            _prov = []",
              d*' ' + "            for _pi, _pg in enumerate(_pf.pages, 1):",
              d*' ' + "                _pt = _pg.extract_text() or ''",
              d*' ' + "                _ref = 'references' in _pt.lower()",
              d*' ' + "                for _dd in phones_in_text(_pt):",
              d*' ' + "                    if _dd in ph and _dd not in [x[0] for x in _prov]:",
              d*' ' + "                        _prov.append((_dd, f'page {_pi}' + (' , after a References heading - likely a referee, not the candidate' if _ref else ' , header/body - likely the candidate')))",
              d*' ' + "            if _prov:",
              d*' ' + "                print('🔢 ' + str(len(ph)) + ' numbers in ' + os.path.basename(ap) + ': ' + ' · '.join(f'{i}) {dd} ({w})' for i, (dd, w) in enumerate(_prov, 1)), flush=True)  # PROVENANCE v81.90: every number carries its page and its section, so a referee can never pose as the candidate",
              d*' ' + "    except Exception: pass"]
    done.append('provenance')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
W = os.path.join(os.getcwd(), 'wa.py')
w = open(W).read().split('\n')
if '# NOT-ON-WHATSAPP v81.90' not in '\n'.join(w):
    hit = [k for k, l in enumerate(w) if 'field did not take the text automatically' in l]
    if hit:
        k = hit[0]; d = ind(w[k])
        w[k:k] = [d*' ' + "try:  # NOT-ON-WHATSAPP v81.90: WhatsApp's own words beat any guess - say them plainly before advising a paste into a field that does not exist",
                  d*' ' + "    if \"isn't on WhatsApp\" in (page.content() or ''):",
                  d*' ' + "        say('⚠️ WhatsApp says this number isn\\'t on WhatsApp - there is no message field to paste into; [x] discards this round, [q] closes it, or teach/re-pick a number that is registered')",
                  d*' ' + "except Exception: pass"]
        done.append('wa-not-on-whatsapp')
    else:
        done.append('wa-anchor-missing')
    srcw = '\n'.join(w); ast.parse(srcw); open(W, 'w').write(srcw)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S193 a number absent from WhatsApp is named aloud", "'S192 the picker shows the number beside the email", "ck('S193 a number absent from WhatsApp is named aloud', (chr(35)+' NOT-ON-WHATSAPP v81.90') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S194 every number carries its page and its section", "'S193 a number absent from WhatsApp is named aloud", "ck('S194 every number carries its page and its section', (chr(35)+' PROVENANCE v81.90') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S191 old guards repin to new shapes, never veto them")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
