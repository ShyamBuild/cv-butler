import ast, subprocess

# ========== briefing.py: collect() reads TAGS, not folders ==========
p = 'briefing.py'; L = open(p).read().split('\n'); done = []

# Find collect() and replace it with tag-based version
i = next((k for k, l in enumerate(L) if l.startswith('def collect(root):')), None)
j = next((k for k in range(i+1, len(L)) if L[k].startswith('def ')), len(L)) if i else None

if i and j:
    new_collect = '''def collect(root):
    """Collect candidates into TAGS sections based on Finder tags."""
    data = {k: [] for k, _, _ in TAGS}
    tag_keys = {k.lower().replace('\\u2013', '-').replace(' ', '_') for k, _, _ in TAGS}
    tag_by_key = {k.lower().replace('\\u2013', '-').replace(' ', '_'): k for k, _, _ in TAGS}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith('.')]
        for f in fn:
            if not f.lower().endswith('.pdf') or f.startswith('.'): continue
            fp = os.path.join(dp, f)
            # Read Finder tags
            finder_tags = []
            try:
                finder_tags = _tags_of(fp)
            except Exception:
                pass
            finder_keys = {t.lower().replace('\\u2013', '-').replace(' ', '_') for t in finder_tags}
            matched_keys = finder_keys & tag_keys
            if not matched_keys:
                continue
            pos = _pos_for(fp, root)
            ph = ''
            try:
                ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]
                ph = (ps or [''])[0] if isinstance(ps, list) else ps
            except Exception:
                try: ph = phone_of(fp)
                except Exception: pass
            for k in matched_keys:
                if k in data:
                    data[k].append([os.path.splitext(f)[0], pos, ph])
    return data
'''
    L[i:j] = new_collect.split('\n')
    done.append('collect-tag-based')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('briefing:', done)

# ========== butler.py: handle_tags() moves files based on tags ==========
p = 'butler.py'; L = open(p).read().split('\n'); done = []

# Find handle_tags and ensure it moves files based on tags
# Look for the function that processes tags
for i, l in enumerate(L):
    if 'def handle_tags(self, p, say):' in l:
        # Check if it already has the move logic
        # Find the end of the function
        j = i + 1
        while j < len(L) and (not L[j].strip() or len(L[j]) - len(L[j].lstrip()) > len(l) - len(l.lstrip())):
            j += 1
        # Check if it has the move logic
        func_body = '\n'.join(L[i:j])
        if 'os.rename' not in func_body and 'shutil.move' not in func_body:
            # Add move logic after tag detection
            # Find where tag is determined
            for k in range(i, j):
                if 'tag =' in L[k] and 'return' not in L[k]:
                    d = len(L[k]) - len(L[k].lstrip())
                    # Insert move logic after this line
                    move_code = [
                        d*' ' + 'if tag:',
                        d*' ' + '    target_folder = os.path.join(os.path.dirname(p), tag)',
                        d*' ' + '    if not os.path.exists(target_folder):',
                        d*' ' + '        os.makedirs(target_folder)',
                        d*' ' + '    target_path = os.path.join(target_folder, os.path.basename(p))',
                        d*' ' + '    if os.path.abspath(p) != os.path.abspath(target_path):',
                        d*' ' + '        try:',
                        d*' ' + '            os.rename(p, target_path)',
                        d*' ' + '            say(f"📁 [move] {os.path.basename(p)} -> {tag}/{os.path.basename(p)}")',
                        d*' ' + '        except Exception as e:',
                        d*' ' + '            say(f"️ [move] failed: {e}")',
                    ]
                    L[k+1:k+1] = move_code
                    done.append('handle_tags-moves')
                    break
        break

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('butler:', done)

# Import test
r = subprocess.run(['cv_env/bin/python3', '-c', 'import briefing, butler; print("IMPORT OK")'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
