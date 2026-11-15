import ast
p = 'fitrank.py'; L = open(p).read().split('\n'); done = []
def ind(l): return len(l) - len(l.lstrip())
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _pdf_text(p):'))
j = next(k for k in range(i+1, i+12) if L[k].strip() == "except Exception: return ''")
L[i:j+1] = ["def _pdf_text(p):",
            "    t = ''",
            "    try:",
            "        import pdfplumber; out = []",
            "        with pdfplumber.open(p) as pdf:",
            "            for pg in pdf.pages[:4]: out.append(pg.extract_text() or '')",
            "        t = '\\n'.join(out)",
            "    except Exception: t = ''",
            "    if len(t.strip()) < 40:",
            "        try:",
            "            import butler",
            "            t = butler.extract_text_ocr(p) or t",
            "        except Exception: pass",
            "    return t"]
done.append('ocr-fallback')
L = open(p).read().split('\n') if False else L
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _jd_for(pos):'))
L.insert(i+1, ind(L[i+1] if i+1 < len(L) else '')*' ' + "    sp0 = _store(pos)")
L.insert(i+2, "    if os.path.exists(sp0):")
L.insert(i+3, "        d0 = json.load(open(sp0))")
L.insert(i+4, "        if d0.get('jdtext'): return d0['jdtext'], d0.get('jd')")
done.append('jd-cache-read')
for k, l in enumerate(L):
    if l.strip().startswith("d = json.load(open(sp)) if os.path.exists(sp) else"):
        L.insert(k+1, ind(l)*' ' + "d['jdtext'] = jdt")
        done.append('jd-cache-write'); break
for k, l in enumerate(L):
    if l.strip().startswith('if ch: json.dump(d, open(sp'):
        d = ind(l)
        blk = [d*' ' + 'budget = 3',
               d*' ' + 'for sub in sorted(os.listdir(pos)):',
               d*' ' + '    sp2 = os.path.join(pos, sub)',
               d*' ' + "    if not os.path.isdir(sp2) or sub.startswith('.'): continue",
               d*' ' + '    for f in os.listdir(sp2):',
               d*' ' + '        if budget <= 0: break',
               d*' ' + '        fp = os.path.join(sp2, f); lf = f.lower()',
               d*' ' + "        if not lf.endswith('.pdf') or lf.startswith('jd') or ' jd' in lf: continue",
               d*' ' + '        st = os.stat(fp); key = f\'{st.st_mtime_ns}|{st.st_size}\'',
               d*' ' + "        if d['rows'].get(f, {}).get('key') == key: continue",
               d*' ' + '        txt = _text(fp)',
               d*' ' + '        if not txt.strip(): continue',
               d*' ' + "        r = rank(txt, jdt, w); r['key'] = key; r['at'] = int(time.time()); r['called'] = d['rows'].get(f, {}).get('called', False); r['sub'] = sub",
               d*' ' + "        d['rows'][f] = r; ch = True; budget -= 1"]
        L[k:k] = blk
        done.append('deep-throttled-ranking'); break
for k, l in enumerate(L):
    if 'no ranking yet for' in l:
        L[k] = ind(l)*' ' + "say(f'no rankings yet for {os.path.basename(pos)} - JD ' + ('found; ranking fills within a few sweeps' if _jd_for(pos)[0] else 'MISSING in this folder'))"
        done.append('honest-message'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S33 fitrank ocr + deep throttle" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S32 call/next routed" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S33 fitrank ocr + deep throttle', os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fitrank.py')) and 'budget = 3' in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fitrank.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S33-guard')
print('✅', done)
