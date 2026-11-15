import ast, subprocess, re

# ---------- briefing.py: one normalization rule, tag wins, folder fallback ----------
p = 'briefing.py'; L = open(p).read().split('\n')
i = next(k for k, l in enumerate(L) if l.startswith('def collect(root):'))
j = next(k for k in range(i+1, len(L)) if L[k].startswith('def '))
# put _norm just above collect
norm = ['def _norm(s):', "    return (s or '').lower().replace('\\u2013', '-').replace(' ', '_')", '']
L[i:j] = norm + [
    'def collect(root):',
    '    data = {k: [] for k, _, _ in TAGS}',
    '    key_of = {_norm(k): k for k, _, _ in TAGS}',
    '    for dp, dn, fn in os.walk(root):',
    '        dn[:] = [d for d in dn if not d.startswith(".")]',
    '        for f in fn:',
    '            if not f.lower().endswith(".pdf") or f.startswith("."): continue',
    '            fp = os.path.join(dp, f)',
    '            tags = []',
    '            try: tags = _tags_of(fp)',
    '            except Exception: tags = []',
    '            sec = None',
    '            for t in tags:',
    '                if _norm(t) in key_of:',
    '                    sec = key_of[_norm(t)]; break',
    '            if sec is None:',
    '                rel = os.path.relpath(dp, root)',
    '                if rel != ".":',
    '                    top = _norm(rel.split(os.sep)[0])',
    '                    if top in key_of: sec = key_of[top]',
    '            if not sec: continue',
    '            pos = _pos_for(fp, root)',
    "            ph = ''",
    '            try:',
    "                ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]",
    "                ph = (ps or [''])[0] if isinstance(ps, list) else ps",
    '            except Exception:',
    '                try: ph = phone_of(fp)',
    '                except Exception: ph = ""',
    '            data[sec].append([os.path.splitext(f)[0], pos, ph])',
    '    return data',
]
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('briefing: collect rewritten with _norm')

# ---------- butler.py: clean old hooks, rewrite reconcile, visible-error hook ----------
p = 'butler.py'; L = open(p).read().split('\n')
L = [l for l in L if '_reconcile_tags(print)' not in l]
# drop orphan 'except Exception: pass' left behind directly after a blank where we removed the call
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _reconcile_tags('))
j = i + 1
while j < len(L) and (not L[j].strip() or (len(L[j]) - len(L[j].lstrip())) > (len(L[i]) - len(L[i].lstrip()))):
    j += 1
d = len(L[i]) - len(L[i].lstrip())
L[i:j] = [
    'def _reconcile_tags(self, say):',
    "    def _n(s): return (s or '').lower().replace('\\u2013', '-').replace(' ', '_')",
    '    known = {_n(t): t for t in TAG_NAMES}',
    '    for dp, dn, fn in os.walk(self.root):',
    '        dn[:] = [x for x in dn if not x.startswith(".")]',
    '        for f in fn:',
    '            if not f.lower().endswith(".pdf"): continue',
    '            fp = os.path.join(dp, f)',
    '            T = get_tags(fp)',
    '            tag = None',
    '            for t in T:',
    '                if _n(t) in known: tag = known[_n(t)]; break',
    '            if not tag: continue',
    '            if _n(os.path.basename(dp)) == _n(tag): continue',
    '            tgt = os.path.join(self.root, tag)',
    '            if not os.path.isdir(tgt): os.makedirs(tgt)',
    '            dst = os.path.join(tgt, f)',
    '            if os.path.abspath(fp) == os.path.abspath(dst): continue',
    '            os.rename(fp, dst)',
    '            say(f"\\U0001f4c1 [reconcile] {f} -> {tag}/")',
    '',
]
# heartbeat hook with VISIBLE errors
for k, l in enumerate(L):
    if 'sweep #' in l and ('print' in l or 'say' in l):
        dd = len(l) - len(l.lstrip())
        L[k+1:k+1] = [dd*' ' + "try:",
                      dd*' ' + "    (globals().get('B') or B)._reconcile_tags(print)",
                      dd*' ' + "except Exception as _re:",
                      dd*' ' + "    print('reconcile error:', _re)"]
        print('butler: reconcile hooked at heartbeat (errors visible)')
        break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('butler: reconcile rewritten')

# ---------- PROOF before you restart ----------
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import briefing, os
root = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
data = briefing.collect(root)
for k, v in data.items():
    if v:
        title = next((t for kk, t, _ in briefing.TAGS if kk == k), k)
        print(f"{title}: " + ", ".join(n for n, _, _ in v))
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-400:])
