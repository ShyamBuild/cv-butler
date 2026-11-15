import ast, subprocess

p = 'briefing.py'; L = open(p).read().split('\n')

# Find collect() and replace with minimal working version
i = next((k for k, l in enumerate(L) if l.startswith('def collect(root):')), None)
j = next((k for k in range(i+1, len(L)) if L[k].startswith('def ')), len(L)) if i else None

if i and j:
    new_collect = [
        'def collect(root):',
        '    """Collect candidates into TAGS sections based on folder membership."""',
        '    data = {k: [] for k, _, _ in TAGS}',
        '    # Build folder name to tag key mapping',
        '    folder_to_tag = {}',
        '    for k, _, _ in TAGS:',
        '        folder_name = k.replace(" ", "_").lower()',
        '        folder_to_tag[folder_name] = k',
        '    # Walk root and collect files from tag folders',
        '    for item in os.listdir(root):',
        '        folder_path = os.path.join(root, item)',
        '        if not os.path.isdir(folder_path): continue',
        '        folder_key = item.lower().replace(" ", "_")',
        '        if folder_key not in folder_to_tag: continue',
        '        tag_key = folder_to_tag[folder_key]',
        '        for f in os.listdir(folder_path):',
        '            if not f.lower().endswith(".pdf"): continue',
        '            fp = os.path.join(folder_path, f)',
        '            pos = _pos_for(fp, root)',
        "            ph = ''",
        '            try:',
        "                ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]",
        "                ph = (ps or [''])[0] if isinstance(ps, list) else ps",
        '            except Exception:',
        '                try: ph = phone_of(fp)',
        '                except Exception: pass',
        '            data[tag_key].append([os.path.splitext(f)[0], pos, ph])',
        '    return data',
    ]
    L[i:j] = new_collect
    print('replaced collect() with minimal version')

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# Test
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import briefing, os
root = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
data = briefing.collect(root)
total = sum(len(v) for v in data.values())
print(f"Total candidates: {total}")
for k, v in data.items():
    if v:
        title = next((t for kk, t, _ in briefing.TAGS if kk == k), k)
        print(f"  {title}: {len(v)}")
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
