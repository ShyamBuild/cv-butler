import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _sniff_ext(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('SETTLE_EXTS ='))
    B[i:i] = ["def _sniff_ext(p):",
              "    try:",
              "        with open(p, 'rb') as f: h = f.read(8)",
              "    except Exception:",
              "        return None",
              "    if h.startswith(b'%PDF'): return '.pdf'",
              "    if h.startswith(b'PK\\x03\\x04'):",
              "        try:",
              "            import zipfile",
              "            n = zipfile.ZipFile(p).namelist()",
              "            if any(x.startswith('word/') for x in n): return '.docx'",
              "            if any(x.startswith('xl/') for x in n): return '.xlsx'",
              "        except Exception:",
              "            return None",
              "    if h.startswith(b'\\xd0\\xcf\\x11\\xe0'): return '.doc'",
              "    return None",
              ""]
    done.append('sniff-helper')
src = '\n'.join(B)
if '# SNIFF-EXT v70' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'ext = os.path.splitext(p)[1].lower()' and k > next(j for j, l2 in enumerate(B) if l2.strip().startswith('def _route(self, p, say):')))
    B.insert(i+1, ind(B[i])*' ' + "if ext not in ('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx'):  # SNIFF-EXT v70")
    B.insert(i+2, ind(B[i])*' ' + "    _se = _sniff_ext(p)")
    B.insert(i+3, ind(B[i])*' ' + "    if _se:")
    B.insert(i+4, ind(B[i])*' ' + "        _d = os.path.dirname(p); _b = os.path.splitext(os.path.basename(p))[0] or 'untitled'")
    B.insert(i+5, ind(B[i])*' ' + "        _c = os.path.join(_d, _b + _se); _n = 1")
    B.insert(i+6, ind(B[i])*' ' + "        while os.path.exists(_c): _c = os.path.join(_d, f'{_b}_{_n}{_se}'); _n += 1")
    B.insert(i+7, ind(B[i])*' ' + "        try:")
    B.insert(i+8, ind(B[i])*' ' + "            os.rename(p, _c); say(f'🧩 [suffix] {os.path.basename(p)} -> {os.path.basename(_c)}'); p = _c; ext = _se")
    B.insert(i+9, ind(B[i])*' ' + "        except Exception: pass")
    done.append('route-sniff')
src = '\n'.join(B)
old = "                if not bl.endswith(('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx')): continue"
if old in src:
    i = next(k for k, l in enumerate(B) if l == old)
    B[i:i+1] = ["                if bl.endswith(SETTLE_EXTS): continue",
                "                if '.' in bl and not bl.endswith(('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx')): continue"]
    done.append('heal-extless')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S88 extension-less files get sniffed" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S87 snapshot call lives in heartbeat" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S88 extension-less files get sniffed', 'def _sniff_ext(' in _src and (chr(35)+' SNIFF-EXT') in _src and _src.count('_sniff_ext(') >= 2)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S88-guard')
print('✅', done)
