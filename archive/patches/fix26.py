import ast, subprocess

# ========== butler.py: add tag reconciliation ==========
p = 'butler.py'; L = open(p).read().split('\n')

# Find the sweep method and add tag reconciliation
for i, l in enumerate(L):
    if 'def _sweep(self):' in l or 'def sweep(self):' in l:
        # Find where to insert reconciliation (after file processing)
        j = i + 1
        while j < len(L) and not L[j].strip().startswith('def '):
            j += 1
        # Insert reconciliation before the next method
        d = len(L[i]) - len(L[i].lstrip())
        reconcile = [
            '',
            d*' ' + 'def _reconcile_tags(self, say):',
            d*' ' + '    """Move files to folders matching their tags."""',
            d*' ' + '    if not hasattr(self, \'root\'): return',
            d*' ' + '    for dp, dn, fn in os.walk(self.root):',
            d*' ' + '        dn[:] = [d for d in dn if not d.startswith(".")]',
            d*' ' + '        for f in fn:',
            d*' ' + '            if not f.lower().endswith(".pdf"): continue',
            d*' ' + '            fp = os.path.join(dp, f)',
            d*' ' + '            T = get_tags(fp)',
            d*' ' + '            named = [t for t in T if t in TAG_NAMES]',
            d*' ' + '            if not named: continue',
            d*' ' + '            tag = named[0]',
            d*' ' + '            safe_tag = re.sub(r\'[\\\\/:*?"<>|]\', \'\', tag).strip()',
            d*' ' + '            if not safe_tag: continue',
            d*' ' + '            current_folder = os.path.basename(dp)',
            d*' ' + '            if current_folder.lower().replace(" ", "_") == safe_tag.lower().replace(" ", "_"): continue',
            d*' ' + '            target_folder = os.path.join(self.root, safe_tag)',
            d*' ' + '            if not os.path.exists(target_folder):',
            d*' ' + '                os.makedirs(target_folder)',
            d*' ' + '            target_path = os.path.join(target_folder, f)',
            d*' ' + '            try:',
            d*' ' + '                os.rename(fp, target_path)',
            d*' ' + '                say(f"📁 [reconcile] {f} -> {safe_tag}/")',
            d*' ' + '            except Exception as e:',
            d*' ' + '                say(f"️ [reconcile] failed: {e}")',
            '',
        ]
        L[j:j] = reconcile
        print('added _reconcile_tags()')
        break

# Find where sweep calls other methods and add reconcile call
for i, l in enumerate(L):
    if 'self._archive_source' in l or 'self.normalize_suffix' in l:
        d = len(l) - len(l.lstrip())
        # Add reconcile call after archive/normalize
        L.insert(i+1, d*' ' + 'self._reconcile_tags(say)')
        print('added reconcile call to sweep')
        break

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# Test
r = subprocess.run(['cv_env/bin/python3', '-c', 'import butler; print("IMPORT OK")'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
