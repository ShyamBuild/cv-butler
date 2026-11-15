import ast, subprocess

p = 'briefing.py'; L = open(p).read().split('\n')

for i, l in enumerate(L):
    if 'def collect(root):' in l:
        j = i + 1
        while j < len(L) and not L[j].strip().startswith('def '):
            j += 1
        d = len(l) - len(l.lstrip())
        new_collect = [
            'def collect(root):',
            '    """Collect candidates. Named tags override folders. No setup needed."""',
            '    # Build normalized key -> original key mapping',
            '    norm_to_orig = {k.lower().replace(" ", "_"): k for k, _, _ in TAGS}',
            '    data = {k: [] for k, _, _ in TAGS}',
            '    for dp, dn, fn in os.walk(root):',
            '        dn[:] = [d for d in dn if not d.startswith(".")]',
            '        for f in fn:',
            '            if not f.lower().endswith(".pdf"): continue',
            '            fp = os.path.join(dp, f)',
            '            # Read Finder tags',
            '            finder_tags = []',
            '            try: finder_tags = _tags_of(fp)',
            '            except: pass',
            '            # Find named tag (if any)',
            '            named_tag = None',
            '            for t in finder_tags:',
            '                tk = t.lower().replace(" ", "_")',
            '                if tk in norm_to_orig:',
            '                    named_tag = tk',
            '                    break',
            '            # Determine section: named tag wins, else folder',
            '            section_key = None',
            '            if named_tag:',
            '                section_key = norm_to_orig.get(named_tag)',
            '            else:',
            '                # Fall back to folder',
            '                rel = os.path.relpath(dp, root)',
            '                if rel != ".":',
            '                    top = rel.split(os.sep)[0].lower().replace(" ", "_")',
            '                    if top in norm_to_orig:',
            '                        section_key = norm_to_orig.get(top)',
            '            if not section_key or section_key not in data: continue',
            '            pos = _pos_for(fp, root)',
            "            ph = ''",
            '            try:',
            "                ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]",
            "                ph = (ps or [''])[0] if isinstance(ps, list) else ps",
            '            except: ph = phone_of(fp)',
            '            data[section_key].append([os.path.splitext(f)[0], pos, ph])',
            '    return data',
        ]
        L[i:j] = new_collect
        print('briefing: collect() fixed with norm_to_orig mapping')
        break

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
