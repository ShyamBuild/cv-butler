import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if 'def _snapshot(self' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _heal(self, say=print):'))
    B[i:i] = ["    def _snapshot(self, say=print):  # SNAPSHOT v69",
              "        import subprocess, datetime, glob",
              "        ic = os.path.expanduser('~/Library/Mobile Documents/com~apple~CloudDocs')",
              "        if not os.path.isdir(ic): return",
              "        now = datetime.date.today()",
              "        mind = os.path.join(ic, f'cv-memory-week-{now.isocalendar()[0]}-{now.isocalendar()[1]}.tgz')",
              "        if now.weekday() == 6 and not os.path.exists(mind):",
              "            subprocess.run(['tar', '-czf', mind, '--exclude=wa_profile', '--exclude=__pycache__', '--exclude=download_debris', '--exclude=cv_env', '--exclude=archive', '-C', os.path.expanduser('~'), 'CV_Tool', '-C', os.path.join(self.root), 'stage_log.json'], capture_output=True)",
              "            say(f'☁️ weekly mind snapshot: {os.path.basename(mind)}')",
              "        tree = os.path.join(ic, f'cv-tree-{now.strftime(\"%Y-%m\")}.tgz')",
              "        if now.day == 1 and not os.path.exists(tree):",
              "            subprocess.run(['tar', '-czf', tree, '-C', os.path.dirname(self.root), os.path.basename(self.root)], capture_output=True)",
              "            say(f'☁️ monthly tree snapshot: {os.path.basename(tree)}')",
              "        for pat in ('cv-memory-week-*.tgz', 'cv-tree-*.tgz'):",
              "            old = sorted(glob.glob(os.path.join(ic, pat)))[:-4]",
              "            for o in old:",
              "                try: os.remove(o)",
              "                except Exception: pass",
              ""]
    done.append('snapshot-method')
src = '\n'.join(B)
if 'B._snapshot(' not in src:
    i = next(k for k, l in enumerate(B) if 'B._heal(hsay)' in l or 'B._heal((lambda' in l)
    B.insert(i+1, ind(B[i])*' ' + 'B._snapshot(hsay)')
    done.append('snapshot-wired')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S86 cloud snapshot habit" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S85 cadence never queues twins" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S86 cloud snapshot habit', (chr(35)+' SNAPSHOT') in _src and 'B._snapshot(' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S86-guard')
print('✅', done)
