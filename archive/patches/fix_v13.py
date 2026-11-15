import ast, subprocess
p = 'butler.py'; L = open(p).read().split('\n'); done = []
for i, l in enumerate(L):
    if l.strip() == "if not getattr(self, '_skip_tags', False): self.handle_tags(p, say)" and i > 0 and L[i-1].strip() == 'self.handle_excel(p, say)':
        if i+1 >= len(L) or '_compact_numbers' not in L[i+1]:
            d = len(l) - len(l.lstrip())
            L.insert(i+1, d*' ' + 'self._compact_numbers(os.path.dirname(p), say)')
            done.append('xlsx-route-compacts')
        break
if not any(l.strip().startswith('def _git_stamp(') for l in L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('VERSION ='))
    d = len(L[i]) - len(L[i].lstrip())
    L[i+1:i+1] = [d*' ' + 'def _git_stamp():',
                  d*' ' + '    try:',
                  d*' ' + "        r = subprocess.run(['git', '-C', BASE_DIR, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, timeout=5)",
                  d*' ' + "        return (r.stdout or '').strip() or 'nogit'",
                  d*' ' + '    except Exception:',
                  d*' ' + "        return 'nogit'",
                  d*' ' + 'GIT_STAMP = _git_stamp()',
                  '']
    done.append('git-stamp')
for i, l in enumerate(L):
    if '🤖✨ {VERSION}' in l and 'GIT_STAMP' not in l:
        L[i] = l.replace('{VERSION}', '{VERSION} · git {GIT_STAMP}')
        done.append('banner-stamped'); break
for i, l in enumerate(L):
    if l.strip().startswith('print(f"💓 sweep #{n}') and i+1 < len(L) and '_git_stamp()' not in L[i+1]:
        d = len(l) - len(l.lstrip())
        L[i+1:i+1] = [d*' ' + 'if _git_stamp() != GIT_STAMP:',
                      d*' ' + '    print(f"⚠️ newer committed code exists (git {_git_stamp()}) - type  restart  to run the latest proven version")']
        done.append('staleness-nag'); break
for i, l in enumerate(L):
    if l.strip() == "if not pages: pages = _mdfind_app('com.apple.iWork.Pages')":
        d = len(l) - len(l.lstrip())
        L[i+1:i+1] = [d*' ' + 'if not pages:',
                      d*' ' + '    try:',
                      d*' ' + "        r = subprocess.run(['osascript', '-e', 'POSIX path of (path to application \"Pages\")'], capture_output=True, text=True, timeout=10)",
                      d*' ' + "        cand = (r.stdout or '').strip().rstrip('/')",
                      d*' ' + '        if r.returncode == 0 and cand and os.path.isdir(cand): pages = cand',
                      d*' ' + '    except Exception:',
                      d*' ' + '        pass']
        done.append('pages-detection-hardened'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
r = subprocess.run(['cv_env/bin/python3', '-c', 'import butler; print("IMPORT OK", butler.GIT_STAMP)'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
