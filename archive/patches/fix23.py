import ast, subprocess

p = 'briefing.py'; L = open(p).read().split('\n')

# Find collect() and replace with debug version
i = next((k for k, l in enumerate(L) if l.startswith('def collect(root):')), None)
j = next((k for k in range(i+1, len(L)) if L[k].startswith('def ')), len(L)) if i else None

if i and j:
    new_collect = [
        'def collect(root):',
        '    """Collect candidates into TAGS sections based on folder membership."""',
        '    import sys',
        '    data = {k: [] for k, _, _ in TAGS}',
        '    # Build normalized tag keys',
        '    tag_keys = set()',
        '    for k, _, _ in TAGS:',
        '        nk = k.lower().replace(" ", "_")',
        '        tag_keys.add(nk)',
        '    print(f"DEBUG: tag_keys = {tag_keys}", file=sys.stderr)',
        '    for dp, dn, fn in os.walk(root):',
        '        dn[:] = [d for d in dn if not d.startswith(".")]',
        '        for f in fn:',
        '            if not f.lower().endswith(".pdf") or f.startswith("."): continue',
        '            fp = os.path.join(dp, f)',
        '            rel = os.path.relpath(dp, root)',
        '            if rel == ".": continue',
        '            top_folder = rel.split(os.sep)[0].lower().replace(" ", "_")',
        '            print(f"DEBUG: file={f}, folder={top_folder}", file=sys.stderr)',
        '            if top_folder not in tag_keys:',
        '                print(f"DEBUG:   no match for {top_folder}", file=sys.stderr)',
        '                continue',
        '            tag_key = top_folder',
        '            if tag_key not in data: continue',
        '            pos = _pos_for(fp, root)',
        "            ph = ''",
        '            try:',
        "                ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]",
        "                ph = (ps or [''])[0] if isinstance(ps, list) else ps",
        '            except Exception:',
        '                try: ph = phone_of(fp)',
        '                except Exception: pass',
        '            data[tag_key].append([os.path.splitext(f)[0], pos, ph])',
        '            print(f"DEBUG:   added to {tag_key}", file=sys.stderr)',
        '    return data',
    ]
    L[i:j] = new_collect
    print('replaced collect() with debug version')

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# Test with stderr visible
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import briefing, os, sys
root = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"
data = briefing.collect(root)
total = sum(len(v) for v in data.values())
print(f"Total candidates: {total}")
for k, v in data.items():
    if v:
        title = next((t for kk, t, _ in briefing.TAGS if kk == k), k)
        print(f"  {title}: {len(v)}")
'''], capture_output=True, text=True)
print("STDOUT:", r.stdout.strip())
print("STDERR:", r.stderr.strip()[:500])
