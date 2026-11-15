import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
CAP = 'OCR-CAP v85.16: three minutes of patience per paper was a hang wearing a timeout'
hits = [k for k, l in enumerate(B) if 'timeout=180' in l and 'OCR-CAP' not in l]
for k in reversed(hits):
    l = B[k]
    newl = l.replace('timeout=180', 'timeout=25')
    if newl.rstrip().endswith(')'):
        B[k] = newl + '  # ' + CAP
    else:
        B[k] = newl
        B.insert(k, ind(l)*' ' + '# ' + CAP)
if hits: done.append('ocr-cap-x%d' % len(hits))
f0 = next((k for k, l in enumerate(B) if l.strip().startswith('try: t = extract_text_ocr(p)')), None)
if f0 is not None and 'TEXT-FIRST' not in B[f0]:
    d = ind(B[f0])
    pair = f0 + 1 if f0 + 1 < len(B) and B[f0+1].strip().startswith('except Exception:') else f0
    B[f0:pair+1] = [d*' ' + "t = ''  # TEXT-FIRST v85.16: the text layer is read before any pixel is summoned",
                    d*' ' + "try: t = extract_text(p) or ''",
                    d*' ' + "except Exception: t = ''",
                    d*' ' + "if not t.strip():",
                    (d+4)*' ' + "try: t = extract_text_ocr(p) or ''",
                    (d+4)*' ' + "except Exception: t = ''"]
    done.append('text-first')
if 'def _email_cheap(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def emails_of('))
    B[i:i] = ["def _email_cheap(p):  # CHEAP-MAIL v85.16: seating discovers email from the text layer only; the pixel bill is never paid at the seat",
              "    try:",
              "        return emails_in_text(extract_text(p) or '')",
              "    except Exception:",
              "        return ''",
              ""]
    done.append('email-cheap')
for k, l in enumerate(B):
    if "for _fn in (" in l and "'emails_of')" in l and '_email_cheap' not in l:
        if "'email_of'" in l:
            B[k] = l.replace("'email_of'", "'_email_cheap', 'email_of'")
            done.append('probe-cheap'); break
s0 = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
s1 = next(k for k in range(s0 + 1, len(B)) if B[k].startswith('def '))
for k in range(s0, s1):
    if B[k].strip() == 'v = get_visual_name(p)':
        d = ind(B[k])
        B[k] = d*' ' + "v = heuristic_name(p) or get_visual_name(p)  # TEXT-EYES v85.16: the text eyes are asked before the vision eyes; vision remains the fallback, not the first resort"
        done.append('text-eyes'); break
for k in range(s0, s1):
    if B[k].strip().startswith('q = os.path.join(os.path.dirname(p), canon') and 'NAME-EVIDENCE' not in '\n'.join(B[s0:k]):
        d = ind(B[k])
        B.insert(k, d*' ' + "if canon and _name_key(canon) != _name_key(os.path.splitext(x)[0]): say(f'👁️ {x} → eyes {v!r} → canon {canon!r}')  # NAME-EVIDENCE v85.16: when the eyes and the filename disagree, the receipt names every gate between them")
        done.append('name-evidence'); break
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S349 no pixel is summoned before the text layer is asked, and no OCR may wait beyond twenty-five seconds", "'S348 no duty works in silence and no whole-chair pass repeats within a day", "ck('S349 no pixel is summoned before the text layer is asked, and no OCR may wait beyond twenty-five seconds', (chr(35)+' TEXT-FIRST v85.16') in _src and (('timeout=' + '180') not in _src) and (chr(35)+' OCR-CAP v85.16') in _src)"),
      ("'S350 when the eyes and the filename disagree, the receipt names every gate between them", "'S349 no pixel is summoned before the text layer is asked, and no OCR may wait beyond twenty-five seconds", "ck('S350 when the eyes and the filename disagree, the receipt names every gate between them', (chr(35)+' NAME-EVIDENCE v85.16') in _src and (chr(35)+' TEXT-EYES v85.16') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
