import ast, subprocess
def ind(l): return len(l) - len(l.lstrip())
p = 'butler.py'; L = open(p).read().split('\n'); done = []
d_cls = ind(next(l for l in L if l.strip().startswith('def _check_siblings(')))

# 1) pull handle_tags INTO the class if it is orphaned at module level
a = next(k for k, l in enumerate(L) if l.strip().startswith('def handle_tags('))
if ind(L[a]) < d_cls:
    b = next(k for k in range(a+1, len(L)) if L[k].strip().startswith('def ') and ind(L[k]) <= ind(L[a]))
    shift = d_cls - ind(L[a])
    L[a:b] = [ (ind(l)+shift)*' ' + l.strip() if l.strip() else '' for l in L[a:b] ]
    done.append('handle_tags-into-class')

# 2) real _reconcile_tags as a class method
if not any(l.strip().startswith('def _reconcile_tags(') and ind(l) == d_cls for l in L):
    r = next(k for k, l in enumerate(L) if l.strip().startswith('def route(') and ind(l) == d_cls)
    L[r:r] = [d_cls*' ' + 'def _reconcile_tags(self, say):',
              d_cls*' ' + "    def _n(s): return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')",
              d_cls*' ' + '    known = {_n(t): t for t in TAG_NAMES}',
              d_cls*' ' + '    for dp, dn, fn in os.walk(self.root):',
              d_cls*' ' + '        dn[:] = [x for x in dn if not x.startswith(".")]',
              d_cls*' ' + '        for f in fn:',
              d_cls*' ' + '            if not f.lower().endswith(".pdf"): continue',
              d_cls*' ' + '            fp = os.path.join(dp, f)',
              d_cls*' ' + '            T = get_tags(fp)',
              d_cls*' ' + '            tag = None',
              d_cls*' ' + '            for t in T:',
              d_cls*' ' + '                if _n(t) in known: tag = known[_n(t)]; break',
              d_cls*' ' + '            if not tag: continue',
              d_cls*' ' + '            tgt = os.path.join(self.position_folder_for(fp), tag)',
              d_cls*' ' + '            if os.path.abspath(os.path.dirname(fp)) == os.path.abspath(tgt): continue',
              d_cls*' ' + '            os.makedirs(tgt, exist_ok=True)',
              d_cls*' ' + '            dst = os.path.join(tgt, f)',
              d_cls*' ' + '            if os.path.exists(dst): continue',
              d_cls*' ' + '            os.rename(fp, dst)',
              d_cls*' ' + "            with self.lock: self.stats['moved'] += 1",
              d_cls*' ' + '            say(f"\\U0001f4c1 [reconcile] {f} -> {tag}/")',
              '']
    done.append('reconcile-added')

# 3) mdls-FIRST get_tags (plist only as fallback)
g = next(k for k, l in enumerate(L) if l.strip().startswith('def get_tags('))
e = next(k for k in range(g+1, len(L)) if L[k].strip().startswith('def ') and ind(L[k]) == 0)
L[g:e] = [
 'def get_tags(path):',
 '    try:',
 "        r = subprocess.run(['mdls', '-name', 'kMDItemUserTags', path], capture_output=True, text=True, timeout=15)",
 "        out = (r.stdout or '').strip()",
 "        if out and '(null)' not in out:",
 '            tags, lines, k = [], out.splitlines(), 0',
 '            while k < len(lines):',
 '                line = lines[k].strip()',
 "                if line.startswith('kMDItemUserTags'):",
 "                    rest = line.split('=', 1)[1].strip() if '=' in line else ''",
 "                    if rest == '(':",
 '                        k += 1',
 '                        while k < len(lines):',
 "                            item = lines[k].strip().rstrip(',')",
 "                            if item == ')': break",
 '                            if item.startswith(\'"\') and item.endswith(\'"\'): item = item[1:-1]',
 "                            nm = _unescape(item).split(chr(10))[0].strip()",
 '                            if nm and nm not in COLOR_TAGS: tags.append(nm)',
 '                            k += 1',
 '                k += 1',
 '            if tags: return tags',
 '    except Exception:',
 '        pass',
 '    try:',
 '        import plistlib',
 "        data = os.getxattr(path, 'com.apple.metadata:_kMDItemUserTags')",
 '        out = []',
 '        def walk(o):',
 '            if isinstance(o, str):',
 '                nm = o.split(chr(10))[0].strip()',
 '                if nm and nm not in COLOR_TAGS: out.append(nm)',
 '            elif isinstance(o, (list, tuple)):',
 '                for x in o: walk(x)',
 '        walk(plistlib.loads(data))',
 '        return out',
 '    except Exception:',
 '        return []',
 '']
done.append('get_tags-mdls-first')

# 4) loosen the two brakes that froze renames
for i, l in enumerate(L):
    if 'self.rc.get(ino, 0) >= 2' in l:
        L[i] = l.replace('>= 2', '>= 5'); done.append('rc-raised')
    if "_ck not in getattr(self, '_ocr_done', set())" in l:
        L[i] = l.replace("_ck not in getattr(self, '_ocr_done', set())", "getattr(self, '_ocr_tries', {}).get(_ck, 0) < 3")
        done.append('ocr-retry')
    if "self._ocr_done = getattr(self, '_ocr_done', set()); self._ocr_done.add(_ck)" in l:
        L[i] = "            self._ocr_tries = getattr(self, '_ocr_tries', {}); self._ocr_tries[_ck] = self._ocr_tries.get(_ck, 0) + 1"
        done.append('ocr-counter')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import butler, os
print("handle_tags on class:", hasattr(butler.Butler, "handle_tags"))
print("_reconcile_tags on class:", hasattr(butler.Butler, "_reconcile_tags"))
p = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location/Call Scheduled/Pradip Amte.pdf"
print("get_tags:", butler.get_tags(p) if os.path.exists(p) else "path moved")
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-400:])
