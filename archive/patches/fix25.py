import ast, subprocess

# ========== briefing.py: robust collect() ==========
p = 'briefing.py'; L = open(p).read().split('\n')

i = next((k for k, l in enumerate(L) if l.startswith('def collect(root):')), None)
j = next((k for k in range(i+1, len(L)) if L[k].startswith('def ')), len(L)) if i else None

if i and j:
    new_collect = [
        'def collect(root):',
        '    """Collect candidates. Priority: Finder tags > folder name."""',
        '    data = {k: [] for k, _, _ in TAGS}',
        '    folder_to_tag = {k.replace(" ", "_").lower(): k for k, _, _ in TAGS}',
        '    for item in os.listdir(root):',
        '        folder_path = os.path.join(root, item)',
        '        if not os.path.isdir(folder_path): continue',
        '        folder_key = item.lower().replace(" ", "_")',
        '        if folder_key not in folder_to_tag: continue',
        '        tag_key = folder_to_tag[folder_key]',
        '        for f in os.listdir(folder_path):',
        '            if not f.lower().endswith(".pdf"): continue',
        '            fp = os.path.join(folder_path, f)',
        '            # Check if file has Finder tags that override folder',
        '            actual_tags = []',
        '            try: actual_tags = _tags_of(fp)',
        '            except: pass',
        '            if actual_tags:',
        '                # Use tags instead of folder',
        '                for t in actual_tags:',
        '                    tk = t.lower().replace(" ", "_")',
        '                    if tk in data:',
        '                        pos = _pos_for(fp, root)',
        "                        ph = ''",
        '                        try:',
        "                            ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]",
        "                            ph = (ps or [''])[0] if isinstance(ps, list) else ps",
        '                        except: ph = phone_of(fp)',
        '                        data[tk].append([os.path.splitext(f)[0], pos, ph])',
        '            else:',
        '                # No tags, use folder',
        '                pos = _pos_for(fp, root)',
        "                ph = ''",
        '                try:',
        "                    ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]",
        "                    ph = (ps or [''])[0] if isinstance(ps, list) else ps",
        '                except: ph = phone_of(fp)',
        '                data[tag_key].append([os.path.splitext(f)[0], pos, ph])',
        '    return data',
    ]
    L[i:j] = new_collect
    print('briefing: collect() rewritten')

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# ========== butler.py: robust handle_tags() ==========
p = 'butler.py'; L = open(p).read().split('\n')

# Find handle_tags and make it actually move files
for i, l in enumerate(L):
    if 'def handle_tags(self, p, say):' in l:
        # Find the end of the function
        j = i + 1
        while j < len(L) and (not L[j].strip() or len(L[j]) - len(L[j].lstrip()) > len(l) - len(l.lstrip())):
            j += 1
        # Replace with robust version
        new_func = [
            'def handle_tags(self, p, say):',
            '    """Move file to folder matching its tags. Create folder if needed."""',
            '    T = get_tags(p)',
            '    named = [t for t in T if t in TAG_NAMES]',
            '    if not named: return',
            '    tag = named[0]',
            '    # Sanitize tag name for folder',
            '    safe_tag = re.sub(r\'[\\\\/:*?"<>|]\', \'\', tag).strip()',
            '    if not safe_tag: return',
            '    # Create target folder',
            '    target_folder = os.path.join(os.path.dirname(p), safe_tag)',
            '    if not os.path.exists(target_folder):',
            '        os.makedirs(target_folder)',
            '        say(f"📁 [created] {safe_tag}/")',
            '    # Move file',
            '    target_path = os.path.join(target_folder, os.path.basename(p))',
            '    if os.path.abspath(p) != os.path.abspath(target_path):',
            '        try:',
            '            os.rename(p, target_path)',
            '            say(f"📁 [move] {os.path.basename(p)} -> {safe_tag}/")',
            '        except Exception as e:',
            '            say(f"️ [move] failed: {e}")',
        ]
        L[i:j] = new_func
        print('butler: handle_tags() rewritten')
        break

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# Test
r = subprocess.run(['cv_env/bin/python3', '-c', 'import briefing, butler; print("IMPORT OK")'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
