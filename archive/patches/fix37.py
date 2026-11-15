import ast, subprocess
p = 'butler.py'; src = open(p).read(); L = src.split('\n')
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
direct = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
METHODS = {'route','_route','handle_tags','handle_pdf','handle_excel','handle_convert','normalize_suffix',
           '_rename','_check_siblings','_archive_source','_save_idx','position_folder_for','_jkey',
           '_jload','_jsave','_is_jd','_rename_jd','_llm_json','_load','_save'}
del_segs, move_nodes = [], []
def scan(nodes, in_cls):
    for n in nodes:
        if isinstance(n, ast.FunctionDef):
            args = [a.arg for a in n.args.args]
            if n.name in ('_unescape', 'get_tags', '_reconcile_tags') and not in_cls:
                del_segs.append((n.lineno, n.end_lineno)); continue
            if in_cls:
                scan(n.body, True); continue
            if args and args[0] == 'self' and n.name in METHODS:
                move_nodes.append(n)
            scan(n.body, False)
        elif isinstance(n, (ast.For, ast.While, ast.If, ast.With)):
            scan(getattr(n, 'body', []) + getattr(n, 'orelse', []), in_cls)
        elif isinstance(n, ast.Try):
            scan(n.body + n.handlers + n.orelse + n.finalbody, in_cls)
scan(tree.body, False)
for n in list(move_nodes):
    if any(s <= n.lineno <= e for s, e in del_segs):
        move_nodes.remove(n)
moved = []
for n in move_nodes:
    seg = L[n.lineno-1:n.end_lineno]
    base = min(len(l) - len(l.lstrip()) for l in seg if l.strip())
    moved.append('\n'.join(('    ' + l[base:]) if l.strip() else '' for l in seg))
for s, e in sorted(del_segs + [(n.lineno, n.end_lineno) for n in move_nodes], reverse=True):
    del L[s-1:e]
done = ['deleted %d bad/dup defs' % len(del_segs), 'moved %d stranded methods' % len(move_nodes)]

MOD_FUNCS = [
 'def _unescape(s):',
 '    BS = chr(92)',
 "    s = re.sub(BS + 'U([0-9a-fA-F]{4,8})', lambda m: chr(int(m.group(1), 16)), s)",
 "    s = re.sub(BS + 'u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)",
 "    s = s.replace(BS + '\"', '\"')",
 '    return s',
 'def get_tags(path):',
 '    try:',
 "        r = subprocess.run(['mdls', '-name', 'kMDItemUserTags', path], capture_output=True, text=True, timeout=15)",
 "        out = (r.stdout or '').strip()",
 "        if out and '(null)' not in out:",
 '            tags, lines, k = [], out.splitlines(), 0',
 '            while k < len(lines):',
 '                line = lines[k].strip()',
 "                if line.startswith('kMDItemUserTags'):",
 "                    rest = line.split('=', 1)[1].strip() if '=' in line else ''",
 "                    if rest == '(':",
 '                        k += 1',
 '                        while k < len(lines):',
 "                            item = lines[k].strip().rstrip(',')",
 "                            if item == ')': break",
 '                            if item.startswith(\'"\') and item.endswith(\'"\'): item = item[1:-1]',
 "                            nm = _unescape(item).split(chr(10))[0].strip()",
 '                            if nm and nm not in COLOR_TAGS: tags.append(nm)',
 '                            k += 1',
 '                k += 1',
 '            if tags: return tags',
 '    except Exception:',
 '        pass',
 '    return []',
 '']
i = next(k for k, l in enumerate(L) if l.strip() == 'class Butler:')
L[i:i] = MOD_FUNCS; done.append('canonical _unescape+get_tags')

NEW_METHODS = moved + [
 '    def handle_tags(self, p, say):',
 '        T = get_tags(p)',
 '        named = [t for t in T if t in TAG_NAMES or t.replace(chr(8211), "-") in TAG_NAMES]',
 '        if not named: return',
 '        tag = named[0]',
 '        safe_tag = re.sub(r\'[\\\\/:*?"<>|]\', \'\', tag).strip()',
 '        if not safe_tag: return',
 '        target_folder = os.path.join(self.position_folder_for(p), safe_tag)',
 '        if os.path.abspath(os.path.dirname(p)) == os.path.abspath(target_folder): return',
 '        os.makedirs(target_folder, exist_ok=True)',
 '        dst = os.path.join(target_folder, os.path.basename(p))',
 '        if os.path.exists(dst):',
 '            b, e = os.path.splitext(os.path.basename(p)); c = 1',
 '            while os.path.exists(dst): dst = os.path.join(target_folder, f"{b}_{c}{e}"); c += 1',
 '        os.rename(p, dst)',
 "        with self.lock: self.stats['moved'] += 1",
 '        say(f"\\U0001f4c1 [move] {os.path.basename(p)} -> {safe_tag}/")',
 '    def _reconcile_tags(self, say):',
 "        def _n(s): return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')",
 '        known = {_n(t): t for t in TAG_NAMES}',
 '        for dp, dn, fn in os.walk(self.root):',
 '            dn[:] = [x for x in dn if not x.startswith(".")]',
 '            for f in fn:',
 '                if not f.lower().endswith(".pdf"): continue',
 '                fp = os.path.join(dp, f)',
 '                T = get_tags(fp)',
 '                tag = None',
 '                for t in T:',
 '                    if _n(t) in known: tag = known[_n(t)]; break',
 '                if not tag: continue',
 '                tgt = os.path.join(self.position_folder_for(fp), tag)',
 '                if os.path.abspath(os.path.dirname(fp)) == os.path.abspath(tgt): continue',
 '                os.makedirs(tgt, exist_ok=True)',
 '                dst = os.path.join(tgt, f)',
 '                if os.path.exists(dst): continue',
 '                os.rename(fp, dst)',
 "                with self.lock: self.stats['moved'] += 1",
 '                say(f"\\U0001f4c1 [reconcile] {f} -> {tag}/")',
 '']
j = next(k for k, l in enumerate(L) if l.startswith('def main('))
L[j:j] = NEW_METHODS; done.append('class methods restored')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import butler, os
B = butler.Butler
for m in ("route", "_route", "handle_tags", "_reconcile_tags", "handle_pdf", "normalize_suffix"):
    print(m, "on class:", hasattr(B, m))
p = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location/Call Scheduled/Pradip Amte.pdf"
print("get_tags:", butler.get_tags(p) if os.path.exists(p) else "path moved")
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-400:])
