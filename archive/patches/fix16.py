import ast
p = 'briefing.py'; L = open(p).read().split('\n'); done = []

# Find and replace collect() with a version that reads BOTH folders and Finder tags
i = next((k for k, l in enumerate(L) if l.startswith('def collect(root):')), None)
j = next((k for k in range(i+1, len(L)) if L[k].startswith('def ')), len(L)) if i else None

if i is not None and j is not None:
    new_collect = '''def collect(root):
    """Collect candidates into TAGS sections. A file belongs to a section if:
       (a) it sits inside a tag-named folder, OR
       (b) it has a matching Finder tag."""
    data = {k: [] for k, _, _ in TAGS}
    tag_keys = {k.lower().replace('\\u2013', '-') for k, _, _ in TAGS}
    tag_by_key = {k.lower().replace('\\u2013', '-'): k for k, _, _ in TAGS}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith('.')]
        for f in fn:
            if not f.lower().endswith('.pdf') or f.startswith('.'): continue
            fp = os.path.join(dp, f)
            # (a) folder-based: which tag-folder is this file in?
            rel = os.path.relpath(dp, root)
            folder_tag = None
            if rel and rel != '.':
                top_folder = rel.split(os.sep)[0].lower().replace('\\u2013', '-')
                if top_folder in tag_keys:
                    folder_tag = tag_by_key[top_folder]
            # (b) Finder-tag-based
            finder_tags = []
            try:
                finder_tags = _tags_of(fp)
            except Exception:
                pass
            finder_keys = {t.lower().replace('\\u2013', '-') for t in finder_tags}
            # Combine both sources
            matched_keys = set()
            if folder_tag:
                matched_keys.add(folder_tag.lower().replace('\\u2013', '-'))
            matched_keys.update(finder_keys & tag_keys)
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
    done.append('collect-folder+tag')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('briefing:', done or 'nothing missing')

# Verify
import subprocess
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import briefing, os
root = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
if os.path.isdir(root):
    data = briefing.collect(root)
    total = sum(len(v) for v in data.values())
    print(f"Total candidates: {total}")
    for k, v in data.items():
        if v:
            title = next((t for kk, t, _ in briefing.TAGS if kk == k), k)
            print(f"  {title}: {len(v)}")
else:
    print(f"root not found: {root}")
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
