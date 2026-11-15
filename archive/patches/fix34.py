import ast, subprocess
def ind(l): return len(l) - len(l.lstrip())
def cut(L, i):
    d = ind(L[i]); j = i + 1
    while j < len(L):
        s = L[j]
        if s.strip() and ind(s) <= d and (s.lstrip().startswith('def ') or s.lstrip().startswith('class ')): break
        j += 1
    return j
done = []
p = 'butler.py'; L = open(p).read().split('\n')

# 1) tag sight restored: plist-first get_tags + valid _unescape
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _unescape('))
L[i:cut(L, i)] = [
 'def _unescape(s):',
 '    BS = chr(92)',
 "    s = re.sub(BS + 'U([0-9a-fA-F]{4,8})', lambda m: chr(int(m.group(1), 16)), s)",
 "    s = re.sub(BS + 'u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)",
 "    s = s.replace(BS + '\"', '\"')",
 "    s = s.replace(BS + 'n', chr(10))",
 "    s = s.replace(BS + 't', chr(9))",
 '    return s',
 'def _tags_from_plist(path):',
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
 '        return None',
 'def get_tags(path):',
 '    t = _tags_from_plist(path)',
 '    if t is not None: return t',
 '    try:',
 "        r = subprocess.run(['mdls', '-name', 'kMDItemUserTags', path], capture_output=True, text=True, timeout=15)",
 "        out = (r.stdout or '').strip()",
 "        if not out or '(null)' in out: return []",
 '        tags, lines, i = [], out.splitlines(), 0',
 '        while i < len(lines):',
 '            line = lines[i].strip()',
 "            if line.startswith('kMDItemUserTags'):",
 "                rest = line.split('=', 1)[1].strip() if '=' in line else ''",
 "                if rest == '(':",
 '                    i += 1',
 '                    while i < len(lines):',
 "                        item = lines[i].strip().rstrip(',')",
 "                        if item == ')': break",
 '                        if item.startswith(\'"\') and item.endswith(\'"\'): item = item[1:-1]',
 "                        nm = _unescape(item).split(chr(10))[0].strip()",
 '                        if nm and nm not in COLOR_TAGS: tags.append(nm)',
 '                        i += 1',
 '            i += 1',
 '        return tags',
 '    except Exception:',
 '        return []',
 '']
done.append('get_tags-restored')

# 2) real _reconcile_tags + 3) position-anchored handle_tags
if not any(l.strip().startswith('def _reconcile_tags(') for l in L):
    a = next(k for k, l in enumerate(L) if l.strip().startswith('def handle_tags('))
    d = ind(L[a])
    L[a:a] = [d*' ' + 'def _reconcile_tags(self, say):',
              d*' ' + "    def _n(s): return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')",
              d*' ' + '    known = {_n(t): t for t in TAG_NAMES}',
              d*' ' + '    for dp, dn, fn in os.walk(self.root):',
              d*' ' + '        dn[:] = [x for x in dn if not x.startswith(".")]',
              d*' ' + '        for f in fn:',
              d*' ' + '            if not f.lower().endswith(".pdf"): continue',
              d*' ' + '            fp = os.path.join(dp, f)',
              d*' ' + '            T = get_tags(fp)',
              d*' ' + '            tag = None',
              d*' ' + '            for t in T:',
              d*' ' + '                if _n(t) in known: tag = known[_n(t)]; break',
              d*' ' + '            if not tag: continue',
              d*' ' + '            tgt = os.path.join(self.position_folder_for(fp), tag)',
              d*' ' + '            if os.path.abspath(os.path.dirname(fp)) == os.path.abspath(tgt): continue',
              d*' ' + '            os.makedirs(tgt, exist_ok=True)',
              d*' ' + '            dst = os.path.join(tgt, f)',
              d*' ' + '            if os.path.exists(dst): continue',
              d*' ' + '            os.rename(fp, dst)',
              d*' ' + "            with self.lock: self.stats['moved'] += 1",
              d*' ' + '            say(f"\\U0001f4c1 [reconcile] {f} -> {tag}/")',
              '']
    done.append('reconcile-added')
a = next(k for k, l in enumerate(L) if l.strip().startswith('def handle_tags('))
d = ind(L[a])
L[a:cut(L, a)] = [d*' ' + 'def handle_tags(self, p, say):',
                  d*' ' + '    T = get_tags(p)',
                  d*' ' + '    named = [t for t in T if t in TAG_NAMES or t.replace(chr(8211), "-") in TAG_NAMES]',
                  d*' ' + '    if not named: return',
                  d*' ' + '    tag = named[0]',
                  d*' ' + '    safe_tag = re.sub(r\'[\\\\/:*?"<>|]\', \'\', tag).strip()',
                  d*' ' + '    if not safe_tag: return',
                  d*' ' + '    target_folder = os.path.join(self.position_folder_for(p), safe_tag)',
                  d*' ' + '    if os.path.abspath(os.path.dirname(p)) == os.path.abspath(target_folder): return',
                  d*' ' + '    os.makedirs(target_folder, exist_ok=True)',
                  d*' ' + '    dst = os.path.join(target_folder, os.path.basename(p))',
                  d*' ' + '    if os.path.exists(dst):',
                  d*' ' + '        b, e = os.path.splitext(os.path.basename(p)); c = 1',
                  d*' ' + '        while os.path.exists(dst): dst = os.path.join(target_folder, f"{b}_{c}{e}"); c += 1',
                  d*' ' + '    os.rename(p, dst)',
                  d*' ' + "    with self.lock: self.stats['moved'] += 1",
                  d*' ' + '    say(f"\\U0001f4c1 [move] {os.path.basename(p)} -> {os.path.relpath(dst, self.root)}")',
                  d*' ' + "    si = getattr(self, 'scan_idx', None)",
                  d*' ' + '    if si:',
                  d*' ' + '        for k, v in list(si.items()):',
                  d*' ' + '            if v == os.path.abspath(p): si[k] = os.path.abspath(dst)',
                  d*' ' + '        self._save_idx()',
                  '']
done.append('handle_tags-anchored')

# 4) kill the ghost calls in _rename; 5) visible heartbeat errors
out = []
for l in L:
    if l.strip() == 'self._reconcile_tags(say)': continue
    out.append(l)
L = out; done.append('ghost-calls-removed')
for i, l in enumerate(L):
    if l.strip() == 'except Exception: pass' and i > 0 and 'B._reconcile_tags(print)' in L[i-1]:
        L[i] = l.replace('except Exception: pass', "except Exception as _re: print('reconcile error:', _re)")
        done.append('heartbeat-visible')
while L and not L[-1].strip(): L.pop()
if L[-1].strip() == 'except Exception: pass' and L[-2].strip() == 'try: B._reconcile_tags(print)':
    L = L[:-2]; done.append('eof-stray-removed')

# 6) tolerant phone regex; 7) ino in index
for i, l in enumerate(L):
    if l.strip().startswith('PHONE_RE = re.compile('):
        L[i] = "PHONE_RE = re.compile(r'(?:\\+?91[\\s\\-\\.]?)?([6-9](?:[\\s\\-\\.]?\\d){9})')"
        done.append('phone-regex')
    if l.strip() == 'd = m.group(1) + m.group(2)':
        L[i] = l.replace('d = m.group(1) + m.group(2)', "d = re.sub(r'\\D', '', m.group(1))")
        done.append('phone-strip')
    if l.strip().startswith('def _save_idx(self):'):
        dd = ind(l)
        L[i:cut(L, i)] = [dd*' ' + 'def _save_idx(self):',
                          dd*' ' + "    if not getattr(self, 'scan_idx', None): return",
                          dd*' ' + '    try:',
                          dd*' ' + "        json.dump({'root': self.root, 'at': time.time(),",
                          dd*' ' + "                   'idx': getattr(self, 'scan_idx', {}),",
                          dd*' ' + "                   'ino': getattr(self, 'scan_ino', {})},",
                          dd*' ' + "                  open(os.path.join(BASE_DIR, 'scan_index.json'), 'w'))",
                          dd*' ' + '    except Exception:',
                          dd*' ' + '        pass',
                          '']
        done.append('save-idx-ino'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)

# 8) briefing: inode fallback for scan numbers
p = 'briefing.py'; L = open(p).read().split('\n')
a = next(k for k, l in enumerate(L) if l.strip().startswith('def _scan_path('))
d = ind(L[a])
L[a:cut(L, a)] = [d*' ' + 'def _scan_path(num):',
                  d*' ' + '    try:',
                  d*' ' + "        d = json.load(open(os.path.join(BASE_DIR, 'scan_index.json')))",
                  d*' ' + '    except Exception:',
                  d*' ' + '        return None',
                  d*' ' + "    p = d.get('idx', {}).get(str(num))",
                  d*' ' + '    if p and os.path.exists(p): return p',
                  d*' ' + "    ino = d.get('ino', {}).get(str(num))",
                  d*' ' + '    if ino:',
                  d*' ' + "        root = d.get('root') or os.path.expanduser('~')",
                  d*' ' + '        for dp, dn, fn in os.walk(root):',
                  d*' ' + '            dn[:] = [x for x in dn if not x.startswith(".")]',
                  d*' ' + '            for f in fn:',
                  d*' ' + '                fp = os.path.join(dp, f)',
                  d*' ' + '                try:',
                  d*' ' + '                    if os.stat(fp).st_ino == ino:',
                  d*' ' + "                        d['idx'][str(num)] = fp",
                  d*' ' + "                        try: json.dump(d, open(os.path.join(BASE_DIR, 'scan_index.json'), 'w'))",
                  d*' ' + '                        except Exception: pass',
                  d*' ' + '                        return fp',
                  d*' ' + '                except OSError:',
                  d*' ' + '                    pass',
                  d*' ' + '    return None',
                  '']
done.append('scan-inode')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)

# PROOF
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import butler, briefing, os
print("has _reconcile_tags:", hasattr(butler.Butler, "_reconcile_tags"))
p = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location/Call Scheduled/Pradip Amte.pdf"
print("butler get_tags:", butler.get_tags(p) if os.path.exists(p) else "path changed - list folder")
root = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
data = briefing.collect(root)
for k, v in data.items():
    if v:
        t = next(x for kk, x, _ in briefing.TAGS if kk == k)
        print(f"{t}: " + ", ".join(n for n, _, _ in v))
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-400:])
