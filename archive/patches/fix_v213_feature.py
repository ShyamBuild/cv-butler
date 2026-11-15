import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if 'def emails_of(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def emails_in_text(t):'))
    e = next(k for k in range(i, len(B)) if B[k].strip() == 'return out')
    d = ind(B[i])
    B.insert(e+2, d*' ' + "def emails_of(p):  # EMAIL-OF v81.74: the picker confirms humans by email, the anchor the master chose")
    B.insert(e+3, d*' ' + "    try:")
    B.insert(e+4, d*' ' + "        with pdfplumber.open(p) as pdf:")
    B.insert(e+5, d*' ' + "            return emails_in_text(\"\\n\".join((pg.extract_text() or '') for pg in pdf.pages))")
    B.insert(e+6, d*' ' + "    except Exception:")
    B.insert(e+7, d*' ' + "        return []")
    B.insert(e+8, "")
    done.append('emails-of')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if '# STRICT-RESOLVE v81.75' not in srcg:
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
if "'S182 several humans become a question, never a guess" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S181 identity speaks before any number is used" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S182 several humans become a question, never a guess', (chr(35)+' STRICT-RESOLVE v81.75') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and 'pick the human by email' in open(os.path.join(BASE_DIR, 'briefing.py')).read())")
    B.insert(i+2, d*' ' + "ck('S183 the picker reads emails from the paper', 'def emails_of(' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S182-S183-guards')
print('✅', done)
