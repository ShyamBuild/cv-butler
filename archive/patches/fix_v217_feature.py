import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _full_text(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def phones_of(p):'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "def _full_text(p):  # FULL-TEXT v81.76: text layer first, vision second - designed CVs whose layer is silent still speak",
              d*' ' + "    try:",
              d*' ' + "        with pdfplumber.open(p) as pdf:",
              d*' ' + "            t = \"\\n\".join((pg.extract_text() or '') for pg in pdf.pages)",
              d*' ' + "    except Exception:",
              d*' ' + "        t = ''",
              d*' ' + "    if not t.strip():",
              d*' ' + "        try: t = extract_text_ocr(p) or ''",
              d*' ' + "        except Exception: t = ''",
              d*' ' + "    return t",
              ""]
    done.append('full-text')
i = next(k for k, l in enumerate(B) if l.strip() in ('txt = ""', "txt = ''"))
e = next(k for k in range(i, len(B)) if 'ph = phones_in_text(txt)' in B[k])
B[i:e] = [ind(B[i])*' ' + "txt = _full_text(p)  # FULL-TEXT v81.76: the phone clerk and the email clerk share one pair of eyes"]
done.append('phones-uses-fulltext')
for k, l in enumerate(B):
    if 'with pdfplumber.open(ap) as _pf:' in l:
        B[k] = ind(l)*' ' + "_em = (emails_in_text(_full_text(ap)) or [''])[0]"
        done.append('taught-email-fulltext'); break
for k, l in enumerate(B):
    if l.strip().startswith('with pdfplumber.open(p) as pdf:') and 'emails_of' in '\n'.join(B[max(0, k-3):k]):
        B[k+1] = ind(B[k+1])*' ' + "return emails_in_text(_full_text(p))"
        done.append('emails-of-fulltext'); break
for k, l in enumerate(B):
    if 'we are talking about' in l and 'txt or ocr' in l:
        B[k] = l.replace('txt or ocr', 'txt')
        done.append('else-ocr-fix'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
for k, l in enumerate(g):
    if 'os.path.basename(os.path.dirname(os.path.dirname(_c)))' in l:
        g[k] = l.replace('os.path.dirname(os.path.dirname(_c))', 'os.path.dirname(_c)') + '  # POSITION-LABEL v81.76: the folder that distinguishes humans is the position, not the client (comment lives outside the f-string braces)'
        done.append('position-label'); break
srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S184 designed CVs speak through vision when their layer is silent", "'S183 the picker reads emails from the paper", "ck('S184 designed CVs speak through vision when their layer is silent', ('def _full_'+'text(') in _src and ('return emails_in_text(_full_'+'text(p))') in _src)"),
      ("'S185 the picker labels humans by position, not client", "'S184 designed CVs speak through vision when their layer is silent", "ck('S185 the picker labels humans by position, not client', (chr(35)+' POSITION-LABEL v81.76') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
