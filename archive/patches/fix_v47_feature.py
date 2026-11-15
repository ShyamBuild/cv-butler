import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
def ind(l): return len(l) - len(l.lstrip())
if 'DOWNLOAD-STABILITY-GATE' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def route(self, p, say):'))
    d = ind(L[i])
    L[i+1:i+1] = [d*' ' + '    # DOWNLOAD-STABILITY-GATE v39',
                  d*' ' + '    try:',
                  d*' ' + '        _bn = os.path.basename(p).lower()',
                  d*' ' + "        if _bn.endswith(('.crdownload', '.part', '.tmp', '.tmp.html', '.download')) or _bn.startswith('unconfirmed'):",
                  d*' ' + '            return',
                  d*' ' + '        _st = os.stat(p)',
                  d*' ' + '        if _st.st_size == 0:',
                  d*' ' + '            return',
                  d*' ' + '        if time.time() - _st.st_mtime < 3.0:',
                  d*' ' + '            time.sleep(2.0)',
                  d*' ' + '            _s2 = os.stat(p)',
                  d*' ' + '            if _s2.st_size != _st.st_size or _s2.st_mtime != _st.st_mtime:',
                  d*' ' + '                return',
                  d*' ' + '    except Exception:',
                  d*' ' + '        return']
    done.append('route-stability-gate')
if 'conversion skipped' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def convert_doc('))
    d = ind(L[i])
    L[i+1:i+1] = [d*' ' + '    try:',
                  d*' ' + '        if os.path.getsize(doc_path) == 0:',
                  d*' ' + "            print('⚠️ conversion skipped: source is 0 bytes (still downloading?)')",
                  d*' ' + '            return False',
                  d*' ' + '    except Exception:',
                  d*' ' + '        return False']
    done.append('converter-zero-byte-guard')
B = L
if "'S29 download stability gate" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S28 learned phone beats extraction" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S29 download stability gate', (chr(35) + ' DOWNLOAD-STABILITY-GATE') in _src)")
    B.insert(i+2, d*' ' + "ck('S30 converter refuses empty sources', ('conversion skipped: ' + 'source is 0 bytes') in _src)")
    done.append('S29-S30-guards')
open(p, 'w').write('\n'.join(L))
print('✅', done or 'nothing missing')
