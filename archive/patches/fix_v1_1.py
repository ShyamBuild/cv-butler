import ast, re, subprocess
p = 'butler_v1.py'; L = open(p).read().split('\n')
tree = ast.parse('\n'.join(L))
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
in_cls = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
done = []

def find_block(pat):
    for i, l in enumerate(L):
        m = re.match(r'(\s*)def ' + pat + r'\(', l)
        if m:
            d = len(m.group(1)); j = i + 1
            while j < len(L):
                s = L[j]
                if s.strip() and (len(s) - len(s.lstrip())) <= d: break
                j += 1
            return i, j, d
    return None

# 1) lift route/_route into the class
lifted = []
for name in ('route', '_route'):
    if name in in_cls: continue
    b = find_block(name)
    if not b: done.append(name + ':NOT-FOUND'); continue
    i, j, d = b
    block = L[i:j]
    base = min(len(l) - len(l.lstrip()) for l in block if l.strip())
    lifted += ['    ' + l[base:] if l.strip() else '' for l in block] + ['']
    del L[i:j]
    done.append(name + ':lifted')
if lifted:
    k = next(idx for idx, l in enumerate(L) if l.startswith('def _selftest(') or l.startswith('def main('))
    L[k:k] = lifted

# 2) quote-regex get_tags (cannot miss quoted mdls values)
b = find_block('get_tags')
if b:
    i, j, d = b
    L[i:j] = [
     'def get_tags(path):',
     '    try:',
     "        r = subprocess.run(['mdls', '-name', 'kMDItemUserTags', path], capture_output=True, text=True, timeout=15)",
     "        out = (r.stdout or '').strip()",
     "        if not out or '(null)' in out: return []",
     '        raw = re.findall(r\'"([^"]*)"\', out)',
     '        if not raw:',
     "            raw = [x.strip().rstrip(',') for x in out.splitlines()[1:] if x.strip().rstrip(',') not in ('(', ')')]",
     '        tags = []',
     '        for item in raw:',
     '            nm = _unescape(item).split(chr(10))[0].strip()',
     '            if nm and nm not in COLOR_TAGS and nm not in tags: tags.append(nm)',
     '        return tags',
     '    except Exception:',
     '        return []',
     '']
    done.append('get_tags:quote-regex')

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)
r = subprocess.run(['cv_env/bin/python3', 'butler_v1.py', '--selftest',
                    '/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location'],
                   capture_output=True, text=True, cwd='.')
print(r.stdout.strip() or r.stderr.strip()[-500:])
