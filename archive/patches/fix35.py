import ast, subprocess
def ind(l): return len(l) - len(l.lstrip())
def cut(L, i, stop_ind=None):
    d = stop_ind if stop_ind is not None else ind(L[i]); j = i + 1
    while j < len(L):
        s = L[j]
        if s.strip() and ind(s) <= d and (s.lstrip().startswith('def ') or s.lstrip().startswith('class ')): break
        j += 1
    return j
done = []
p = 'butler.py'; L = open(p).read().split('\n')

# 0) delete any module-level (indent 0) impostor _reconcile_tags
i = 0
while i < len(L):
    if L[i].startswith('def _reconcile_tags('):
        L[i:cut(L, i, 0)] = []; done.append('imposter-removed'); continue
    i += 1

# 1) mdls-FIRST get_tags (plist only as fallback)
i = next(k for k, l in enumerate(L) if l.strip().startswith('def get_tags('))
L[i:cut(L, i, 0)] = [
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
 "                    elif rest.startswith('(') and rest.endswith(')'):",
 "                        item = rest[1:-1].strip().rstrip(',')",
 '                        if item.startswith(\'"\') and item.endswith(\'"\'): item = item[1:-1]',
 "                        nm = _unescape(item).split(chr(10))[0].strip()",
 '                        if nm and nm not in COLOR_TAGS: tags.append(nm)',
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

# 2) _reconcile_tags INSIDE the class, anchored on def route
if not any(l.strip().startswith('def _reconcile_tags(') and ind(l) == 4 for l in L):
    a = next(k for k, l in enumerate(L) if l == '    def route(self, p, say):')
    L[a:a] = ['    def _reconcile_tags(self, say):',
              "        def _n(s): return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')",
              '        known = {_n(t): t for t in TAG_NAMES}',
              '        for dp, dn, fn in os.walk(self.root):',
              '            dn[:] = [x for x in dn if not x.startswith(".")]',
              '            for f in fn:',
              '                if not f.lower().endswith(".pdf"): continue',
              '                fp = os.path.join(dp, f)',
              '                T = get_tags(fp)',
              '                tag = None',
              '                for t in T:',
              '                    if _n(t) in known: tag = known[_n(t)]; break',
              '                if not tag: continue',
              '                tgt = os.path.join(self.position_folder_for(fp), tag)',
              '                if os.path.abspath(os.path.dirname(fp)) == os.path.abspath(tgt): continue',
              '                os.makedirs(tgt, exist_ok=True)',
              '                dst = os.path.join(tgt, f)',
              '                if os.path.exists(dst): continue',
              '                os.rename(fp, dst)',
              "                with self.lock: self.stats['moved'] += 1",
              '                say(f"\\U0001f4c1 [reconcile] {f} -> {tag}/")',
              '']
    done.append('reconcile-in-class')

# 3) heartbeat visible + EOF stray gone
out = []; k = 0
while k < len(L):
    l = L[k]
    if l.strip() == 'try: B._reconcile_tags(print)' and k+1 < len(L) and L[k+1].strip() == 'except Exception: pass':
        d = ind(l)
        if d == 0:
            k += 2; done.append('eof-stray-removed'); continue
        out.append(d*' ' + 'try: B._reconcile_tags(print)')
        out.append(d*' ' + "except Exception as _re: print('reconcile error:', _re)")
        done.append('heartbeat-visible'); k += 2; continue
    out.append(l); k += 1
L = out
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)

# 4) briefing: mdls-first _tags_of + unescape in _norm
p = 'briefing.py'; L = open(p).read().split('\n')
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _tags_of('))
L[i:cut(L, i, 0)] = [
 'def _unescape(s):',
 '    BS = chr(92)',
 "    s = re.sub(BS + 'U([0-9a-fA-F]{4,8})', lambda m: chr(int(m.group(1), 16)), s)",
 "    s = re.sub(BS + 'u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)",
 "    s = s.replace(BS + '\"', '\"')",
 '    return s',
 'def _tags_of(path):',
 '    try:',
 "        r = subprocess.run(['mdls', '-name', 'kMDItemUserTags', path], capture_output=True, text=True, timeout=15)",
 "        out = (r.stdout or '').strip()",
 "        if out and '(null)' not in out:",
 '            tags = []',
 '            for line in out.splitlines():',
 '                line = line.strip().rstrip(\',\')',
 "                if line in ('(', ')') or line.startswith('kMDItemUserTags'): continue",
 '                if line.startswith(\'"\') and line.endswith(\'"\'): line = line[1:-1]',
 "                nm = _unescape(line).split(chr(10))[0].strip()",
 '                if nm and nm not in COLOR_TAGS: tags.append(nm)',
 '            if tags: return tags',
 '    except Exception:',
 '        pass',
 '    try:',
 '        import plistlib',
 "        arr = plistlib.loads(os.getxattr(path, 'com.apple.metadata:_kMDItemUserTags'))",
 '        out = []',
 '        for t in arr:',
 "            nm = str(t).split(chr(10))[0].strip()",
 '            if nm and nm not in COLOR_TAGS: out.append(nm)',
 '        return out',
 '    except Exception:',
 '        return []',
 '']
done.append('briefing-mdls-first')
for i, l in enumerate(L):
    if l.strip().startswith('def _norm('):
        d = ind(l)
        L[i+1:i+1] = [d*' ' + '    s = _unescape(s)']
        done.append('norm-unescapes'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)

r = subprocess.run(['cv_env/bin/python3', '-c', '''
import butler, briefing, os
print("has _reconcile_tags:", hasattr(butler.Butler, "_reconcile_tags"))
p = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location/Call Scheduled/Pradip Amte.pdf"
print("butler get_tags:", butler.get_tags(p) if os.path.exists(p) else "missing")
print("briefing _tags_of:", briefing._tags_of(p) if os.path.exists(p) else "missing")
root = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
data = briefing.collect(root)
for k, v in data.items():
    if v:
        t = next(x for kk, x, _ in briefing.TAGS if kk == k)
        print(f"{t}: " + ", ".join(n for n, _, _ in v))
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-400:])
