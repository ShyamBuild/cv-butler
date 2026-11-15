import ast, subprocess
p = 'butler.py'; src = open(p).read(); L = src.split('\n')
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
direct = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
MOVE = {'route', '_route'}
segs = []
def scan(nodes):
    for n in nodes:
        if isinstance(n, ast.FunctionDef):
            if n.name in MOVE and n not in cls.body:
                segs.append((n.lineno, n.end_lineno, n.name))
            scan(n.body)
        elif isinstance(n, (ast.For, ast.While, ast.If, ast.With)):
            scan(getattr(n, 'body', []) + getattr(n, 'orelse', []))
        elif isinstance(n, ast.Try):
            scan(n.body + n.handlers + n.orelse + n.finalbody)
scan(tree.body)
moved = []
for s, e, name in sorted(segs, reverse=True):
    block = L[s-1:e]
    base = min(len(l) - len(l.lstrip()) for l in block if l.strip())
    moved.insert(0, (name, ['    ' + l[base:] if l.strip() else '' for l in block]))
    del L[s-1:e]
# delete every module-level get_tags/_unescape (shadowing sources)
tree2 = ast.parse('\n'.join(L))
for n in sorted([n for n in tree2.body if isinstance(n, ast.FunctionDef) and n.name in ('get_tags', '_unescape')], key=lambda n: -n.lineno):
    del L[n.lineno-1:n.end_lineno]
# insert moved methods before main()
j = next(k for k, l in enumerate(L) if l.startswith('def main('))
for name, block in moved:
    L[j:j] = block + ['']
# canonical readers at EOF = guaranteed winning binding
L += ['',
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
 '    return []']
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅ moved:', [m[0] for m in moved])
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import butler, os
B = butler.Butler
for m in ("route", "_route", "handle_tags", "_reconcile_tags"):
    print(m, "on class:", hasattr(B, m))
p = "/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location/Call Scheduled/Pradip Amte.pdf"
print("get_tags:", butler.get_tags(p) if os.path.exists(p) else "path moved")
'''], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-400:])
