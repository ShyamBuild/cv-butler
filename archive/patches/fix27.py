import ast, subprocess

# ========== butler.py: fix reconcile to handle color tags ==========
p = 'butler.py'; L = open(p).read().split('\n')

# Find and replace _reconcile_tags with color-aware version
for i, l in enumerate(L):
    if 'def _reconcile_tags(self, say):' in l:
        j = i + 1
        while j < len(L) and (not L[j].strip() or len(L[j]) - len(L[j].lstrip()) > len(l) - len(l.lstrip())):
            j += 1
        d = len(l) - len(l.lstrip())
        new_func = [
            'def _reconcile_tags(self, say):',
            '    """Move files to folders matching their tags (named or color)."""',
            '    if not hasattr(self, \'root\'): return',
            '    # Load color map',
            '    cmap = {}',
            '    try: cmap = json.load(open(os.path.join(BASE_DIR, \'color_tags.json\')))',
            '    except: pass',
            '    for dp, dn, fn in os.walk(self.root):',
            '        dn[:] = [d for d in dn if not d.startswith(".")]',
            '        for f in fn:',
            '            if not f.lower().endswith(".pdf"): continue',
            '            fp = os.path.join(dp, f)',
            '            T = get_tags(fp)',
            '            if not T: continue',
            '            # Try named tags first',
            '            named = [t for t in T if t in TAG_NAMES]',
            '            if named:',
            '                tag = named[0]',
            '            else:',
            '                # Color-only: use color map',
            '                color = T[0] if T else None',
            '                tag = cmap.get(color) if color else None',
            '            if not tag: continue',
            '            safe_tag = re.sub(r\'[\\\\/:*?"<>|]\', \'\', tag).strip()',
            '            if not safe_tag: continue',
            '            current_folder = os.path.basename(dp)',
            '            if current_folder.lower().replace(" ", "_") == safe_tag.lower().replace(" ", "_"): continue',
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
        print('replaced _reconcile_tags with color-aware version')
        break

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# ========== briefing.py: fix collect to read tags, not folders ==========
p = 'briefing.py'; L = open(p).read().split('\n')

for i, l in enumerate(L):
    if 'def collect(root):' in l:
        j = i + 1
        while j < len(L) and not L[j].strip().startswith('def '):
            j += 1
        d = len(l) - len(l.lstrip())
        new_collect = [
            'def collect(root):',
            '    """Collect candidates based on actual tags (named or color)."""',
            '    data = {k: [] for k, _, _ in TAGS}',
            '    cmap = {}',
            '    try: cmap = json.load(open(os.path.join(BASE_DIR, \'color_tags.json\')))',
            '    except: pass',
            '    for dp, dn, fn in os.walk(root):',
            '        dn[:] = [d for d in dn if not d.startswith(".")]',
            '        for f in fn:',
            '            if not f.lower().endswith(".pdf"): continue',
            '            fp = os.path.join(dp, f)',
            '            T = get_tags(fp)',
            '            if not T: continue',
            '            named = [t for t in T if t in TAG_NAMES]',
            '            if named:',
            '                tag = named[0]',
            '            else:',
            '                color = T[0] if T else None',
            '                tag = cmap.get(color) if color else None',
            '            if not tag: continue',
            '            tag_key = tag.lower().replace(" ", "_")',
            '            if tag_key not in data: continue',
            '            pos = _pos_for(fp, root)',
            "            ph = ''",
            '            try:',
            "                ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]",
            "                ph = (ps or [''])[0] if isinstance(ps, list) else ps",
            '            except: ph = phone_of(fp)',
            '            data[tag_key].append([os.path.splitext(f)[0], pos, ph])',
            '    return data',
        ]
        L[i:j] = new_collect
        print('replaced collect() with tag-based version')
        break

new = '\n'.join(L)
ast.parse(new)
open(p, 'w').write(new)

# Test
r = subprocess.run(['cv_env/bin/python3', '-c', 'import briefing, butler; print("IMPORT OK")'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
