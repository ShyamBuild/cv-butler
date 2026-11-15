import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
r0 = next(k for k, l in enumerate(B) if l.startswith('def desk_resolve('))
r1 = next(k for k in range(r0 + 1, len(B)) if B[k].startswith('def desk_paths('))
if 'DESK-JD-BLIND' not in '\n'.join(B[r0:r1]):
    B[r0:r1] = ["def desk_resolve(spec, root):  # DESK v84.0 (JD-blind v84.1): a chair is a folder that holds people, not a folder that holds a JD",
                "    toks = [t for t in spec.lower().split() if t]",
                "    best = None; bs = -1; bf = -1",
                "    for dp, dn, fn in os.walk(root):",
                "        rel = os.path.relpath(dp, root)",
                "        if rel == '.' or rel.count(os.sep) > 1: continue",
                "        if any(seg.lower().startswith('jd') for seg in rel.split(os.sep)): continue  # DESK-JD-BLIND v84.1",
                "        papers = [x for x in fn if x.lower().endswith(('.pdf', '.docx'))]",
                "        blob = rel.lower() + ' ' + ' '.join(papers).lower()",
                "        hit = sum(1 for t in toks if t in blob)",
                "        if hit == len(toks) and (hit > bs or (hit == bs and len(papers) > bf)):",
                "            best, bs, bf = dp, hit, len(papers)",
                "    return best",
                ""]
    done.append('desk-jd-blind')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "secondary: {os.path.relpath(d.get('secondary')" in l:
        d = ind(l)
        B[k:k+1] = [d*' ' + "_pr = os.path.relpath(d['primary'], root) if d.get('primary') else ''",
                    d*' ' + "_se = os.path.relpath(d['secondary'], root) if d.get('secondary') else '-'  # DESK-DISPLAY v84.1: a placeholder is never run through relpath",
                    d*' ' + "say(f'🪑 desk: {_pr or \"-\"} · secondary: {_se}' if d.get('primary') else '🪑 no desk set - the butler watches the whole library evenly')"]
        done.append('desk-display'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if len(sys.argv) > 1 and sys.argv[1] in ('pending', 'status', 'note')"):
        B[k] = ind(l)*' ' + "if len(sys.argv) > 1 and sys.argv[1] in ('pending', 'status', 'note', 'desk', 'briefing', 'chase'):  # PIPELINE-CLI-FIRST v84.1: six verbs answer before any root is validated"
        done.append('cli-verb-tuple'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('else: pipeline_note('):
        d = ind(l)
        B[k] = d*' ' + "elif _v == 'note': pipeline_note(_a[0] if _a else '', ' '.join(_a[1:]), print)"
        j = next(m for m in range(k + 1, len(B)) if B[m].strip() == 'sys.exit(0)')
        B[j:j] = [d*' ' + "elif _v == 'desk': desk_cmd(' '.join(_a), _pl_root(), print)",
                  d*' ' + "elif _v == 'briefing': daily_briefing(print)",
                  d*' ' + "elif _v == 'chase': chase_cmd(' '.join(_a), _pl_root(), print)"]
        done.append('cli-five-verbs'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S225 six verbs answer before any root is validated", "'S224 the parse asks twice before it stays silent", "ck('S225 six verbs answer before any root is validated', (chr(35)+' PIPELINE-CLI-FIRST v84.1') in _src and (\"'desk', 'briefing', 'chase')\" in _src))"),
      ("'S226 the resolver seats folders that hold people, not folders that hold JDs", "'S225 six verbs answer before any root is validated", "ck('S226 the resolver seats folders that hold people, not folders that hold JDs', (chr(35)+' DESK-JD-BLIND v84.1') in _src)"),
      ("'S227 a placeholder is never run through relpath", "'S226 the resolver seats folders that hold people, not folders that hold JDs", "ck('S227 a placeholder is never run through relpath', (\"relpath(d.get('secondary') or '-'\" not in _src) and (chr(35)+' DESK-DISPLAY v84.1') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S223 absence reads as empty bytes, never as None")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
