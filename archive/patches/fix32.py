import ast, subprocess

p = 'butler.py'; L = open(p).read().split('\n'); done = []

# 1) delete dangling bare calls to the ghost method
before = len(L)
L = [l for l in L if l.strip() != 'self._reconcile_tags(say)']
if len(L) != before: done.append('dangling-calls-removed')

# 2) normalize any swallowed heartbeat hook to a visible-error version
for i, l in enumerate(L):
    if '_reconcile_tags(print)' in l:
        d = len(l) - len(l.lstrip())
        block_start = i-1 if i-1 >= 0 and L[i-1].strip() == 'try:' else i
        block_end = i+1
        if block_end < len(L) and L[block_end].strip().startswith('except Exception'):
            if block_end+1 < len(L) and L[block_end+1].strip() == 'pass':
                block_end += 2
            else:
                block_end += 1
        L[block_start:block_end] = [d*' ' + 'try:',
                                    d*' ' + "    B._reconcile_tags(print)",
                                    d*' ' + 'except Exception as _re:',
                                    d*' ' + "    print('reconcile error:', _re)"]
        done.append('heartbeat-hook-visible')
        break

# 3) add the REAL method before handle_tags if missing
if not any(l.strip().startswith('def _reconcile_tags(') for l in L):
    a = next(k for k, l in enumerate(L) if l.strip().startswith('def handle_tags(self, p, say):'))
    d = len(L[a]) - len(L[a].lstrip())
    L[a:a] = [d*' ' + 'def _reconcile_tags(self, say):',
              d*' ' + "    def _n(s): return (s or '').lower().replace('\\u2013', '-').replace(' ', '_')",
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
              d*' ' + '            if _n(os.path.basename(dp)) == _n(tag): continue',
              d*' ' + '            tgt = os.path.join(self.root, tag)',
              d*' ' + '            if not os.path.isdir(tgt): os.makedirs(tgt)',
              d*' ' + '            dst = os.path.join(tgt, f)',
              d*' ' + '            if os.path.abspath(fp) == os.path.abspath(dst): continue',
              d*' ' + '            os.rename(fp, dst)',
              d*' ' + '            say(f"\\U0001f4c1 [reconcile] {f} -> {tag}/")',
              '']
    done.append('method-added')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('butler:', done or 'nothing missing')

# 4) PROOF: method exists + collect puts Pradip in the right row
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import butler, briefing, os
print("has _reconcile_tags:", hasattr(butler.Butler, "_reconcile_tags"))
root = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
data = briefing.collect(root)
for k, v in data.items():
    if v:
        title = next((t for kk, t, _ in briefing.TAGS if kk == k), k)
        print(f"{title}: " + ", ".join(n for n, _, _ in v))
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-400:])
