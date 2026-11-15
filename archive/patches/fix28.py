import ast, subprocess

# ========== briefing.py: collect() uses _tags_of() (no manual setup) ==========
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
            '    data = {k: [] for k, _, _ in TAGS}',
            '    tag_keys = {k.lower().replace(" ", "_") for k, _, _ in TAGS}',
            '    tag_by_key = {k.lower().replace(" ", "_"): k for k, _, _ in TAGS}',
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
            '                if tk in tag_keys:',
            '                    named_tag = tk',
            '                    break',
            '            # Determine section: named tag wins, else folder',
            '            section_key = None',
            '            if named_tag:',
            '                section_key = named_tag',
            '            else:',
            '                # Fall back to folder',
            '                rel = os.path.relpath(dp, root)',
            '                if rel != ".":',
            '                    top = rel.split(os.sep)[0].lower().replace(" ", "_")',
            '                    if top in tag_keys:',
            '                        section_key = top',
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
        print('briefing: collect() fixed (uses _tags_of, no setup)')
        break

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# ========== butler.py: reconcile uses _tags_of too ==========
p = 'butler.py'; L = open(p).read().split('\n')

for i, l in enumerate(L):
    if 'def _reconcile_tags(self, say):' in l:
        j = i + 1
        while j < len(L) and (not L[j].strip() or len(L[j]) - len(L[j].lstrip()) > len(l) - len(l.lstrip())):
            j += 1
        d = len(l) - len(l.lstrip())
        new_func = [
            'def _reconcile_tags(self, say):',
            '    """Move files to folders matching their named tags. Auto-creates folders."""',
            '    if not hasattr(self, \'root\'): return',
            '    for dp, dn, fn in os.walk(self.root):',
            '        dn[:] = [d for d in dn if not d.startswith(".")]',
            '        for f in fn:',
            '            if not f.lower().endswith(".pdf"): continue',
            '            fp = os.path.join(dp, f)',
            '            # Read tags',
            '            finder_tags = []',
            '            try: finder_tags = get_tags(fp)',
            '            except: pass',
            '            # Find named tag',
            '            named = [t for t in finder_tags if t in TAG_NAMES]',
            '            if not named: continue',
            '            tag = named[0]',
            '            safe_tag = re.sub(r\'[\\\\/:*?"<>|]\', \'\', tag).strip()',
            '            if not safe_tag: continue',
            '            current = os.path.basename(dp)',
            '            if current.lower().replace(" ", "_") == safe_tag.lower().replace(" ", "_"): continue',
            '            target_folder = os.path.join(self.root, safe_tag)',
            '            if not os.path.exists(target_folder):',
            '                os.makedirs(target_folder)',
            '            target_path = os.path.join(target_folder, f)',
            '            try:',
            '                os.rename(fp, target_path)',
            '                say(f"📁 [reconcile] {f} -> {safe_tag}/")',
            '            except Exception as e:',
            '                say(f"️ [reconcile] failed: {e}")',
        ]
        L[i:j] = new_func
        print('butler: _reconcile_tags fixed (named tags only, auto-creates folders)')
        break

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# Test
r = subprocess.run(['cv_env/bin/python3', '-c', 'import briefing, butler; print("IMPORT OK")'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
