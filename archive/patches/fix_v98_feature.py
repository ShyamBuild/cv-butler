import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _tag_poll(' not in src:
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
POLL = ["if _t.time() - getattr(B, '_last_poll', 0) > 15:  # TAG-POLL v65",
        "    B._last_poll = _t.time()",
        "    for _cp in B._tag_poll(): ex.submit(work, _cp)",
        "    B._heal((lambda m: None) if INTERACTIVE else print)"]
src = '\n'.join(B)
if '# TAG-POLL v65' not in src:
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
src = '\n'.join(B)
if '# TAGS-FIRST v63' in src:
    i = next(k for k, l in enumerate(B) if '# TAGS-FIRST v63' in l)
    del B[i]
    done.append('protocol-restore-rename-then-move')
src = '\n'.join(B)
if '# RENAME-FIRST v65' not in src:
    i = next(k for k, l in enumerate(B) if '# RECONCILE-GATE v60' in l)
    B[i+1:i+1] = [ind(B[i])*' ' + 'self.handle_pdf(fp, say)  # RENAME-FIRST v65',
                  ind(B[i])*' ' + 'if not os.path.exists(fp): continue']
    done.append('reconcile-rename-first')
src = '\n'.join(B)
if '# HEAL-RETRY v65' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if self._heal_done.get(f) == key: continue')
    d = ind(B[i])
    B[i:i+2] = [d*' ' + 'prev = self._heal_done.get(f)',
                d*' ' + 'if prev and prev[0] == key and now - prev[1] < 600: continue  # HEAL-RETRY v65',
                d*' ' + 'self._heal_done[f] = (key, now)']
    done.append('heal-retry-expiry')
src = '\n'.join(B)
if '# SUFFIX-STABLE v65' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if name and f"{name}.pdf" != base:')
    d = ind(B[i])
    B[i:i+1] = [d*' ' + "_b0 = os.path.splitext(base)[0]  # SUFFIX-STABLE v65",
                d*' ' + "_okb = (not name) or _b0.lower() == name.lower() or bool(re.match(re.escape(name) + r'[_\\s]\\d+$', _b0, re.I))",
                d*' ' + "if name and not _okb:"]
    done.append('suffix-stable')
src = '\n'.join(B)
if '# SELF-FREE v65' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _rename(self, old_path, new_name, say, tag):'))
    j = next(k for k in range(i, i+20) if B[k].strip().startswith('existing = {x.lower() for x in os.listdir(dirname)}'))
    B.insert(j+1, ind(B[j])*' ' + "existing.discard(os.path.basename(old_path).lower())  # SELF-FREE v65")
    k = next(k2 for k2 in range(i, i+25) if B[k2].strip().startswith('target = os.path.join(dirname, cand)'))
    B.insert(k, ind(B[k])*' ' + "if cand.lower() == os.path.basename(old_path).lower(): return  # SELF-FREE v65")
    done.append('self-free')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S75 tag poll catches silent re-tags" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S74 worker-door journal skip" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S75 tag poll catches silent re-tags', 'def _tag_poll(' in _src and _src.count(chr(35)+' TAG-POLL') >= 2)")
    B.insert(i+2, d*' ' + "ck('S76 reconcile reads tags without mdls', _src.split('def _reconcile_tags')[1].split('\\ndef ')[0].count('_tags_of_fast(') >= 1)")
    B.insert(i+3, d*' ' + "_pdfseg = _src.split(\"elif ext == '.pdf':\")[1].split('elif ext ==')[0]")
    B.insert(i+4, d*' ' + "ck('S77 PROTOCOL rename-then-move for CVs', _pdfseg.index('self.handle_pdf(') < _pdfseg.index('self.handle_tags(') and (chr(35)+' TAGS-FIRST') not in _pdfseg)")
    B.insert(i+5, d*' ' + "ck('S78 heal retries + reconcile rename-first', (chr(35)+' HEAL-RETRY') in _src and (chr(35)+' RENAME-FIRST') in _src)")
    B.insert(i+6, d*' ' + "ck('S79 suffix-stable renames, self slot free', (chr(35)+' SUFFIX-STABLE') in _src and _src.count(chr(35)+' SELF-FREE') >= 2)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S75-S79-guards')
print('✅', done)
