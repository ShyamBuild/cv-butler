import ast, subprocess
DASH = '.replace("\\u2013", "-")'

# ========== briefing.py: en-dash-safe collect ==========
p = 'briefing.py'; L = open(p).read().split('\n')
for i, l in enumerate(L):
    if 'folder_to_tag[k.lower().replace(" ", "_")] = k' in l:
        L[i] = '        folder_to_tag[k.lower()' + DASH + '.replace(" ", "_")] = k'
        print('briefing: folder_to_tag en-dash safe')
    if 'named = [t for t in finder_tags if t.lower().replace(" ", "_") in folder_to_tag]' in l:
        L[i] = '            named = [t for t in finder_tags if t.lower()' + DASH + '.replace(" ", "_") in folder_to_tag]'
        print('briefing: named-match en-dash safe')
    if 'tag_key = named[0].lower().replace(" ", "_")' in l:
        L[i] = '                tag_key = named[0].lower()' + DASH + '.replace(" ", "_")'
        print('briefing: tag_key en-dash safe')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)

# ========== butler.py: en-dash-safe reconcile + run every sweep ==========
p = 'butler.py'; L = open(p).read().split('\n')
for i, l in enumerate(L):
    if 'named = [t for t in finder_tags if t in TAG_NAMES]' in l or 'named = [t for t in T if t in TAG_NAMES]' in l:
        d = len(l) - len(l.lstrip())
        L[i] = d*' ' + 'named = [t for t in (finder_tags if "finder_tags" in dir() else T) if t' + DASH + ' in TAG_NAMES or t in TAG_NAMES]'
        print('butler: named-match en-dash safe')
    if 'current.lower().replace(" ", "_") == safe_tag.lower().replace(" ", "_")' in l:
        d = len(l) - len(l.lstrip())
        L[i] = d*' ' + 'if current.lower()' + DASH + '.replace(" ", "_") == safe_tag.lower()' + DASH + '.replace(" ", "_"): continue'
        print('butler: folder-compare en-dash safe')

# Force reconcile on every heartbeat sweep
added = False
for i, l in enumerate(L):
    if 'sweep #' in l and ('print' in l or 'say' in l) and '_reconcile_tags' not in L[i+1] if i+1 < len(L) else True:
        d = len(l) - len(l.lstrip())
        L.insert(i+1, d*' ' + 'try: self._reconcile_tags(print)' if 'self' in l else d*' ' + 'try: B._reconcile_tags(print)')
        L.insert(i+2, (d)*' ' + 'except Exception: pass')
        added = True
        print('butler: reconcile runs every sweep')
        break
if not added:
    print('butler: WARNING sweep anchor not found')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)

r = subprocess.run(['cv_env/bin/python3', '-c', 'import briefing, butler; print("IMPORT OK")'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
