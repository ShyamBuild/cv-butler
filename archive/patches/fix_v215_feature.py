import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if 'if tk and (tk == stem or all(w in stem for w in tk.split())):' in l:
        B[k] = ind(l)*' ' + "if tk and (tk == stem or sorted(tk.split()) == sorted(stem.split())):  # EXACT-TEACH v81.73: a token is a whole word or nothing; 'a' inside 'sharma' is not identity"
        done.append('taught-exact'); break
for k, l in enumerate(B):
    if 'for pg in pdf.pages[:2])' in l:
        B[k] = l.replace('pdf.pages[:2]', 'pdf.pages'); done.append('all-pages'); break
src = '\n'.join(B)
if '# IDENTITY-FIRST v81.73' not in src:
    i = next(k for k, l in enumerate(B) if 'taught number in use for' in l)
    d = ind(B[i])
    B[i:i] = [d*' ' + "_em = ''",
              d*' ' + "try:",
              d*' ' + "    with pdfplumber.open(ap) as _pf: _em = (emails_in_text('\\n'.join((pg.extract_text() or '') for pg in _pf.pages)) or [''])[0]",
              d*' ' + "except Exception: pass",
              d*' ' + "print(f'\\U0001faaa {os.path.basename(ap)} · email: {_em or \"none readable\"} · taught for \"{tk}\" -> {tv}', flush=True)  # IDENTITY-FIRST v81.73: file and email before any number is used"]
    done.append('identity-first-taught')
src = '\n'.join(B)
if '# IDENTITY-FIRST-EXTRACT v81.73' not in src:
    i = next(k for k, l in enumerate(B) if '# EMAIL-ALWAYS v81.67' in l)
    d = ind(B[i])
    B[i] = d*' ' + "em = emails_in_text(txt)  # IDENTITY-FIRST-EXTRACT v81.73: file, email and source before the window opens"
    B.insert(i+1, d*' ' + "if ph: print(f'\\U0001faaa {os.path.basename(ap)} · email: {em[0] if em else \"none readable\"} · phone extracted: {ph[0]}', flush=True)")
    done.append('identity-first-extract')
src = '\n'.join(B)
if 'def emails_of(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def emails_in_text(t):'))
    e = next(k for k in range(i, len(B)) if B[k].strip() == 'return out')
    d = ind(B[i])
    B[e+2:e+2] = [d*' ' + "def emails_of(p):  # EMAIL-OF v81.74: the picker confirms humans by email, the anchor the master chose",
                  d*' ' + "    try:",
                  d*' ' + "        with pdfplumber.open(p) as pdf:",
                  d*' ' + "            return emails_in_text(\"\\n\".join((pg.extract_text() or '') for pg in pdf.pages))",
                  d*' ' + "    except Exception:",
                  d*' ' + "        return []",
                  ""]
    done.append('emails-of')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if '# STRICT-RESOLVE v81.75' not in '\n'.join(g):
    i = next(k for k, l in enumerate(g) if 'for _sr in ([] if hit else' in l)
    d = ind(g[i])
    g[i:i] = [d*' ' + "_qt = [t for t in q.split()]  # STRICT-RESOLVE v81.75: exact stem, equal token-sets, or whole words only; several humans means a question, never a guess",
              d*' ' + "_strict = []",
              d*' ' + "for _sr2 in [f['path'], os.path.dirname(os.path.dirname(f['path']))]:",
              d*' ' + "    for dp, dn, fn in os.walk(_sr2):",
              d*' ' + "        for x in fn:",
              d*' ' + "            if not x.lower().endswith('.pdf'): continue",
              d*' ' + "            _xs = os.path.splitext(x)[0].lower().replace('_', ' ')",
              d*' ' + "            if _xs == q or sorted(_xs.split()) == sorted(_qt) or all(t in _xs.split() for t in _qt):",
              d*' ' + "                _strict.append(os.path.join(dp, x))",
              d*' ' + "if len(_strict) == 1:",
              d*' ' + "    hit = _strict[0]",
              d*' ' + "elif len(_strict) > 1:",
              d*' ' + "    say('🪪 several candidates wear that name - pick the human by email:')",
              d*' ' + "    for _n, _c in enumerate(_strict, 1):",
              d*' ' + "        try: _em = (butler.emails_of(_c) or ['none readable'])[0]",
              d*' ' + "        except Exception: _em = 'none readable'",
              d*' ' + "        say(f'   {_n}) {os.path.basename(_c)} · {_em} · {os.path.basename(os.path.dirname(os.path.dirname(_c)))}')",
              d*' ' + "    try: hit = _strict[int(input('   pick #: ').strip()) - 1]",
              d*' ' + "    except Exception: say('🤷 pick skipped'); hit = None",
              ""]
    done.append('strict-resolve')
    srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S179 a taught key is whole tokens or nothing", "'S178 every voice asks the same clerk", "ck('S179 a taught key is whole tokens or nothing', 'sorted(tk.split()) == sorted(stem.split())' in _src and ('all(w in stem for w in tk.sp'+'lit())') not in _src)"),
      ("'S180 the whole paper is read, not an excerpt", "'S179 a taught key is whole tokens or nothing", "ck('S180 the whole paper is read, not an excerpt', ('txt = ' + chr(34) + chr(92) + 'n' + chr(34) + '.join((pg.extract_text() or ' + chr(39) + chr(39) + ') for pg in pdf.pages)') in _src)  # clerk-scoped: other readers may skim, the phone clerk may not"),
      ("'S181 identity speaks before any number is used", "'S180 the whole paper is read, not an excerpt", "ck('S181 identity speaks before any number is used', (chr(35)+' IDENTITY-FIRST v81.73') in _src and (chr(35)+' IDENTITY-FIRST-EXTRACT v81.73') in _src)"),
      ("'S182 several humans become a question, never a guess", "'S181 identity speaks before any number is used", "ck('S182 several humans become a question, never a guess', (chr(35)+' STRICT-RESOLVE v81.75') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and 'pick the human by email' in open(os.path.join(BASE_DIR, 'briefing.py')).read())"),
      ("'S183 the picker reads emails from the paper", "'S182 several humans become a question, never a guess", "ck('S183 the picker reads emails from the paper', 'def emails_of(' in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
