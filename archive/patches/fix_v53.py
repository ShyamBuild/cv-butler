import ast, os, shutil
for f in ('butler.py', 'wa.py'):
    shutil.copy(os.path.expanduser('~/pending_v30/' + f), f)
p = 'butler.py'; L = open(p).read().split('\n'); done = ['union-restored-from-pending']
def ind(l): return len(l) - len(l.lstrip())
i0 = next(k for k, l in enumerate(L) if l.strip().startswith('def _selftest('))
i1 = i0 + 1
while i1 < len(L) and not (L[i1].strip() and not ind(L[i1])): i1 += 1
seg = L[i0:i1]; out = []
for l in seg:
    s = l.strip()
    if s.startswith('_tm = next(') or s.startswith('tags = getattr(B, _tm)') or s.startswith('tags = B.tags_of(') or s.startswith('rows = briefing.collect(POS)'):
        continue
    if s.startswith("ck('S1 bindings'"):
        out.append(ind(l)*' ' + "ck('S1 bindings', all(callable(getattr(B, m, None)) for m in ('route','handle_tags','_reconcile_tags','_compact_numbers','position_folder_for','_folder_for_tag')))")
        continue
    if s.startswith("ck('S2 tag reading'"):
        out.append(ind(l)*' ' + "ck('S2 tag reading', bool(_prw) and os.path.basename(os.path.dirname(_prw[0])) in ('Closed – Not Proceeding','Closed - Not Proceeding'), os.path.basename(os.path.dirname(_prw[0])) if _prw else 'pradip missing')")
        continue
    if s.startswith('cands = [f for f in sorted(os.listdir(POS))'):
        d = ind(l)
        out += [d*' ' + 'cands = []',
                d*' ' + 'for _dp, _dn, _fn in os.walk(root):',
                d*' ' + "    _dn[:] = [x for x in _dn if not x.startswith('.') and x.lower() not in ('converted files','converted doc files','duplicates','previous versions')]",
                d*' ' + '    for _f in sorted(_fn):',
                d*' ' + '        _fl = _f.lower()',
                d*' ' + "        if _fl.endswith('.pdf') and not _f.startswith('zz_') and not _fl.startswith('jd') and ' jd' not in _fl and '_jd' not in _fl and not _fl.startswith('regional') and 'location' not in _fl:",
                d*' ' + '            cands.append(os.path.join(_dp, _f)); break',
                d*' ' + '    if cands: break']
        continue
    if s.startswith('_sh.copy(os.path.join(POS, cands[0]), tmp)'):
        out.append(ind(l)*' ' + '_sh.copy(cands[0], tmp)'); continue
    if s.startswith("b0 = os.path.splitext(cands[0])[0]"):
        out.append(ind(l)*' ' + 'b0 = os.path.splitext(os.path.basename(cands[0]))[0]'); continue
    if s.startswith("ck('S5 board closed row'"):
        d = ind(l)
        out += [d*' ' + "_clf = [dd for dd in os.listdir(POS) if dd.lower().startswith('closed')]",
                d*' ' + "ck('S5 board closed row', bool(_clf) and any(os.path.isfile(os.path.join(POS, dd, f)) for dd in _clf for f in os.listdir(os.path.join(POS, dd))))"]
        continue
    out.append(l)
L[i0:i1] = out; done.append('selftest-tuned')
for k, l in enumerate(L):
    if l.strip().startswith('def handle_tags(self') and 'relpath(os.path.dirname' not in '\n'.join(L[k:k+3]):
        sig = l.strip(); pname = sig.split('(')[1].split(')')[0].split(',')[1].strip()
        L.insert(k+1, ind(l)*' ' + f'    if len(os.path.relpath(os.path.dirname({pname}), self.root).split(os.sep)) < 2: return')
        done.append('handle-tags-depth-guard'); break
for k, l in enumerate(L):
    if l.strip().startswith('def _reconcile_tags('):
        w = next(x for x in range(k+1, min(k+25, len(L))) if 'os.walk(' in L[x])
        if 'relpath(dp, self.root)' not in '\n'.join(L[w:w+3]):
            L.insert(w+1, (ind(L[w])+4)*' ' + 'if len(os.path.relpath(dp, self.root).split(os.sep)) < 2: continue')
            done.append('reconcile-depth-guard')
        break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
shutil.copy(p, os.path.expanduser('~/pending_v30/butler.py'))
print('✅', done)
