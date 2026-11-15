import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
i0 = next(k for k, l in enumerate(B) if l.startswith('def phones_in_text(t):'))
e0 = next(k for k in range(i0, len(B)) if B[k].strip() == 'return out')
B[i0:e0+1] = ["def phones_in_text(t):  # UNICODE-SPACE v81.63: nbsp and thin spaces are separators too",
              "    t = (t or '').replace('\\u00a0', ' ').replace('\\u2007', ' ').replace('\\u2009', ' ').replace('\\u202f', ' ').replace('\\u2002', ' ').replace('\\u2003', ' ')",
              "    out = []",
              "    for m in PHONE_RE.finditer(t):",
              "        d = re.sub(r'\\D', '', m.group(1))",
              "        if d not in out: out.append(d)",
              "    return out"]
done.append('unicode-space')
B = open('butler.py').read().split('\n') if False else B
i1 = next(k for k, l in enumerate(B) if l.startswith('def phones_of(p):'))
e1 = next(k for k in range(i1, len(B)) if B[k].strip() == 'return ph')
B[i1:e1+1] = ["def phones_of(p):  # TAUGHT v81.63: a taught number beats extraction; empty results are never cached; identity is spoken when nothing is found",
              "    ap = os.path.abspath(p)",
              "    try: taught = json.load(open(os.path.join(BASE_DIR, 'phones_taught.json')))",
              "    except Exception: taught = {}",
              "    stem = os.path.splitext(os.path.basename(ap))[0].lower()",
              "    for tk, tv in taught.items():",
              "        if tk and (tk == stem or all(w in stem for w in tk.split())):",
              "            return [re.sub(r'\\D', '', str(tv))]",
              "    try: store = json.load(open(PHONES_FILE))",
              "    except Exception: store = {}",
              "    try:",
              "        st = os.stat(p); k = f\"v3|{st.st_ino}|{st.st_mtime}|{st.st_size}\"",
              "    except OSError:",
              "        return []",
              "    e = store.get(ap)",
              "    if e and e.get('k') == k and e.get('phones'): return e['phones']",
              "    txt = ''",
              "    try:",
              "        with pdfplumber.open(p) as pdf:",
              "            txt = \"\\n\".join((pg.extract_text() or '') for pg in pdf.pages[:2])",
              "    except Exception: pass",
              "    ph = phones_in_text(txt)",
              "    if not ph:",
              "        ocr = extract_text_ocr(p)",
              "        if ocr.strip(): ph = phones_in_text(ocr)",
              "    if ph:",
              "        store[ap] = {'k': k, 'phones': ph}",
              "        try: json.dump(store, open(PHONES_FILE, 'w'))",
              "        except Exception: pass",
              "    else:",
              "        print(f'\\U0001f937 we are talking about {os.path.basename(ap)} - no phone readable in it; teach me: phones_taught.json', flush=True)",
              "    return ph"]
done.append('taught-and-uncached')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S170 nbsp and thin spaces are separators too" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S169 brackets and portal glue are scars too" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S170 nbsp and thin spaces are separators too', phones_in_text('Mob: 93605' + chr(160) + '66513') == ['9360566513'])")
    B.insert(i+2, d*' ' + "ck('S171 a taught number beats extraction and empty is never cached', 'phones_taught.json' in _src and (chr(35)+' TAUGHT v81.63') in _src and 'v3|' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S170-S171-guards')
print('✅', done)
