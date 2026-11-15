import ast, subprocess
def ind(l): return len(l) - len(l.lstrip())
def block_end(L, i):
    d = ind(L[i]); j = i + 1
    while j < len(L):
        s = L[j]
        if s.strip() and ind(s) <= d and (s.lstrip().startswith('def ') or s.lstrip().startswith('class ')): break
        j += 1
    return j
done = []

# ---------------- butler.py ----------------
p = 'butler.py'; L = open(p).read().split('\n')

# 1) valid _unescape (butler stops being tag-blind)
for i, l in enumerate(L):
    if l.strip().startswith('def _unescape('):
        L[i:block_end(L, i)] = [
            'def _unescape(s):',
            '    BS = chr(92)',
            "    s = re.sub(BS + 'U([0-9a-fA-F]{4,8})', lambda m: chr(int(m.group(1), 16)), s)",
            "    s = re.sub(BS + 'u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)",
            "    s = s.replace(BS + '\"', '\"')",
            "    s = s.replace(BS + 'n', chr(10))",
            '    return s']
        done.append('unescape-fixed'); break

# 2) real _reconcile_tags method (position-level folders, no nesting)
if not any(l.strip().startswith('def _reconcile_tags(') for l in L):
    a = next(k for k, l in enumerate(L) if l.strip().startswith('def handle_tags(self, p, say):'))
    d = ind(L[a])
    L[a:a] = [d*' ' + 'def _reconcile_tags(self, say):',
              d*' ' + '    def _n(s): return (s or \'\').lower().replace(chr(8211), \'-\').replace(\' \', \'_\')',
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
              d*' ' + '            with self.lock: self.stats[\'moved\'] += 1',
              d*' ' + '            say(f"\\U0001f4c1 [reconcile] {f} -> {tag}/")',
              '']
    done.append('reconcile-added')

# 3) handle_tags moves to POSITION-level tag folder, never nested
for i, l in enumerate(L):
    if l.strip().startswith('def handle_tags(self, p, say):'):
        L[i:block_end(L, i)] = [
            '    def handle_tags(self, p, say):',
            '        T = get_tags(p)',
            '        named = [t for t in T if t in TAG_NAMES or t.replace(chr(8211), "-") in TAG_NAMES]',
            '        if not named: return',
            '        tag = named[0]',
            '        safe_tag = re.sub(r\'[\\\\/:*?"<>|]\', \'\', tag).strip()',
            '        if not safe_tag: return',
            '        target_folder = os.path.join(self.position_folder_for(p), safe_tag)',
            '        if os.path.abspath(os.path.dirname(p)) == os.path.abspath(target_folder): return',
            '        os.makedirs(target_folder, exist_ok=True)',
            '        dst = os.path.join(target_folder, os.path.basename(p))',
            '        if os.path.exists(dst):',
            '            b, e = os.path.splitext(os.path.basename(p)); c = 1',
            '            while os.path.exists(dst): dst = os.path.join(target_folder, f"{b}_{c}{e}"); c += 1',
            '        os.rename(p, dst)',
            '        with self.lock: self.stats[\'moved\'] += 1',
            '        say(f"\\U0001f4c1 [move] {os.path.basename(p)} -> {safe_tag}/")',
            '        si = getattr(self, \'scan_idx\', None)',
            '        if si:',
            '            for k, v in list(si.items()):',
            '                if v == os.path.abspath(p): si[k] = os.path.abspath(dst)',
            '            self._save_idx()',
            '']
        done.append('handle_tags-position-level'); break

# 4) single reconcile call in _rename; 5) _save_idx writes ino
out = []
for i, l in enumerate(L):
    if l.strip() == 'self._reconcile_tags(say)' and i+1 < len(L) and L[i+1].strip() == 'self._reconcile_tags(say)':
        out.append(l); continue
    if l.strip() == 'self._reconcile_tags(say)' and i > 0 and L[i-1].strip() == 'self._reconcile_tags(say)':
        continue
    out.append(l)
L = out; done.append('single-reconcile-call')
for i, l in enumerate(L):
    if l.strip().startswith('def _save_idx(self):'):
        d = ind(l)
        L[i:block_end(L, i)] = [d*' ' + 'def _save_idx(self):',
                                d*' ' + "    if not getattr(self, 'scan_idx', None): return",
                                d*' ' + '    try:',
                                d*' ' + "        json.dump({'root': self.root, 'at': time.time(),",
                                d*' ' + "                   'idx': getattr(self, 'scan_idx', {}),",
                                d*' ' + "                   'ino': getattr(self, 'scan_ino', {})},",
                                d*' ' + "                  open(os.path.join(BASE_DIR, 'scan_index.json'), 'w'))",
                                d*' ' + '    except Exception:',
                                d*' ' + '        pass',
                                '']
        done.append('save-idx-ino'); break
# 6) drop stray module-level reconcile at EOF
while L and (L[-1].strip() == '' ): L.pop()
if L[-1].strip() == 'except Exception: pass' and len(L) > 1 and L[-2].strip() == 'try: B._reconcile_tags(print)':
    L = L[:-2]; done.append('eof-stray-removed')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)

# ---------------- briefing.py ----------------
p = 'briefing.py'; L = open(p).read().split('\n')
# single _norm
idxs = [i for i, l in enumerate(L) if l.strip().startswith('def _norm(')]
if len(idxs) > 1:
    for i in reversed(idxs[1:]):
        del L[i:i+2]
    done.append('norm-deduped')
for i, l in enumerate(L):
    if l.strip().startswith('def _norm('):
        L[i:block_end(L, i)] = ['def _norm(s):',
                                "    return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')",
                                '']
        done.append('norm-single'); break
# inode-aware _scan_path
for i, l in enumerate(L):
    if l.strip().startswith('def _scan_path('):
        L[i:block_end(L, i)] = [
            'def _scan_path(num):',
            '    try:',
            "        d = json.load(open(os.path.join(BASE_DIR, 'scan_index.json')))",
            '    except Exception:',
            '        return None',
            "    p = d.get('idx', {}).get(str(num))",
            '    if p and os.path.exists(p): return p',
            "    ino = d.get('ino', {}).get(str(num))",
            '    if ino:',
            "        root = d.get('root') or os.path.expanduser('~')",
            '        for dp, dn, fn in os.walk(root):',
            '            dn[:] = [x for x in dn if not x.startswith(".")]',
            '            for f in fn:',
            '                fp = os.path.join(dp, f)',
            '                try:',
            '                    if os.stat(fp).st_ino == ino:',
            "                        d['idx'][str(num)] = fp",
            "                        try: json.dump(d, open(os.path.join(BASE_DIR, 'scan_index.json'), 'w'))",
            '                        except Exception: pass',
            '                        return fp',
            '                except OSError:',
            '                    pass',
            '    return None',
            '']
        done.append('scan-inode'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)

print('✅', done)
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import butler, briefing
p = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location/Call Scheduled/Pradip Amte.pdf"
import os
if os.path.exists(p):
    print("butler get_tags:", butler.get_tags(p))
root = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
data = briefing.collect(root)
for k, v in data.items():
    if v:
        t = next(x for kk, x, _ in briefing.TAGS if kk == k)
        print(f"{t}: " + ", ".join(n for n, _, _ in v))
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-400:])
