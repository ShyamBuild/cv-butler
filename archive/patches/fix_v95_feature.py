import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if 'def _tag_poll(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _heal(self, say=print):'))
    B[i:i] = ["    def _tag_poll(self):",
              "        import zlib as _z",
              "        if not hasattr(self, '_tagcrc'): self._tagcrc = {}",
              "        changed = []",
              "        for dp, dn, fn in os.walk(self.root):",
              "            dn[:] = [d for d in dn if not d.startswith('.')]",
              "            for f in fn:",
              "                if not f.lower().endswith(('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx')): continue",
              "                fp = os.path.join(dp, f)",
              "                try:",
              "                    tg = os.getxattr(fp, 'com.apple.metadata:_kMDItemUserTags')",
              "                except Exception:",
              "                    tg = b''",
              "                c = _z.crc32(tg)",
              "                old = self._tagcrc.get(fp)",
              "                self._tagcrc[fp] = c",
              "                if old is not None and old != c: changed.append(fp)",
              "        if len(self._tagcrc) > 20000: self._tagcrc = {}",
              "        return changed",
              ""]
    done.append('tag-poll-method')
POLL = ["if _t.time() - getattr(B, '_last_poll', 0) > 15:  # TAG-POLL v64",
        "    B._last_poll = _t.time()",
        "    for _cp in B._tag_poll(): ex.submit(work, _cp)",
        "    B._heal((lambda m: None) if INTERACTIVE else print)"]
src = '\n'.join(B)
if '# TAG-POLL v64' not in src:
    i = next(k for k, l in enumerate(B) if '_t.sleep(2); continue' in l)
    B[i:i] = [ind(B[i])*' ' + x for x in POLL]
    done.append('tag-poll-idle')
    j = next(k for k, l in enumerate(B) if l.strip() == 'if time.time() - last_full > 20:')
    B[j:j] = [ind(B[j])*' ' + x for x in POLL]
    done.append('tag-poll-active')
src = '\n'.join(B)
if src.count('_tags_of_fast(fp) or get_tags(fp)') < 1:
    i = next(k for k, l in enumerate(B) if l.strip() == 'T = get_tags(fp)')
    B[i] = ind(B[i])*' ' + 'T = _tags_of_fast(fp) or get_tags(fp)'
    done.append('reconcile-fast-tags')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S75 tag poll catches silent re-tags" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S74 worker-door journal skip" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S75 tag poll catches silent re-tags', 'def _tag_poll(' in _src and (chr(35)+' TAG-POLL') in _src and _src.count(chr(35)+' TAG-POLL') >= 2)")
    B.insert(i+2, d*' ' + "ck('S76 reconcile reads tags without mdls', _src.split('def _reconcile_tags')[1].split('\\ndef ')[0].count('_tags_of_fast(') >= 1)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S75-S76-guards')
print('✅', done)
